"""
AI Prompt Templates for Health Hackathon RAG System

All prompts are optimized for:
- Factual accuracy
- Grounding in source documents
- Prevention of hallucinations
- Medical information safety
"""


class PromptTemplates:
    """
    Centralized prompt templates for Ollama LLM.
    """
    
    # =========================
    # RAG System Prompt
    # =========================
    RAG_SYSTEM_PROMPT = """You are a professional health information assistant. Your role is to provide accurate, helpful information based STRICTLY on medical documents provided to you.

CRITICAL RULES:
1. Answer ONLY using information from the provided context
2. If information is not in the context, explicitly state: "This information is not available in the documents I have access to"
3. Do NOT use your general medical knowledge
4. Do NOT make assumptions or inferences beyond the context
5. Do NOT provide medical diagnoses or treatment recommendations
6. Always remind users to consult healthcare professionals for medical advice
7. Be precise, clear, and concise
8. Cite the source document when possible

RESPONSE FORMAT:
- Start with a direct answer if information is available
- Support with relevant details from the context
- End with a disclaimer if appropriate
- Cite sources like: "(Source: [document name], Page [number])"
"""
    
    # =========================
    # RAG Query Template
    # =========================
    @staticmethod
    def build_rag_prompt(question: str, context_chunks: list) -> str:
        """
        Build a complete RAG prompt with context and question.
        
        Args:
            question: User's question
            context_chunks: List of dicts with 'text', 'source', 'page'
        
        Returns:
            Complete prompt string
        """
        # Build context section
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            text = chunk.get('text', '')
            source = chunk.get('source', 'Unknown')
            page = chunk.get('page', '?')
            
            context_parts.append(
                f"[Document {i}: {source}, Page {page}]\n{text}\n"
            )
        
        context_text = "\n".join(context_parts)
        
        # Build complete prompt
        prompt = f"""{PromptTemplates.RAG_SYSTEM_PROMPT}

AVAILABLE CONTEXT:
{context_text}

USER QUESTION: {question}

ASSISTANT RESPONSE (based only on the context above):"""
        
        return prompt
    
    # =========================
    # Conversational Prompts
    # =========================
    GREETING_PROMPT = """You are a friendly health information assistant. 
Greet the user warmly and explain that you can help them find information from medical documents.
Keep it brief and professional."""
    
    HELP_PROMPT = """You are a health information assistant.
Explain to the user what you can help with:
- Answering questions about uploaded medical documents
- Providing information on health topics covered in the documents
- Citing sources for all information

Remind them that you cannot provide medical diagnoses or treatment advice."""
    
    # =========================
    # Safety Prompts
    # =========================
    NO_CONTEXT_PROMPT = """The user asked: "{question}"

However, there is NO relevant information in the available medical documents.

Respond politely and professionally:
1. State that the information is not available in the current documents
2. Suggest they consult a healthcare professional
3. Offer to help with other questions that may be in the documents

Keep it brief, empathetic, and professional."""
    
    LOW_CONFIDENCE_PROMPT = """The user asked: "{question}"

The available context has LIMITED relevance (confidence < 50%).

Context:
{context}

Respond carefully:
1. State that you found limited information
2. Provide what you found, WITH CAVEATS
3. Recommend consulting healthcare professionals for certainty
4. Cite the source

Be honest about the limitations."""
    
    # =========================
    # Disclaimer Templates
    # =========================
    MEDICAL_DISCLAIMER = "\n\n⚕️ **Medical Disclaimer**: This information is for educational purposes only and is not a substitute for professional medical advice. Please consult a qualified healthcare provider for medical concerns."
    
    SOURCE_CITATION_TEMPLATE = "(Source: {source}, Page {page})"
    
    # =========================
    # Error Messages
    # =========================
    OLLAMA_NOT_AVAILABLE = "I'm currently unable to process your request because the AI service is not available. Please ensure Ollama is running and try again."
    
    PROCESSING_ERROR = "I encountered an error while processing your question. Please try rephrasing or contact support if the issue persists."
    
    # =========================
    # Helper Methods
    # =========================
    @staticmethod
    def add_medical_disclaimer(text: str) -> str:
        """Add medical disclaimer to response."""
        if not text.strip():
            return text
        return text + PromptTemplates.MEDICAL_DISCLAIMER
    
    @staticmethod
    def format_source_citation(source: str, page: any) -> str:
        """Format a source citation."""
        return PromptTemplates.SOURCE_CITATION_TEMPLATE.format(
            source=source,
            page=page if page else "?"
        )
    
    @staticmethod
    def build_no_context_response(question: str) -> str:
        """Build response when no relevant context is found."""
        return f"""I don't have information about "{question}" in the available medical documents.

For accurate medical information on this topic, I recommend:
1. Consulting a qualified healthcare professional
2. Visiting trusted medical websites (CDC, WHO, Mayo Clinic, etc.)
3. Asking the admin to upload relevant medical documents

Is there anything else I can help you with from the available documents?"""


# Example usage
if __name__ == "__main__":
    # Test prompt building
    question = "What are the symptoms of diabetes?"
    chunks = [
        {
            "text": "Diabetes symptoms include increased thirst, frequent urination, extreme hunger, and unexplained weight loss.",
            "source": "diabetes_guide.pdf",
            "page": 3
        },
        {
            "text": "Additional symptoms may include fatigue, blurred vision, slow-healing sores, and frequent infections.",
            "source": "diabetes_guide.pdf",
            "page": 4
        }
    ]
    
    prompt = PromptTemplates.build_rag_prompt(question, chunks)
    print("=== Generated RAG Prompt ===")
    print(prompt)
    print("\n=== No Context Response ===")
    print(PromptTemplates.build_no_context_response(question))
