import unittest
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import shutil

from examai.pdf.processor import pdf_processor
from examai.pdf.search import VectorSearchManager
from examai.database import DatabaseManager

class TestPDF(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test index files
        self.test_dir = tempfile.mkdtemp()
        self.index_path = Path(self.test_dir) / "test_faiss.index"
        
        # Setup temporary SQLite database
        self.db = DatabaseManager()
        self.db.is_sqlite = True
        
        import sqlite3
        def mock_conn():
            conn = sqlite3.connect(":memory:")
            conn.row_factory = sqlite3.Row
            return conn, True
        self.db.get_connection = mock_conn
        self.db.init_db()

    def tearDown(self):
        # Remove temporary directories
        shutil.rmtree(self.test_dir)

    def test_pdf_chunking_logic(self):
        """Test text division with sliding overlap and word-boundaries preservation."""
        page_text = "This is a simple text that we want to chunk for testing the word boundaries split."
        # Use small chunk size (e.g. 50 characters including prefix) to force division
        chunks = pdf_processor.chunk_page_text(
            text=page_text,
            page_num=1,
            doc_name="test.pdf",
            chunk_size=70,
            overlap=10
        )
        
        self.assertTrue(len(chunks) > 0)
        # Ensure metadata prefix was prepended
        self.assertTrue(chunks[0].startswith("[Document: test.pdf, Page: 1]"))
        # Ensure it contains part of text
        self.assertIn("This is a simple", chunks[0])

    @patch("examai.pdf.search.db")
    @patch("examai.pdf.search.INDEX_PATH")
    @patch("examai.pdf.embeddings.embeddings_generator.generate_embeddings")
    def test_vector_search_integration(self, mock_embed, mock_index_path, mock_db):
        """Test embedding addition to FAISS and query search matching."""
        # Setup mocks
        mock_index_path.__str__.return_value = str(self.index_path)
        
        # 3 chunks
        chunks = ["Database normal forms reduce redundancy", "CPU scheduler allocates CPU time", "TCP is a connection oriented protocol"]
        
        # Mock embeddings generator to return 3 distinct vectors (dimension 384)
        mock_vectors = np.random.rand(3, 384).astype(np.float32)
        mock_embed.side_effect = lambda texts: mock_vectors[:len(texts)]
        
        # Mock DB queries
        # mock_db.execute_write returns sequential mock IDs
        ids = [101, 102, 103]
        mock_db.execute_write.side_effect = ids
        
        # mock_db.execute_query returns the text mapping
        mock_db.execute_query.side_effect = [
            [], # check existing check
            [
                {"id": 101, "chunk_text": chunks[0]},
                {"id": 102, "chunk_text": chunks[1]},
                {"id": 103, "chunk_text": chunks[2]}
            ] # matching search retrieval
        ]
        
        # Run Indexing
        manager = VectorSearchManager()
        # Patch pdf processor output
        with patch("examai.pdf.processor.pdf_processor.process_pdf", return_value=chunks):
            indexed_count = manager.index_pdf("mock.pdf")
            self.assertEqual(indexed_count, 3)
            
        # Verify FAISS holds 3 vectors
        self.assertEqual(manager.index.ntotal, 3)
        
        # Run Search Query
        # Search query encodes 1 query vector
        mock_embed.side_effect = lambda texts: np.random.rand(1, 384).astype(np.float32)
        
        results = manager.search("normal forms", k=2)
        self.assertTrue(len(results) > 0)
        self.assertIn(results[0], chunks)
