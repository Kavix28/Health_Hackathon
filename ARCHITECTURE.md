# 🏗️ Health Hackathon RAG System - Technical Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    HEALTH HACKATHON SYSTEM                       │
│                 RAG-Powered Medical Information Bot              │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                         │
├───────────────────────────────┬──────────────────────────────────┤
│   Admin Dashboard             │   Patient Chat Interface         │
│   (admin_health.html)         │   (chat_health.html)            │
│                               │                                  │
│   • Upload PDFs               │   • Ask Questions               │
│   • View Documents            │   • View Responses              │
│   • Delete Documents          │   • See Sources                 │
│   • View Statistics           │   • Check Confidence            │
└───────────────────────────────┴──────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                            │
│                        (Flask - app.py)                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Routes:                        Middleware:                      │
│  • /admin/auth                  • Session Management             │
│  • /admin/upload                • Token Authentication           │
│  • /admin/documents             • File Validation                │
│  • /admin/delete/<file>         • Error Handling                 │
│  • /chat/query                  • Logging                        │
│  • /health                                                        │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                       SERVICE LAYER                               │
├──────────────────────┬──────────────────────┬───────────────────┤
│  OllamaService       │  RetrievalService    │ DocumentProcessor │
│  (ollama_service.py) │ (retrieval_service.py)│(document_processor│
│                      │                       │      .py)        │
│  • LLM inference     │  • Semantic search   │  • PDF extraction│
│  • RAG response      │  • Embedding gen.    │  • Text chunking │
│  • Prompt building   │  • Similarity calc.  │  • Validation    │
│  • Safety checks     │  • Top-K retrieval   │  • Page tracking │
└──────────────────────┴──────────────────────┴───────────────────┘
         │                       │                      │
         │                       │                      │
         ▼                       ▼                      ▼
┌─────────────────┐    ┌──────────────────┐   ┌────────────────┐
│  Ollama API     │    │ Sentence         │   │ PDFPlumber     │
│  localhost:11434│    │ Transformers     │   │ Library        │
│                 │    │ (all-MiniLM-L6)  │   │                │
│  • llama3       │    │                  │   │ • Text extract │
│  • Local exec.  │    │ • Embeddings     │   │ • Page info    │
└─────────────────┘    └──────────────────┘   └────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                 │
├──────────────────────┬──────────────────────┬───────────────────┤
│  knowledge_base_     │  uploads_health/     │  upload_logs_     │
│  health.json         │                      │  health.json      │
│                      │                      │                   │
│  [                   │  • PDF files         │  [                │
│    {                 │  • Secure storage    │    {              │
│      "id": 1,        │  • Original docs     │      "filename",  │
│      "text": "...",  │                      │      "timestamp", │
│      "source": "...",│                      │      "chunks",    │
│      "page": 3       │                      │      "status"     │
│    },                │                      │    }              │
│    ...               │                      │  ]                │
│  ]                   │                      │                   │
└──────────────────────┴──────────────────────┴───────────────────┘
```

---

## RAG Pipeline (Detailed)

### 1. Document Upload Flow

```
Admin uploads PDF
       │
       ▼
[Validation]
 • File size check (<50MB)
 • PDF format verification
 • Text extraction test
       │
       ▼
[Text Extraction]
 • PDFPlumber reads each page
 • Adds [Page N] markers
 • Concatenates to full text
       │
       ▼
[Chunking]
 • Split by page markers
 • Chunk into 300-word segments
 • Maintain page attribution
 • Keep chunks >= 40 words
       │
       ▼
[Embedding Generation]
 • Sentence Transformer encodes each chunk
 • Generates 384-dim vectors
 • Batch processing for efficiency
       │
       ▼
[Knowledge Base Update]
 • Assign unique IDs to chunks
 • Add to kb_docs array
 • Regenerate full embedding matrix
 • Save to knowledge_base_health.json
       │
       ▼
Success - Document indexed
```

### 2. Query Processing Flow

```
User asks question
       │
       ▼
[Question Embedding]
 • Encode question with Sentence Transformer
 • Generate 384-dim query vector
       │
       ▼
[Semantic Search]
 • Calculate cosine similarity: scores = kb_embeddings @ query_vector
 • Sort by similarity score
 • Filter by min_score (0.25)
 • Select top-K chunks (5)
       │
       ├─[No relevant chunks]──> Return "No information found"
       │
       ▼
