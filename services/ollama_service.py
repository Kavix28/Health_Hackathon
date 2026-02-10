"""
Ollama Service: Local LLM Integration for Health Hackathon

This service handles all interactions with the Ollama local LLM.
No cloud APIs. No OpenAI. Fully local execution.

Key Features:
- Local LLM execution via Ollama API
- Grounded responses using RAG context
- Anti-hallucination safeguards
- Configurable model selection
"""

import requests
import json
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaService:
    """
    Service class for interacting with Ollama LLM.
    
    Ollama must be running locally on http://localhost:11434
    
    Install: https://ollama.ai
    Pull model: ollama pull llama3
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        """
        Initialize Ollama service.
        
        Args:
            base_url: Ollama API endpoint (default: localhost:11434)
            model: Model name to use (default: llama3)
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.generate_endpoint = f"{self.base_url}/api/generate"
        self.chat_endpoint = f"{self.base_url}/api/chat"
        
        # Verify Ollama is running
        self._verify_connection()
    
    def _verify_connection(self):
        """Verify that Ollama is accessible."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"✓ Connected to Ollama at {self.base_url}")
                available_models = [model['name'] for model in response.json().get('models', [])]
                logger.info(f"✓ Available models: {available_models}")
                
                if self.model not in [m.split(':')[0] for m in available_models]:
                    logger.warning(f"⚠ Model '{self.model}' not found. Available: {available_models}")
                    logger.warning(f"⚠ Run: ollama pull {self.model}")
            else:
                logger.error(f"✗ Ollama connection failed: HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            logger.error(f"✗ Cannot connect to Ollama at {self.base_url}")
            logger.error("✗ Please ensure Ollama is running")
            logger.error("✗ Install from: https://ollama.ai")
        except Exception as e:
            logger.error(f"✗ Ollama verification error: {str(e)}")
    
    def generate_rag_response(
        self,
        question: str,
        context_chunks: List[Dict],
        temperature: float = 0.3,
        max_tokens: int = 500
    ) -> Dict[str, any]:
        """
        Generate a grounded response using RAG context.
        
        This is the CORE RAG function for the hackathon.
        
        Args:
            question: The user's question
            context_chunks: List of retrieved document chunks
            temperature: LLM temperature (lower = more factual)
            max_tokens: Maximum response length
        
        Returns:
            {
                "answer": str,
                "sources": List[str],
                "confidence": float,
                "model": str,
                "error": Optional[str]
            }
        """
        try:
            # Build the RAG prompt
            prompt = self._build_rag_prompt(question, context_chunks)
            
            # Make request to Ollama
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            logger.info(f"Sending request to Ollama ({self.model})...")
            response = requests.post(
                self.generate_endpoint,
                json=payload,
                timeout=60  # Longer timeout for LLM generation
            )
            
            if response.status_code != 200:
                return {
                    "answer": "I apologize, but I'm having trouble generating a response right now.",
                    "sources": [],
                    "confidence": 0.0,
                    "model": self.model,
                    "error": f"HTTP {response.status_code}"
                }
            
            result = response.json()
            answer = result.get("response", "").strip()
            
            # Extract sources from context chunks
            sources = self._extract_sources(context_chunks)
            
            # Calculate confidence based on context relevance
            confidence = self._calculate_confidence(context_chunks)
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "model": self.model,
                "error": None
            }
            
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return {
                "answer": "The request took too long. Please try a simpler question.",
                "sources": [],
                "confidence": 0.0,
                "model": self.model,
                "error": "Timeout"
            }
        except Exception as e:
            logger.error(f"Ollama generation error: {str(e)}")
            return {
                "answer": "An error occurred while generating the response.",
                "sources": [],
                "confidence": 0.0,
                "model": self.model,
                "error": str(e)
            }
    
    def _build_rag_prompt(self, question: str, context_chunks: List[Dict]) -> str:
        """
        Build the RAG prompt with anti-hallucination instructions.
        
        This is CRITICAL for preventing medical misinformation.
        """
        # Extract context text from chunks
        contexts = []
        for i, chunk in enumerate(context_chunks, 1):
            text = chunk.get('text', '')
            source = chunk.get('source', 'Unknown')
            page = chunk.get('page', '?')
            contexts.append(f"[Context {i} from {source}, Page {page}]\n{text}\n")
        
        context_text = "\n".join(contexts)
        
        # Build the prompt with strict grounding instructions
        prompt = f"""You are a health information assistant. Your role is to provide accurate, factual information based ONLY on the provided medical documents.

STRICT RULES:
1. Answer ONLY using information from the context below
2. If the answer is not in the context, say "I don't have that information in the available documents"
3. Do NOT use your general knowledge or training data
4. Do NOT make up or infer information
5. Be concise and clear
6. Cite the context number when referring to information

CONTEXT:
{context_text}

QUESTION: {question}

ANSWER (based only on the context above):"""
        
        return prompt
    
    def _extract_sources(self, context_chunks: List[Dict]) -> List[str]:
        """Extract unique sources from context chunks."""
        sources = []
        seen = set()
        
        for chunk in context_chunks:
            source = chunk.get('source', 'Unknown')
            page = chunk.get('page', '?')
            source_str = f"{source} (Page {page})"
            
            if source_str not in seen:
                sources.append(source_str)
                seen.add(source_str)
        
        return sources
    
    def _calculate_confidence(self, context_chunks: List[Dict]) -> float:
        """
        Calculate confidence score based on retrieval quality.
        
        Higher score = more relevant context
        """
        if not context_chunks:
            return 0.0
        
        # Use the average relevance score from the chunks
        # (This assumes the retrieval service adds a 'score' field)
        scores = [chunk.get('score', 0.5) for chunk in context_chunks]
        avg_score = sum(scores) / len(scores) if scores else 0.5
        
        return round(avg_score, 2)
    
    def test_connection(self) -> bool:
        """
        Test if Ollama is accessible and the model is available.
        
        Returns:
            True if Ollama is ready, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                return any(self.model in name for name in model_names)
            return False
        except:
            return False
    
    def generate_simple_response(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate a simple response without RAG context.
        Useful for greetings and general queries.
        
        Args:
            prompt: The prompt to send
            temperature: Creativity level
        
        Returns:
            Generated text response
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": 200
                }
            }
            
            response = requests.post(self.generate_endpoint, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            else:
                return "I'm having trouble responding right now."
                
        except Exception as e:
            logger.error(f"Simple generation error: {str(e)}")
            return "An error occurred."


# Example usage
if __name__ == "__main__":
    # Test the Ollama service
    service = OllamaService()
    
    if service.test_connection():
        print("✓ Ollama is ready!")
        
        # Test simple generation
        response = service.generate_simple_response("Say hello!")
        print(f"Response: {response}")
    else:
        print("✗ Ollama is not ready")
        print("Run: ollama pull llama3")
