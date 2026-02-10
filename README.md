# 🏥 Health Hackathon RAG System

**A fully local, Ollama-powered RAG (Retrieval-Augmented Generation) chatbot for medical information**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-purple.svg)](https://ollama.ai)

---

## 🎯 Project Overview

This is a **hackathon-ready**, production-quality RAG system that provides grounded medical information using:

- **Ollama** for local LLM inference (NO OpenAI, NO cloud APIs)
- **Semantic search** with sentence transformers
- **Admin document management** for PDF uploads
- **Anti-hallucination** safeguards
- **Source attribution** for all responses

## ✨ Features

### For Administrators

- 📤 **Upload PDF Documents** - Drag-and-drop or file picker
- 📊 **View Statistics** - Track documents, chunks, and system health
- 🗑️ **Delete Documents** - Remove outdated or incorrect information
- 🔒 **Secure Access** - Token-based authentication

### For Patients/Users

- 💬 **Natural Language Queries** - Ask health questions in plain English
- 🎯 **Grounded Responses** - Answers based ONLY on uploaded documents
- 📚 **Source Citations** - Every answer includes PDF source and page number
- ⚕️ **Medical Disclaimers** - Automatic safety warnings on all responses
- 📈 **Confidence Scoring** - Know how reliable the answer is

### Technical Features

- 🔍 **Semantic Search** - Finds relevant information even with different wording
- 🧠 **RAG Pipeline** - Combines retrieval with generation for accuracy
- 🚫 **No Hallucinations** - Strict prompts prevent fabricated information
- 💪 **Fully Local** - No data leaves your machine
- ⚡ **Fast Processing** - Batch embedding generation for efficiency

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Ollama** - [Download here](https://ollama.ai)
3. **At least 8GB RAM** (16GB recommended for larger models)

### Installation Steps

#### 1. Navigate to the Project

```powershell
cd c:\PROJECTS\Health_Hackathon
```

#### 2. Create Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

#### 3. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

#### 4. Install and Setup Ollama

**Download Ollama:**

- Visit https://ollama.ai
- Download the Windows installer
- Install Ollama

**Pull the desired model:**

```powershell
# Recommended: Llama 3 (4.7GB)
ollama pull llama3

# Alternative: Phi-2 (smaller, faster - 1.6GB)
ollama pull phi

# Alternative: Mistral (4.1GB)
ollama pull mistral
```

**Verify Ollama is running:**

```powershell
ollama list
```

You should see your downloaded models.

#### 5. Configure the Application (Optional)

Edit `config/settings.py` to customize:

- Admin token
- Ollama model selection
- Port number
- RAG parameters

#### 6. Run the Application

```powershell
python app.py
```

You should see:

```
============================================================
Starting Health Hackathon RAG System v1.0.0
============================================================
✓ Connected to Ollama at http://localhost:11434
✓ Available models: ['llama3:latest']
✓ Embedding model loaded
[INFO] Knowledge base is empty
============================================================
Starting Flask server on 0.0.0.0:5003
Patient Chat: http://localhost:5003/
Admin Panel: http://localhost:5003/admin
Admin Token: health_admin_2026
============================================================
```

#### 7. Access the System

**Patient Chat Interface:**

- Open browser: http://localhost:5003/
- Start asking health questions
- (Initially, you'll get "knowledge base empty" - upload documents first)

**Admin Dashboard:**

1. Open browser: http://localhost:5003/admin
2. Enter admin token: `health_admin_2026` (or your custom token)
3. Upload medical PDF documents
4. View statistics and manage documents

---

## 📖 Usage Guide

### Admin Workflow

1. **Login**
   - Go to `/admin`
   - Enter the admin token from `config/settings.py`

2. **Upload Documents**
   - Drag and drop a PDF onto the upload zone, OR
   - Click the upload zone to browse files
   - Wait for processing (you'll see chunk count)
   - Documents are automatically indexed

3. **View Documents**
   - See all uploaded PDFs with size and chunk statistics
   - Monitor system health and Ollama status

4. **Delete Documents**
   - Click "Delete" on any document
   - Chunks are automatically removed from knowledge base
   - Embeddings are regenerated

### Patient Workflow

1. **Ask a Question**
   - Type your health question in the chat box
   - Press Enter or click Send

2. **Receive Answer**
   - The system retrieves relevant document chunks
   - Ollama generates a grounded response
   - You see:
     - The answer
     - Confidence score
     - Source citations (PDF + page number)
     - Medical disclaimer

3. **Example Questions**
   - "What are the symptoms of diabetes?"
   - "How can I prevent hypertension?"
   - "What is a healthy diet for heart disease?"

---

## 🏗️ Architecture

```
User Question
      ↓
[Sentence Transformer] → Embedding
      ↓
[Semantic Search] → Top-5 Relevant Chunks
      ↓
[Prompt Builder] → RAG Prompt with Context
      ↓
[Ollama LLM] → Generate Response
      ↓
[Response Formatter] → Add Sources + Disclaimer
      ↓
User Answer
```

### Technology Stack

**Backend:**

- Flask - Web framework
- Sentence Transformers - Semantic embeddings
- PDFPlumber - PDF text extraction
- NumPy - Vector operations
- Ollama - Local LLM inference

**Frontend:**

- Vanilla JavaScript
- Modern CSS3 with gradients
- Font Awesome icons

**Storage:**

- JSON files for knowledge base
- Filesystem for PDFs

---

## 📁 Project Structure

```
Health_Hackathon/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
│
├── services/                   # Service layer
│   ├── ollama_service.py       # Ollama LLM integration
│   ├── document_processor.py   # PDF processing
│   └── retrieval_service.py    # Semantic search
│
├── config/                     # Configuration
│   ├── settings.py             # App settings
│   └── prompts.py              # AI prompt templates
│
├── static/                     # Frontend
│   ├── admin_health.html       # Admin dashboard
│   └── chat_health.html        # Patient chat
│
├── uploads_health/             # PDF storage
├── knowledge_base_health.json  # Document chunks + metadata
└── upload_logs_health.json     # Upload tracking
```

---

## 🔧 Configuration

### Key Settings (config/settings.py)

```python
# Security
ADMIN_TOKEN = "health_admin_2026"  # CHANGE THIS!

# Ollama
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3"  # or "phi", "mistral", etc.
OLLAMA_TEMPERATURE = 0.3  # Lower = more factual

# RAG
TOP_K_CHUNKS = 5  # Number of chunks to retrieve
MIN_RELEVANCE_SCORE = 0.25  # Minimum similarity threshold
CHUNK_SIZE = 300  # Words per chunk

# File Upload
MAX_FILE_SIZE_MB = 50
```

### Environment Variables (Optional)

Create a `.env` file:

```
ADMIN_TOKEN=your-secure-token-here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

---

## 🛡️ Safety & Anti-Hallucination

### Mechanisms

1. **Strict Prompts** - Explicit instructions to use ONLY provided context
2. **Confidence Scoring** - Low-confidence answers are flagged
3. **Source Attribution** - Every answer cites the source document
4. **No Context Fallback** - If no relevant info is found, system says so explicitly
5. **Medical Disclaimers** - All responses include professional consultation reminder

### Example Safety Responses

**Question:** "What is the cure for cancer?"
**Response (if not in documents):**

```
I don't have information about "cure for cancer" in the available medical documents.

For accurate medical information on this topic, I recommend:
1. Consulting a qualified healthcare professional
2. Visiting trusted medical websites (CDC, WHO, Mayo Clinic, etc.)
3. Asking the admin to upload relevant medical documents

⚕️ Medical Disclaimer: This information is for educational purposes only...
```

---

## 🚨 Troubleshooting

### Problem: "Ollama not available"

**Solution:**

```powershell
# Check if Ollama is running
ollama list

# If not, start Ollama service (it usually starts automatically)
# Then pull your model
ollama pull llama3
```

### Problem: "Knowledge base is empty"

**Solution:**

- Go to `/admin`
- Upload PDF documents
- Verify they appear in the documents list

### Problem: "No relevant chunks found"

**Solution:**

- Make sure your question relates to uploaded documents
- Try rephrasing the question
- Lower `MIN_RELEVANCE_SCORE` in settings (not recommended)

### Problem: "Upload fails"

**Solution:**

- Check PDF is valid (can be opened in PDF reader)
- Check file size < 50MB
- Check PDF has extractable text (not scanned images)

### Problem: "Slow responses"

**Solution:**

- Use a smaller Ollama model (phi instead of llama3)
- Reduce `OLLAMA_MAX_TOKENS` in settings
- Reduce `TOP_K_CHUNKS` to 3 instead of 5

---

## 📊 Performance

### Typical Response Times

- **PDF Upload & Processing:** 5-30 seconds (depends on PDF size)
- **Query Processing:** 2-5 seconds
  - Retrieval: <1 second
  - Ollama generation: 2-4 seconds (depends on model)

### Recommended Hardware

- **Minimum:** 8GB RAM, 4-core CPU
- **Recommended:** 16GB RAM, 8-core CPU
- **Storage:** 10GB free space (for models + documents)

---

## 🎓 For Hackathon Judges

### Why This Project Stands Out

1. **Fully Local** - No API costs, no data privacy concerns
2. **Production-Ready** - Error handling, validation, logging
3. **Safety-First** - Anti-hallucination mechanisms for medical domain
4. **Complete System** - Admin panel + user interface + backend
5. **Well-Architected** - Clean separation of concerns, modular design
6. **Documented** - Comprehensive docs for setup and usage

### Demo Flow

1. Show admin panel - upload a medical PDF
2. Show kb processing - chunks created
3. Go to chat - ask a question covered in the PDF
4. Show grounded response with sources
5. Ask a question NOT in the PDF
6. Show safe fallback response

---

## 📝 License

MIT License - See LICENSE file

---

## 🤝 Contributing

This is a hackathon project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📧 Support

For issues or questions:

- Check the Troubleshooting section
- Review the logs (Flask outputs detailed logs)
- Ensure Ollama is running and model is pulled

---

## 🙏 Acknowledgments

- **Ollama** - For making local LLM inference accessible
- **Sentence Transformers** - For powerful semantic search
- **Flask** - For the excellent web framework
- **Font Awesome** - For beautiful icons

---

**Built for Health Hackathon 2026**
**Powered by Ollama • No Cloud APIs • Fully Local**
#   H e a l t h _ H a c k a t h o n  
 