[RAG Prompt Construction]
 • Build context from top-K chunks
 • Add source citations
 • Insert anti-hallucination instructions
 • Format: SYSTEM + CONTEXT + QUESTION
       │
       ▼
[Ollama Generation]
 • POST to localhost:11434/api/generate
 • Model: llama3
 • Temperature: 0.3 (factual)
 • Stream: false
 • Max tokens: 500
       │
       ▼
[Response Processing]
 • Extract generated text
 • Add medical disclaimer
 • Format source citations
 • Calculate confidence score
       │
       ▼
[Return to User]
 • Answer text
 • Sources list
 • Confidence score
 • Model name
```

---

## Component Details

### 1. OllamaService

**Responsibilities:**

- Connect to Ollama API
- Generate RAG responses
- Build safety-focused prompts
- Handle API errors

**Key Methods:**

```python
generate_rag_response(question, context_chunks, temperature, max_tokens)
├─ Builds RAG prompt with anti-hallucination rules
├─ Sends POST to Ollama API
├─ Parses response
├─ Calculates confidence
└─ Returns formatted result

_build_rag_prompt(question, context_chunks)
├─ Injects system instructions
├─ Formats context with sources
├─ Adds question
└─ Returns complete prompt

test_connection()
└─ Verifies Ollama is accessible and model is available
```

**Safety Features:**

- Explicit "use ONLY context" instructions
- Fallback for no-context scenarios
- Model-specific prompt optimization
- Error handling for timeouts

---

### 2. RetrievalService

**Responsibilities:**

- Semantic search via embeddings
- Generate embeddings for new documents
- Calculate relevance scores

**Key Methods:**

```python
retrieve_relevant_chunks(query, kb_docs, kb_embeddings, top_k, min_score)
├─ Embed query
├─ Compute similarity: np.dot(kb_embeddings, query_embedding)
├─ Sort and filter by min_score
├─ Return top-K chunks with scores
└─ Add relevance labels (High/Medium/Low)

generate_embeddings(texts, batch_size)
├─ Use Sentence Transformer
├─ Batch processing for large sets
├─ Normalize embeddings
└─ Return numpy array
```

**Search Algorithm:**

```
Cosine Similarity = (kb_embedding · query_embedding) / (||kb|| × ||query||)

Since embeddings are normalized during generation:
  ||kb|| = ||query|| = 1

Therefore:
  Cosine Similarity = kb_embedding · query_embedding (simple dot product)

Scores range from -1 to 1 (higher = more similar)
```

---

### 3. DocumentProcessor

**Responsibilities:**

- Extract text from PDFs
- Intelligent chunking with page info
- Validate PDFs

**Key Methods:**

```python
extract_text_from_pdf(pdf_path)
├─ Open with PDFPlumber
├─ Iterate through pages
├─ Add [Page N] markers
├─ Concatenate text
└─ Return full text with markers

chunk_text_with_pages(text)
├─ Split on [Page N] markers
├─ For each page section:
│   ├─ Split into words
│   ├─ Create 300-word chunks
│   ├─ Assign page number
│   └─ Clean text
└─ Return list of (chunk_text, page_number)

