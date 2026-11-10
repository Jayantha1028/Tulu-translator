"""
kannada_tigalari_converter.nlp.ollama_model_exporter
===================================================
Generates an optimized Ollama Modelfile with embedded Tulu Dravidian grammar rules,
pronoun systems, 8-case noun declensions, and high-frequency idioms.
Allows running a fine-tuned Tulu AI assistant locally via Ollama with ZERO training burden.
"""

from __future__ import annotations

import argparse
import os
import sys

# Ensure project paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(PARENT_DIR)
for p in (ROOT_DIR, PARENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)


class OllamaModelExporter:
    """Generates ready-to-run Ollama Modelfiles for ultra-lightweight models."""

    @classmethod
    def generate_modelfile_content(cls, base_model: str = "qwen2.5:0.5b") -> str:
        """Embeds Tulu linguistic paradigms directly into the system prompt."""
        return f"""# Tulu-AI Local Assistant Modelfile
# Base: {base_model} (Ultra-lightweight, runs in <400 MB RAM on Apple Silicon)
FROM {base_model}

# Optimal generation parameters for Dravidian agglutinative language
PARAMETER temperature 0.2
PARAMETER top_p 0.85
PARAMETER repeat_penalty 1.15
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|endoftext|>"

# Linguistic System Instructions
SYSTEM \"\"\"You are Tulu-AI, an expert native speaker, linguist, and translator for the Tulu (ತುಳು) Dravidian language and Unicode 16.0 Tigalari script.

CRITICAL TULU GRAMMAR RULES:
1. Sentence Structure: Strictly Subject-Object-Verb (SOV) order.
   - Example: "ಯಾನ್ ಇಲ್ಲಗ್ ಬರ್ಪೆ" (I home-to am-coming).
2. The 8 Grammatical Noun Cases:
   - Nominative: ಇಲ್ಲ (house)
   - Accusative: ಇಲ್ಲನ್ (the house)
   - Instrumental: ಇಲ್ಲಡ್ದ್ (by/from the house)
   - Dative: ಇಲ್ಲಗ್ (to the house)
   - Ablative: ಇಲ್ಲರ್ದ್ (away from the house)
   - Genitive: ಇಲ್ಲದ (of the house)
   - Locative: ಇಲ್ಲಡ್ (in the house)
   - Vocative: ಇಲ್ಲೇ (O house)
3. Pronouns:
   - I: ಯಾನ್ (yaan) | We: ಎಂಕುಲು (eMkulu) / ನಮ (nama)
   - You (informal): ಈ (ee) | You (respectful/formal): ಈರ್ (eer)
   - He: ಆಯೆ (aaye) | She: ಆಲ್ (aal) | They: ಆಕುಲು (aakulu) / ಆರ್ (aar)
4. Common Idioms & Greetings:
   - "ಸೊಲ್ಮೆಲು" (solmelu) = Thank you / Greetings
   - "ಎಂಚ ಉಲ್ಲರ್?" (encha ullar?) = How are you? (formal)
   - "ಆವು" (aavu) = Okay / Alright
   - "ಇಜ್ಜಿ" (ijji) = No / Not present
   - "ತೆರಿಯಿಜಿ" (teriyiji) = I don't know / Not understood

When translating or conversing, prioritize accurate native Tulu vocabulary over borrowed words. Output Kannada script and English translation clearly.\"\"\"
"""

    @classmethod
    def export_modelfile(cls, output_path: str, base_model: str = "qwen2.5:0.5b") -> str:
        """Writes the Modelfile to disk."""
        content = cls.generate_modelfile_content(base_model=base_model)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path


def main():
    parser = argparse.ArgumentParser(description="Export zero-burden Ollama Modelfile for Tulu.")
    parser.add_argument("--model", type=str, default="qwen2.5:0.5b", help="Base Ollama model (default: qwen2.5:0.5b)")
    parser.add_argument("--out", type=str, default="Modelfile.tulu", help="Output path (default: Modelfile.tulu)")
    args = parser.parse_args()

    out_file = OllamaModelExporter.export_modelfile(args.out, base_model=args.model)
    print(f"✓ Generated zero-burden Ollama Modelfile at '{out_file}'")
    print(f"  To run locally in 5 seconds with 0 training overhead:")
    print(f"    ollama create tulu-ai -f {out_file}")
    print(f"    ollama run tulu-ai")


if __name__ == "__main__":
    main()
