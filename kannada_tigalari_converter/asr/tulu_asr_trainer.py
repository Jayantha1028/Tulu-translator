"""
Tulu Speech-to-Text (ASR) LoRA Fine-Tuning Engine
=================================================
Trains low-rank adaptation (LoRA) matrices on OpenAI Whisper decoder layers
using paired Tulu acoustic speech samples on Apple Silicon MPS / CUDA / CPU.

Key Architectural Components:
1. Paired Dataset Generator & Loader (audio .wav <-> Tulu text in Kannada orthography)
2. Whisper PEFT/LoRA Adapter Injection (r=16, alpha=32 on q_proj & v_proj)
3. Speech Seq2Seq Data Collator with Padding
4. Native PyTorch MPS-accelerated Training Loop with Gradient Clipping
5. Evaluation with Word Error Rate (WER) and Character Error Rate (CER) via jiwer
6. Checkpoint Serializer to models/tulu_whisper_lora/
"""

import os
import sys
import time
import json
import math
import random
import numpy as np
from typing import List, Dict, Optional, Tuple, Any

# Ensure project imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(PARENT_DIR)
for p in (CURRENT_DIR, PARENT_DIR, ROOT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
except ImportError:
    torch = None

try:
    from transformers import (
        WhisperProcessor,
        WhisperForConditionalGeneration,
        get_linear_schedule_with_warmup,
    )
except ImportError:
    WhisperProcessor = None
    WhisperForConditionalGeneration = None

try:
    from peft import LoraConfig, get_peft_model, PeftModel
except ImportError:
    LoraConfig = None
    get_peft_model = None

try:
    import jiwer
except ImportError:
    jiwer = None

from kannada_tigalari_converter.asr.tulu_audio_pipeline import (
    AudioPreprocessor,
    SyntheticTuluAudioGenerator,
)


class TuluSpeechDataset(Dataset):
    """
    In-memory PyTorch Dataset for paired Tulu audio features and tokenized labels.
    """

    def __init__(
        self,
        samples: List[Dict[str, str]],
        processor: Any,
        cache_dir: Optional[str] = None,
    ):
        """
        :param samples: List of dicts with keys 'audio_path' and 'text_kannada'.
        :param processor: Hugging Face WhisperProcessor.
        :param cache_dir: Directory where generated WAV files reside.
        """
        self.samples = samples
        self.processor = processor
        self.cache_dir = cache_dir or os.path.join(ROOT_DIR, "datasets", "paired_speech_data")
        os.makedirs(self.cache_dir, exist_ok=True)

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        item = self.samples[idx]
        audio_path = item["audio_path"]
        text = item["text_kannada"]

        # If audio does not exist, synthesize it on-the-fly
        if not os.path.isfile(audio_path):
            SyntheticTuluAudioGenerator.synthesize_to_wav(text, audio_path)

        # Load 16kHz audio array
        audio = AudioPreprocessor.load_audio(audio_path)

        # Extract 80-channel log-Mel spectrogram features (Whisper standard)
        input_features = self.processor.feature_extractor(
            audio,
            sampling_rate=16000,
            return_tensors="pt"
        ).input_features[0]

        # Tokenize target Kannada transcription labels
        labels = self.processor.tokenizer(text).input_ids

        return {
            "input_features": input_features,
            "labels": torch.tensor(labels, dtype=torch.long),
        }


def speech_collate_fn(batch: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
    """
    Pads variable-length label sequences with -100 for PyTorch CrossEntropyLoss masking.
    """
    input_features = torch.stack([item["input_features"] for item in batch])
    raw_labels = [item["labels"] for item in batch]

    max_len = max(len(l) for l in raw_labels)
    padded_labels = []
    for l in raw_labels:
        pad_size = max_len - len(l)
        if pad_size > 0:
            padded = torch.cat([l, torch.full((pad_size,), -100, dtype=torch.long)])
        else:
            padded = l
        padded_labels.append(padded)

    labels = torch.stack(padded_labels)
    return {
        "input_features": input_features,
        "labels": labels,
    }


class TuluASRTrainer:
    """
    LoRA Fine-Tuning Trainer for Tulu Speech-to-Text.
    """

    def __init__(
        self,
        model_name: str = "openai/whisper-tiny",
        output_dir: Optional[str] = None,
        device: Optional[str] = None,
        lora_r: int = 16,
        lora_alpha: int = 32,
        lora_dropout: float = 0.05,
        low_power: bool = True,
    ):
        self.model_name = model_name
        self.output_dir = output_dir or os.path.join(ROOT_DIR, "models", "tulu_whisper_lora")
        self.device = self._select_device(device)
        self.lora_r = lora_r
        self.lora_alpha = lora_alpha
        self.lora_dropout = lora_dropout
        self.low_power = low_power

        # In low-power mode, cap PyTorch CPU threads to 2 to minimize SoC heating
        if torch is not None and self.low_power:
            try:
                torch.set_num_threads(2)
            except Exception:
                pass

        self.processor = None
        self.model = None

    def _select_device(self, preferred: Optional[str]) -> str:
        if preferred:
            return preferred
        if torch is not None:
            if torch.backends.mps.is_available() and torch.backends.mps.is_built():
                return "mps"
            if torch.cuda.is_available():
                return "cuda"
        return "cpu"

    def setup_model(self):
        """Loads Whisper, freezes base parameters, and injects LoRA adapters."""
        if torch is None or WhisperProcessor is None or LoraConfig is None:
            raise RuntimeError("Required training packages (torch, transformers, peft) not installed.")

        print(f"[Tulu Trainer] Loading base model '{self.model_name}' on device '{self.device}'...")
        self.processor = WhisperProcessor.from_pretrained(self.model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(self.model_name)

        # Freeze encoder and base decoder
        for param in self.model.parameters():
            param.requires_grad = False

        # Configure LoRA on attention query and value projection matrices
        peft_config = LoraConfig(
            r=self.lora_r,
            lora_alpha=self.lora_alpha,
            target_modules=["q_proj", "v_proj"],
            lora_dropout=self.lora_dropout,
            bias="none",
        )
        self.model = get_peft_model(self.model, peft_config)
        self.model.to(self.device)
        self.model.print_trainable_parameters()

    def prepare_dataset(
        self,
        num_samples: int = 100,
        val_split: float = 0.1,
    ) -> Tuple[TuluSpeechDataset, TuluSpeechDataset]:
        """
        Gathers sentences from corpus and creates training and validation sets.
        """
        from kannada_tigalari_converter.lexicon.words_dataset_1000 import WORDS_DATASET_1000

        audio_cache_dir = os.path.join(ROOT_DIR, "datasets", "paired_speech_data")
        os.makedirs(audio_cache_dir, exist_ok=True)

        samples = []
        # 1. Use curated vocabulary and phrases first
        for idx, item in enumerate(WORDS_DATASET_1000):
            if len(samples) >= num_samples:
                break
            kn = item["kannada"].strip()
            if not kn:
                continue
            wav_name = f"sample_{idx:05d}.wav"
            wav_path = os.path.join(audio_cache_dir, wav_name)
            samples.append({
                "id": str(idx),
                "text_kannada": kn,
                "audio_path": wav_path,
            })

        # 2. Add from master corpus if more samples requested
        if len(samples) < num_samples:
            master_csv = os.path.join(ROOT_DIR, "datasets", "tulu_master_consolidated_corpus.csv")
            if os.path.isfile(master_csv):
                import csv
                with open(master_csv, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for idx, row in enumerate(reader, start=len(samples)):
                        if len(samples) >= num_samples:
                            break
                        kn = (row.get("tulu_kannada") or row.get("kannada") or "").strip()
                        if 3 <= len(kn) <= 60:
                            wav_name = f"master_{idx:05d}.wav"
                            wav_path = os.path.join(audio_cache_dir, wav_name)
                            samples.append({
                                "id": str(idx),
                                "text_kannada": kn,
                                "audio_path": wav_path,
                            })

        print(f"[Tulu Trainer] Prepared {len(samples)} paired speech samples.")

        # Parallel pre-synthesis of missing audio samples
        missing = [s for s in samples if not os.path.isfile(s["audio_path"])]
        if missing:
            workers = 2 if getattr(self, "low_power", False) else 4
            print(f"[Tulu Trainer] Synthesizing {len(missing)} missing audio samples ({workers} workers, thermal-optimized)...")
            from concurrent.futures import ThreadPoolExecutor
            def _synth(item):
                rate = random.choice([150, 175, 205])
                SyntheticTuluAudioGenerator.synthesize_to_wav(item["text_kannada"], item["audio_path"], rate=rate)

            with ThreadPoolExecutor(max_workers=workers) as pool:
                list(pool.map(_synth, missing))
            print(f"[Tulu Trainer] Audio pre-synthesis complete ({len(samples)} total audio clips ready).")

        random.seed(42)
        random.shuffle(samples)

        split_idx = max(1, int(len(samples) * (1.0 - val_split)))
        train_samples = samples[:split_idx]
        val_samples = samples[split_idx:] if split_idx < len(samples) else samples[:max(1, len(samples) // 5)]

        train_ds = TuluSpeechDataset(train_samples, self.processor, cache_dir=audio_cache_dir)
        val_ds = TuluSpeechDataset(val_samples, self.processor, cache_dir=audio_cache_dir)
        return train_ds, val_ds

    def train(
        self,
        num_samples: int = 100,
        epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 1e-3,
        weight_decay: float = 0.01,
    ) -> Dict[str, Any]:
        """
        Executes the LoRA fine-tuning training loop.
        """
        self.setup_model()
        train_ds, val_ds = self.prepare_dataset(num_samples=num_samples)

        train_loader = DataLoader(
            train_ds,
            batch_size=batch_size,
            shuffle=True,
            collate_fn=speech_collate_fn,
        )
        val_loader = DataLoader(
            val_ds,
            batch_size=batch_size,
            shuffle=False,
            collate_fn=speech_collate_fn,
        )

        optimizer = torch.optim.AdamW(
            [p for p in self.model.parameters() if p.requires_grad],
            lr=learning_rate,
            weight_decay=weight_decay,
        )

        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=max(1, int(total_steps * 0.1)),
            num_training_steps=total_steps,
        )

        print(f"\n[Tulu Trainer] Starting training on {self.device.upper()}...")
        print(f"  Epochs       : {epochs}")
        print(f"  Batch Size   : {batch_size}")
        print(f"  Total Steps  : {total_steps}")
        print(f"  Learning Rate: {learning_rate}")
        print("=" * 60)

        history = {"train_loss": [], "val_loss": [], "epoch_times": []}
        start_time = time.time()

        for epoch in range(1, epochs + 1):
            t_epoch_start = time.time()
            self.model.train()
            total_train_loss = 0.0

            for step, batch in enumerate(train_loader, start=1):
                input_features = batch["input_features"].to(self.device)
                labels = batch["labels"].to(self.device)

                optimizer.zero_grad()
                outputs = self.model(input_features=input_features, labels=labels)
                loss = outputs.loss

                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    [p for p in self.model.parameters() if p.requires_grad],
                    max_norm=1.0
                )
                optimizer.step()
                scheduler.step()

                total_train_loss += loss.item()
                if step % max(1, len(train_loader) // 3) == 0 or step == len(train_loader):
                    print(f"  Epoch {epoch}/{epochs} | Step {step}/{len(train_loader)} | Batch Loss: {loss.item():.4f}")

            avg_train_loss = total_train_loss / len(train_loader)
            history["train_loss"].append(avg_train_loss)

            # Validation
            self.model.eval()
            total_val_loss = 0.0
            with torch.no_grad():
                for v_batch in val_loader:
                    v_inputs = v_batch["input_features"].to(self.device)
                    v_labels = v_batch["labels"].to(self.device)
                    v_out = self.model(input_features=v_inputs, labels=v_labels)
                    total_val_loss += v_out.loss.item()

            avg_val_loss = total_val_loss / max(1, len(val_loader))
            history["val_loss"].append(avg_val_loss)

            epoch_dur = time.time() - t_epoch_start
            history["epoch_times"].append(epoch_dur)
            print(f"--> Epoch {epoch} Done in {epoch_dur:.1f}s | Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f}\n")

            # Thermal management: free Metal GPU cache and pause briefly if low-power mode is enabled
            if self.device == "mps" and hasattr(torch, "mps"):
                torch.mps.empty_cache()
            if self.low_power:
                time.sleep(1.0)

        total_duration = time.time() - start_time
        print(f"[Tulu Trainer] Training loop completed in {total_duration:.1f}s.")

        # Compute final evaluation metrics (WER & CER)
        print("[Tulu Trainer] Running validation evaluation (WER & CER)...")
        eval_metrics = self.evaluate_metrics(val_loader)
        history["eval_metrics"] = eval_metrics
        print(f"  Character Error Rate (CER): {eval_metrics['cer'] * 100:.1f}%")
        print(f"  Word Error Rate (WER)     : {eval_metrics['wer'] * 100:.1f}%")
        if eval_metrics.get("sample_pred"):
            print("\n  Sample Decoded Predictions:")
            for p, r in zip(eval_metrics["sample_pred"][:2], eval_metrics["sample_ref"][:2]):
                print(f"    Target    : {r}")
                print(f"    Recognized: {p}")

        # Save LoRA adapter weights
        self.save_adapter(history)
        return {
            "success": True,
            "epochs": epochs,
            "train_loss": history["train_loss"],
            "val_loss": history["val_loss"],
            "wer": eval_metrics["wer"],
            "cer": eval_metrics["cer"],
            "output_dir": self.output_dir,
            "duration_sec": total_duration,
        }

    def evaluate_metrics(self, val_loader: DataLoader) -> Dict[str, Any]:
        """Evaluates WER and CER on the validation set."""
        self.model.eval()
        predictions = []
        references = []

        with torch.no_grad():
            for batch in val_loader:
                input_features = batch["input_features"].to(self.device)
                labels = batch["labels"].to(self.device)

                # Generate transcriptions with greedy search
                predicted_ids = self.model.generate(
                    input_features,
                    max_new_tokens=128,
                )
                pred_texts = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)

                label_ids = labels.clone()
                label_ids[label_ids == -100] = self.processor.tokenizer.pad_token_id
                ref_texts = self.processor.batch_decode(label_ids, skip_special_tokens=True)

                predictions.extend([p.strip() for p in pred_texts])
                references.extend([r.strip() for r in ref_texts])

        wer = jiwer.wer(references, predictions) if jiwer and len(references) > 0 else 0.0
        cer = jiwer.cer(references, predictions) if jiwer and len(references) > 0 else 0.0
        return {
            "wer": round(float(wer), 4),
            "cer": round(float(cer), 4),
            "sample_pred": predictions[:3],
            "sample_ref": references[:3],
        }

    def save_adapter(self, history: Dict[str, Any]):
        """Serializes the PEFT adapter weights and metadata."""
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"[Tulu Trainer] Saving fine-tuned LoRA weights to: {self.output_dir}")
        self.model.save_pretrained(self.output_dir)
        self.processor.save_pretrained(self.output_dir)

        # Write training summary log
        summary_path = os.path.join(self.output_dir, "training_summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump({
                "base_model": self.model_name,
                "device": self.device,
                "lora_r": self.lora_r,
                "lora_alpha": self.lora_alpha,
                "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "history": history,
            }, f, indent=2)
        print(f"[Tulu Trainer] Adapter saved successfully!")


def train_tulu_asr(
    num_samples: int = 100,
    epochs: int = 3,
    batch_size: int = 4,
    learning_rate: float = 1e-3,
    output_dir: Optional[str] = None,
    low_power: bool = True,
) -> Dict[str, Any]:
    """Convenience functional interface for CLI and scripts."""
    trainer = TuluASRTrainer(output_dir=output_dir, low_power=low_power)
    return trainer.train(
        num_samples=num_samples,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fine-tune Whisper with LoRA for Tulu ASR on Apple Silicon M4 MPS.")
    parser.add_argument("--samples", type=int, default=50, help="Number of paired speech samples to synthesize/train (default: 50)")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs (default: 3)")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size per step (default: 4)")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate (default: 0.001)")
    parser.add_argument("--output", type=str, default=None, help="Output directory for saved LoRA adapter")
    parser.add_argument("--low-power", action="store_true", default=True, help="Limit threads and release GPU buffers to minimize heat (default: True)")
    args = parser.parse_args()

    train_tulu_asr(
        num_samples=args.samples,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        output_dir=args.output,
        low_power=args.low_power,
    )