process_pdf_to_chunks(pdf_path, source_name)
├─ extract_text_from_pdf()
├─ chunk_text_with_pages()
├─ Build chunk dictionaries with metadata
└─ Return list of chunk dicts
```

**Chunking Strategy:**

- **Size:** 300 words per chunk (balance between context and precision)
- **Overlap:** None (simplifies implementation, still effective)
- **Min size:** 40 words (filter out fragments)
- **Page tracking:** Essential for source attribution

---

## Data Models

### Chunk Object

```json
{
  "id": 42,
  "text": "Diabetes is a chronic disease that affects how your body turns food into energy. Most of the food you eat is broken down into sugar (glucose) and released into your bloodstream...",
  "source": "diabetes_overview.pdf",
  "page": 3
}
```

### Query Response

```json
{
  "success": true,
  "answer": "Diabetes symptoms include increased thirst, frequent urination, extreme hunger, unexplained weight loss, fatigue, blurred vision, and slow-healing sores.",
  "sources": [
    "diabetes_overview.pdf (Page 3)",
    "diabetes_overview.pdf (Page 4)"
  ],
  "confidence": 0.87,
  "model": "llama3"
}
```

### Upload Log Entry

```json
{
  "filename": "diabetes_guide.pdf",
  "timestamp": 1707609600.0,
  "chunks": 47,
  "status": "success"
}
```

---

## Security Architecture

### Authentication

- **Admin Token:** Stored in config (changeable via env var)
- **Session-based:** Flask-Session with filesystem storage
- **No JWT/OAuth:** Simple token auth (suitable for hackathon/demo)

### Input Validation

- **File upload:** PDF only, size limits, format validation
- **Query input:** Sanitized, trimmed
- **Filenames:** secure_filename() prevents path traversal

### Safety Mechanisms

1. **Prompt Engineering:** Explicit anti-hallucination instructions
2. **Context Grounding:** Responses must cite sources
3. **Confidence Scoring:** Warn users of low-confidence answers
4. **Medical Disclaimers:** Automatic on all responses
5. **No Context Fallback:** Explicitly state when information is unavailable

---

## Performance Optimization

### Embedding Generation

- **Batch processing:** 100 chunks at a time
- **Memory management:** Delete intermediate results
- **Normalization:** Embeddings normalized once during generation

### Knowledge Base Loading

- **Lazy loading:** KB loaded only on startup and after uploads
- **In-memory storage:** Fast retrieval without DB overhead
- **Numpy operations:** Vectorized similarity calculations

### Response Generation

- **Temperature tuning:** 0.3 for factual responses (vs 0.7 for creativity)
- **Token limits:** 500 tokens to balance quality and speed
- **Streaming disabled:** Wait for complete response (simpler implementation)

---

## Error Handling

### Hierarchical Error Handling

```
User Action
    │
    ├─[Validation Error] → HTTP 400, user-friendly message
    │
    ├─[Processing Error] → HTTP 500, log details, generic message to user
    │
    ├─[Ollama Timeout] → HTTP 503, "Service temporarily unavailable"
    │
    └─[Success] → HTTP 200, formatted response
```

### Logging Strategy

```
[INFO]  - Normal operations
[WARNING] - Degraded but functional (e.g., Ollama model not found)
[ERROR] - Failures that prevent operation
```

All logs include timestamps and context.

---

## Deployment Considerations

### Local Development

- Default port: 5003 (avoid conflicts with common ports)
- Debug mode: Enabled for development
- Auto-reload: Enabled in dev

### Production Recommendations

1. **Use Waitress:** Production WSGI server (included in requirements)
2. **Environment variables:** Move secrets to `.env`
3. **Reverse proxy:** Use nginx for SSL/TLS
4. **Rate limiting:** Add Flask-Limiter
5. **Monitoring:** Add health checks and metrics

### Scaling

- **Horizontal:** Multiple Flask instances with load balancer
- **Vertical:** Increase Ollama resources, use GPU
- **Data:** Move from JSON to PostgreSQL/MongoDB for large KBs

---

## Technology Choices - Justification

### Why Ollama?

- ✅ Fully local (no API costs, no data privacy concerns)
- ✅ Easy to use (simple REST API)
- ✅ Multiple model support
- ✅ Active community
- ❌ Requires local resources (but worth it)

### Why Sentence Transformers?

- ✅ State-of-the-art semantic search
- ✅ Fast inference
- ✅ Good balance of speed and accuracy
- ✅ No fine-tuning needed

### Why Flask?

- ✅ Lightweight and simple
- ✅ Perfect for hackathons
- ✅ Excellent ecosystem
- ✅ Easy to extend

### Why JSON for KB?

- ✅ Simple and hackathon-friendly
- ✅ Human-readable
- ✅ No DB setup required
- ❌ Not scalable past ~10k chunks (but sufficient for hackathon)

---

## Future Enhancements (Post-Hackathon)

1. **Vector Database:** Migrate to Pinecone/Weaviate for scalability
2. **Hybrid Search:** Combine semantic + keyword search
3. **User Accounts:** Multi-user support with history
4. **Feedback Loop:** Allow users to rate answers, retrain
5. **Multi-modal:** Support images in PDFs (OCR + vision models)
6. **Real-time Streaming:** Stream Ollama responses for better UX
7. **Advanced Chunking:** Sliding window, hierarchical chunks
8. **Prompt Optimization:** A/B test different prompt templates

---

**Technical Architecture Document**
**Version 1.0 - February 2026**
**Built for Health Hackathon**
