import unittest
from unittest.mock import patch
from tse.ai.engine import prompt_engine

class TestAI(unittest.TestCase):
    @patch("tse.ai.client.ai_client.generate_completion")
    def test_exam_answer_generation(self, mock_generate):
        """Test prompt compiling and output formatting for standard questions."""
        mock_generate.return_value = (
            "## Definition\nNormalization simplifies DBs.\n## Explanation\nSplitting relations.", 
            "openrouter", 
            "google/gemini-2.5-flash"
        )
        
        result = prompt_engine.generate_exam_answer(
            question="What is normalization?",
            subject="DBMS",
            mode="theory",
            marks=5
        )
        
        self.assertIn("Normalization simplifies DBs.", result["answer"])
        self.assertEqual(result["provider"], "openrouter")
        self.assertEqual(result["model"], "google/gemini-2.5-flash")
        
        # Verify that mock was called
        mock_generate.assert_called_once()

    @patch("tse.ai.client.ai_client.generate_completion")
    def test_rag_answer_generation(self, mock_generate):
        """Test that PDF context is successfully injected into prompt."""
        mock_generate.return_value = ("Answer from PDF context.", "openrouter", "google/gemini-2.5-flash")
        
        result = prompt_engine.generate_exam_answer(
            question="What is ACID?",
            subject="DBMS",
            mode="theory",
            marks=5,
            context="ACID stands for Atomicity, Consistency, Isolation, Durability."
        )
        
        # Verify the context was passed to generate_completion in messages
        args, kwargs = mock_generate.call_args
        messages = kwargs.get("messages") or args[0]
        
        system_msg = next(msg["content"] for msg in messages if msg["role"] == "system")
        self.assertIn("=== PDF DOCUMENT CONTEXT ===", system_msg)
        self.assertIn("ACID stands for Atomicity, Consistency, Isolation, Durability.", system_msg)

    @patch("tse.ai.client.ai_client.generate_completion")
    def test_quiz_generation(self, mock_generate):
        """Test generating JSON structured quiz questions."""
        mock_json = '[{"question": "Q1", "option_a": "A", "option_b": "B", "option_c": "C", "option_d": "D", "correct_option": "A", "explanation": "Exp"}]'
        mock_generate.return_value = (f"```json\n{mock_json}\n```", "openrouter", "google/gemini-2.5-flash")
        
        res = prompt_engine.generate_quiz("DBMS")
        self.assertEqual(res, mock_json)
