import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any
from tse.utils.logger import logger

class PDFProcessor:
    def __init__(self):
        pass

    def extract_pages(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text page by page from a PDF.
        Returns a list of dicts: [{'page_num': int, 'text': str}]
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found at {pdf_path}")

        logger.info(f"Extracting text from PDF: {path.name}")
        pages = []
        try:
            doc = fitz.open(str(path))
            for i, page in enumerate(doc):
                text = page.get_text()
                # Clean up whitespace and newlines
                text_clean = " ".join(text.split())
                if text_clean:
                    pages.append({
                        "page_num": i + 1,
                        "text": text_clean
                    })
            doc.close()
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
            raise RuntimeError(f"Could not parse PDF: {e}")
            
        logger.info(f"Successfully extracted {len(pages)} pages from {path.name}")
        return pages

    def chunk_page_text(self, text: str, page_num: int, doc_name: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Splits text of a single page into chunks of roughly chunk_size characters,
        preserving word boundaries and prepending document metadata.
        """
        words = text.split()
        chunks = []
        current_words = []
        current_len = 0
        
        metadata_prefix = f"[Document: {doc_name}, Page: {page_num}] "
        # Adjust chunk size limit to account for metadata prefix length
        adjusted_limit = chunk_size - len(metadata_prefix)
        
        for word in words:
            current_words.append(word)
            current_len += len(word) + 1
            if current_len >= adjusted_limit:
                chunk_str = metadata_prefix + " ".join(current_words)
                chunks.append(chunk_str)
                
                # Setup overlap
                overlap_ratio = overlap / chunk_size
                overlap_count = int(len(current_words) * overlap_ratio)
                current_words = current_words[-overlap_count:] if overlap_count > 0 else []
                current_len = sum(len(w) + 1 for w in current_words)
                
        if current_words:
            chunk_str = metadata_prefix + " ".join(current_words)
            chunks.append(chunk_str)
            
        return chunks

    def process_pdf(self, pdf_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Runs the full pipeline of extracting pages and splitting them into chunks.
        """
        doc_name = Path(pdf_path).name
        pages = self.extract_pages(pdf_path)
        all_chunks = []
        
        for page in pages:
            page_chunks = self.chunk_page_text(
                text=page["text"],
                page_num=page["page_num"],
                doc_name=doc_name,
                chunk_size=chunk_size,
                overlap=overlap
            )
            all_chunks.extend(page_chunks)
            
        return all_chunks

pdf_processor = PDFProcessor()
