"""
Document Processor: PDF Extraction and Chunking

Handles PDF upload, text extraction, and intelligent chunking.
"""

import os
import pdfplumber
import re
from typing import List, Tuple, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Service for processing PDF documents.
    
    Features:
    - PDF text extraction
    - Page-aware chunking
    - Metadata preservation
    """
    
    def __init__(self, chunk_size: int = 300, min_chunk_words: int = 40):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Number of words per chunk
            min_chunk_words: Minimum words required for a valid chunk
        """
        self.chunk_size = chunk_size
        self.min_chunk_words = min_chunk_words
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF with page markers.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Extracted text with [Page N] markers
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        logger.info(f"Extracting text from: {pdf_path}")
        full_text = ""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"  Total pages: {total_pages}")
                
                for i, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        # Add page marker
                        full_text += f"[Page {i}]\n{page_text}\n\n"
                        logger.info(f"  Extracted page {i}/{total_pages}")
                    else:
                        logger.warning(f"  Page {i} has no extractable text")
            
            logger.info(f"✓ Extracted {len(full_text)} characters")
            return full_text
            
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            raise
    
    def chunk_text_with_pages(self, text: str) -> List[Tuple[str, int]]:
        """
        Split text into chunks while preserving page information.
        
        Args:
            text: Text with [Page N] markers
        
        Returns:
            List of (chunk_text, page_number) tuples
        """
        # Split by page markers
        page_sections = re.split(r'\[Page (\d+)\]', text)
        
        chunks_with_pages = []
        current_page = 1
        
        for i, section in enumerate(page_sections):
            if i == 0:
                # Content before first page marker
                if section.strip():
                    self._chunk_section(section.strip(), 1, chunks_with_pages)
                continue
            elif i % 2 == 1:
                # This is a page number
                current_page = int(section)
            else:
                # This is content for the current page
                if section.strip():
                    self._chunk_section(section.strip(), current_page, chunks_with_pages)
        
        logger.info(f"✓ Created {len(chunks_with_pages)} chunks")
        return chunks_with_pages
    
    def _chunk_section(self, text: str, page: int, results: List):
        """Helper to chunk a section of text."""
        words = text.split()
        
        for j in range(0, len(words), self.chunk_size):
            chunk_words = words[j:j + self.chunk_size]
            
            if len(chunk_words) >= self.min_chunk_words:
                chunk_text = " ".join(chunk_words)
                # Clean up the text
                chunk_text = self._clean_text(chunk_text)
                results.append((chunk_text, page))
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove page markers that might have slipped through
        text = re.sub(r'\[Page \d+\]', '', text)
        # Strip
        text = text.strip()
        return text
    
    def process_pdf_to_chunks(
        self,
        pdf_path: str,
        source_name: str = None
    ) -> List[Dict]:
        """
        Complete pipeline: PDF → chunks with metadata.
        
        Args:
            pdf_path: Path to PDF
            source_name: Display name for source (optional)
        
        Returns:
            List of chunk dictionaries
        """
        if source_name is None:
            source_name = os.path.basename(pdf_path)
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        
        # Chunk with page info
        chunks_with_pages = self.chunk_text_with_pages(text)
        
        # Build chunk dictionaries
        chunk_dicts = []
        for i, (chunk_text, page) in enumerate(chunks_with_pages, 1):
            chunk_dicts.append({
                "id": i,  # Will be reassigned when added to KB
                "text": chunk_text,
                "source": source_name,
                "page": page
            })
        
        logger.info(f"✓ Processed {source_name}: {len(chunk_dicts)} chunks")
        return chunk_dicts
    
    def validate_pdf(self, file_path: str, max_size_mb: int = 50) -> Tuple[bool, str]:
        """
        Validate PDF file.
        
        Args:
            file_path: Path to file
            max_size_mb: Maximum size in MB
        
        Returns:
            (is_valid, error_message)
        """
        # Check existence
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        # Check size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return False, f"File too large: {file_size_mb:.1f}MB (max: {max_size_mb}MB)"
        
        # Check if it's a valid PDF
        try:
            with pdfplumber.open(file_path) as pdf:
                if len(pdf.pages) == 0:
                    return False, "PDF has no pages"
        except Exception as e:
            return False, f"Invalid PDF: {str(e)}"
        
        return True, "OK"


# Example usage
if __name__ == "__main__":
    processor = DocumentProcessor(chunk_size=250)
    
    # Test with a sample PDF
    pdf_path = "test.pdf"
    
    if os.path.exists(pdf_path):
        # Validate
        is_valid, msg = processor.validate_pdf(pdf_path)
        print(f"Validation: {msg}")
        
        if is_valid:
            # Process
            chunks = processor.process_pdf_to_chunks(pdf_path)
            print(f"\nProcessed {len(chunks)} chunks:")
            for chunk in chunks[:3]:
                print(f"  - Page {chunk['page']}: {chunk['text'][:60]}...")
    else:
        print(f"Test PDF not found: {pdf_path}")
