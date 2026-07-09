import unittest
import os
import tempfile
import shutil
from pathlib import Path

from tse.formatter.text import parse_markdown_sections
from tse.formatter.export import export_markdown, export_text, export_word, export_pdf

class TestFormatter(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_markdown_section_parsing(self):
        """Test separating markdown text into header divisions."""
        md_text = (
            "# Main Topic\n"
            "Intro text.\n\n"
            "## Definition\n"
            "This is the definition text.\n\n"
            "## Explanation\n"
            "This is the explanation text."
        )
        
        sections = parse_markdown_sections(md_text)
        self.assertIn("Definition", sections)
        self.assertIn("Explanation", sections)
        self.assertEqual(sections["Definition"], "This is the definition text.")
        self.assertEqual(sections["Explanation"], "This is the explanation text.")

    def test_exporters(self):
        """Test exporting content to TXT, MD, DOCX, and PDF formats."""
        content = (
            "## Definition\n"
            "Core concept summary.\n\n"
            "## Explanation\n"
            "Full explanation paragraphs."
        )
        
        md_path = Path(self.test_dir) / "test.md"
        txt_path = Path(self.test_dir) / "test.txt"
        docx_path = Path(self.test_dir) / "test.docx"
        pdf_path = Path(self.test_dir) / "test.pdf"
        
        # 1. Export Markdown
        export_markdown(content, str(md_path))
        self.assertTrue(md_path.exists())
        with open(md_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), content)
            
        # 2. Export Text
        export_text(content, str(txt_path))
        self.assertTrue(txt_path.exists())
        with open(txt_path, "r", encoding="utf-8") as f:
            plain = f.read()
            self.assertNotIn("##", plain)
            self.assertIn("Core concept summary", plain)
            
        # 3. Export Word (python-docx)
        export_word(content, str(docx_path), title="Test Question")
        self.assertTrue(docx_path.exists())
        self.assertTrue(docx_path.stat().st_size > 0)
        
        # 4. Export PDF (fpdf2)
        export_pdf(content, str(pdf_path), title="Test Question")
        self.assertTrue(pdf_path.exists())
        self.assertTrue(pdf_path.stat().st_size > 0)
