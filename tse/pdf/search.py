import faiss
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from tse.pdf.processor import pdf_processor
from tse.pdf.embeddings import embeddings_generator
from tse.database import db
from tse.utils.logger import logger

INDEX_PATH = Path.home() / ".tse" / "faiss.index"

class VectorSearchManager:
    def __init__(self):
        self._index = None
        self.dimension = 384  # Dimension of all-MiniLM-L6-v2

    @property
    def index(self) -> faiss.IndexIDMap:
        """Lazy loads the FAISS index from disk or creates a new one."""
        if self._index is None:
            if INDEX_PATH.exists():
                try:
                    logger.info("Loading existing FAISS index from disk...")
                    self._index = faiss.read_index(str(INDEX_PATH))
                except Exception as e:
                    logger.error(f"Error reading FAISS index: {e}. Rebuilding empty index.")
                    self._index = self._create_empty_index()
            else:
                self._index = self._create_empty_index()
        return self._index

    def _create_empty_index(self) -> faiss.IndexIDMap:
        """Creates a new empty IndexIDMap wrapping IndexFlatIP."""
        base_index = faiss.IndexFlatIP(self.dimension)
        return faiss.IndexIDMap(base_index)

    def save_index(self) -> None:
        """Saves the current FAISS index state to disk."""
        try:
            logger.info("Saving FAISS index to disk...")
            faiss.write_index(self.index, str(INDEX_PATH))
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")

    def index_pdf(self, pdf_path: str) -> int:
        """
        Processes PDF, chunks it, stores in Database, creates embeddings,
        adds to FAISS index, and saves the index. Returns count of chunks indexed.
        """
        doc_name = Path(pdf_path).name
        
        # Check if already exists in DB, if so, clean it up before indexing to avoid duplicates
        existing = db.execute_query(
            "SELECT id FROM document_chunks WHERE doc_name = %s", (doc_name,)
        )
        if existing:
            logger.info(f"Document {doc_name} is already indexed. Re-indexing...")
            existing_ids = [row["id"] for row in existing]
            # Remove from DB
            db.execute_write("DELETE FROM document_chunks WHERE doc_name = %s", (doc_name,))
            # Remove from FAISS index (FAISS supports removing by ID)
            # Remove ids from IndexIDMap requires converting to numpy array
            try:
                self.index.remove_ids(np.array(existing_ids, dtype=np.int64))
                self.save_index()
            except Exception as e:
                logger.warning(f"Could not remove old vector IDs from FAISS: {e}. Rebuilding index may be needed.")

        # Process text
        chunks = pdf_processor.process_pdf(pdf_path)
        if not chunks:
            logger.warning(f"No text extracted or chunked from {pdf_path}.")
            return 0
            
        logger.info(f"Generated {len(chunks)} chunks for {doc_name}. Generating embeddings...")
        
        # Generate embeddings
        embeddings = embeddings_generator.generate_embeddings(chunks)
        # Normalize for Inner Product (Cosine Similarity)
        faiss.normalize_L2(embeddings)
        
        # Insert chunks to database and collect primary keys
        db_ids = []
        for i, chunk_text in enumerate(chunks):
            db_id = db.execute_write(
                "INSERT INTO document_chunks (doc_name, chunk_index, chunk_text) VALUES (%s, %s, %s)",
                (doc_name, i, chunk_text)
            )
            db_ids.append(db_id)
            
        # Add to FAISS index
        ids_arr = np.array(db_ids, dtype=np.int64)
        self.index.add_with_ids(embeddings, ids_arr)
        
        # Save to disk
        self.save_index()
        logger.info(f"Successfully indexed document {doc_name} with {len(chunks)} vectors.")
        return len(chunks)

    def search(self, query: str, k: int = 5) -> List[str]:
        """
        Executes semantic search against the FAISS vector index.
        Returns a list of matching text chunks.
        """
        if self.index.ntotal == 0:
            logger.warning("FAISS index is empty. No documents indexed yet.")
            return []
            
        # Embed query
        query_vector = embeddings_generator.generate_embeddings([query])
        faiss.normalize_L2(query_vector)
        
        # Search index
        # k should not exceed total vectors in index
        k = min(k, self.index.ntotal)
        if k <= 0:
            return []
            
        distances, indices = self.index.search(query_vector, k)
        
        # Extract matching database IDs (indices[0] is array of match ids)
        matched_ids = [int(idx) for idx in indices[0] if idx != -1]
        if not matched_ids:
            return []
            
        # Query database for actual chunk texts in matching order
        # To maintain order of relevance from FAISS, query and sort in Python
        placeholders = ", ".join(["%s"] * len(matched_ids))
        query_sql = f"SELECT id, chunk_text FROM document_chunks WHERE id IN ({placeholders})"
        rows = db.execute_query(query_sql, tuple(matched_ids))
        
        # Create map for quick lookup
        text_map = {row["id"]: row["chunk_text"] for row in rows}
        
        # Re-assemble matching text in order of FAISS search results
        results = []
        for db_id in matched_ids:
            if db_id in text_map:
                results.append(text_map[db_id])
                
        return results

    def list_indexed_documents(self) -> List[str]:
        """Returns list of all unique documents indexed."""
        rows = db.execute_query("SELECT DISTINCT doc_name FROM document_chunks")
        return [row["doc_name"] for row in rows]

    def clear_index(self) -> None:
        """Deletes all chunks from database and wipes the FAISS index."""
        db.execute_write("DELETE FROM document_chunks")
        self._index = self._create_empty_index()
        self.save_index()
        logger.info("Cleared all PDF vector indexes and database chunks.")

# Singleton Search Manager
search_manager = VectorSearchManager()
