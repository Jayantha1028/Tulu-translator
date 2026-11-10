"""
Unit Tests for Zero-Burden LLM Preparation Utilities:
- Stream Dataset Builder
- Unicode 16.0 Tokenizer Tool
- Memory-Safe LLM Trainer (Dry-Run)
- Ollama Modelfile Exporter
"""

import json
import os
import unittest

from kannada_tigalari_converter.nlp.tulu_dataset_builder import TuluDatasetBuilder
from kannada_tigalari_converter.nlp.tulu_tokenizer_tool import TuluTokenizerTool
from kannada_tigalari_converter.nlp.tulu_llm_trainer import TuluLLMTrainer
from kannada_tigalari_converter.nlp.ollama_model_exporter import OllamaModelExporter


class TestLLMPreparation(unittest.TestCase):
    def test_dataset_builder_streaming(self):
        builder = TuluDatasetBuilder()
        records = list(builder.build_instruction_records(max_records=10))
        self.assertGreater(len(records), 0)
        self.assertLessEqual(len(records), 10)

        first = records[0]
        self.assertIn("instruction", first)
        self.assertIn("output", first)
        self.assertIn("task", first)

    def test_tokenizer_tool_tokens(self):
        tokens = TuluTokenizerTool.get_full_tulu_token_list()
        self.assertGreater(len(tokens), 50)
        # Check Tigalari codepoints present
        self.assertTrue(any(len(c) == 1 and 0x11380 <= ord(c) <= 0x113FF for c in tokens))

        test_out = "/tmp/test_tokens.json"
        path = TuluTokenizerTool.export_token_catalog(test_out)
        self.assertTrue(os.path.exists(path))
        if os.path.exists(test_out):
            os.remove(test_out)

    def test_trainer_dry_run(self):
        trainer = TuluLLMTrainer()
        res = trainer.run_dry_run("datasets/tulu_lora_sft_dataset.jsonl")
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["memory_safe"])
        self.assertGreater(res["records_tested"], 0)

    def test_ollama_modelfile_generation(self):
        content = OllamaModelExporter.generate_modelfile_content(base_model="qwen2.5:0.5b")
        self.assertIn("FROM qwen2.5:0.5b", content)
        self.assertIn("ಯಾನ್ ಇಲ್ಲಗ್ ಬರ್ಪೆ", content)
        self.assertIn("CRITICAL TULU GRAMMAR RULES", content)


if __name__ == "__main__":
    unittest.main()
