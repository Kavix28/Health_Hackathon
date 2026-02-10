"""
Retrieval Service: Semantic Search for RAG

Handles document retrieval using sentence transformers.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetrievalService:
    """
    Service for semantic search and document retrieval.
    
    Uses sentence transformers to find relevant document chunks
    based on semantic similarity.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize retrieval service.
        
        Args:
            model_name: Sentence transformer model to use
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.embedder = SentenceTransformer(model_name)
        logger.info("✓ Embedding model loaded")
    
    def retrieve_relevant_chunks(
        self,
        query: str,
        kb_docs: List[Dict],
        kb_embeddings: np.ndarray,
        top_k: int = 5,
        min_score: float = 0.25
    ) -> List[Dict]:
        """
        Retrieve top-K most relevant chunks for a query.
        
        Args:
            query: User's question
            kb_docs: List of knowledge base documents
            kb_embeddings: Pre-computed embeddings matrix
            top_k: Number of chunks to retrieve
            min_score: Minimum similarity score (0-1)
        
        Returns:
            List of relevant chunks with scores
        """
        if not kb_docs or kb_embeddings is None:
            logger.warning("Knowledge base is empty")
            return []
        
        # Embed the query
        query_embedding = self.embedder.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )[0]
        
        # Calculate similarity scores
        scores = np.dot(kb_embeddings, query_embedding)
        
        # Get top-K indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        # Build result list
        results = []
        for idx in top_indices:
            score = float(scores[idx])
            
            # Filter by minimum score
            if score < min_score:
                continue
            
            chunk = kb_docs[idx].copy()
            chunk['score'] = score
            chunk['relevance'] = self._score_to_relevance(score)
            results.append(chunk)
        
        logger.info(f"Retrieved {len(results)} chunks (scores: {[f'{r['score']:.2f}' for r in results]})")
        
        return results
    
    def _score_to_relevance(self, score: float) -> str:
        """Convert similarity score to human-readable relevance."""
        if score >= 0.7:
            return "High"
        elif score >= 0.5:
            return "Medium"
        elif score >= 0.3:
            return "Low"
        else:
            return "Very Low"
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 100) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            batch_size: Process in batches for memory efficiency
        
        Returns:
            Numpy array of embeddings
        """
        if not texts:
            return None
        
        logger.info(f"Generating embeddings for {len(texts)} texts...")
        
        if len(texts) > batch_size:
            # Process in batches
            all_embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = self.embedder.encode(
                    batch,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    show_progress_bar=False
                )
                all_embeddings.append(batch_embeddings)
                logger.info(f"  Processed {min(i + batch_size, len(texts))}/{len(texts)}")
            
            embeddings = np.vstack(all_embeddings)
        else:
            # Process all at once
            embeddings = self.embedder.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )
        
        logger.info(f"✓ Generated {embeddings.shape[0]} embeddings")
        return embeddings
    
    def calculate_relevance_score(
        self,
        query: str,
        chunks: List[Dict]
    ) -> float:
        """
        Calculate overall relevance score for a set of chunks.
        
        Args:
            query: The query
            chunks: Retrieved chunks with scores
        
        Returns:
            Average relevance score (0-1)
        """
        if not chunks:
            return 0.0
        
        scores = [chunk.get('score', 0.0) for chunk in chunks]
        return sum(scores) / len(scores) if scores else 0.0


# Example usage
if __name__ == "__main__":
    # Test retrieval service
    service = RetrievalService()
    
    # Mock knowledge base
    kb_docs = [
        {"id": 1, "text": "Diabetes is a chronic disease that affects blood sugar levels.", "source": "diabetes.pdf", "page": 1},
        {"id": 2, "text": "Symptoms include increased thirst and frequent urination.", "source": "diabetes.pdf", "page": 2},
        {"id": 3, "text": "Hypertension is high blood pressure.", "source": "hypertension.pdf", "page": 1}
    ]
    
    # Generate embeddings
    texts = [doc['text'] for doc in kb_docs]
    kb_embeddings = service.generate_embeddings(texts)
    
    # Test retrieval
    query = "What are the symptoms of diabetes?"
    results = service.retrieve_relevant_chunks(query, kb_docs, kb_embeddings, top_k=2)
    
    print(f"\nQuery: {query}")
    print(f"Retrieved {len(results)} chunks:\n")
    for chunk in results:
        print(f"- [{chunk['relevance']}] {chunk['text'][:50]}... (score: {chunk['score']:.2f})")
