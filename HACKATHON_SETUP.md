# ⚡ HACKATHON QUICK SETUP GUIDE

**Get the Health Hackathon RAG System running in 15 minutes**

---

## 🎯 Pre-Hackathon Checklist

Before the hackathon starts, make sure you have:

- [ ] Python 3.8+ installed
- [ ] Ollama installed and running
- [ ] At least 8GB free RAM
- [ ] 10GB free disk space
- [ ] Internet connection (for initial model download)
- [ ] Sample medical PDFs ready to upload

---

## 🚀 Speed Run Setup (15 Minutes)

### Step 1: Install Ollama (5 minutes)

```powershell
# Download from https://ollama.ai
# Install the Windows version
# Ollama will start automatically

# Pull the model
ollama pull llama3
# Alternative (smaller/faster):
ollama pull phi

# Verify
ollama list
```

Expected output:

```
NAME            SIZE
llama3:latest   4.7 GB
```

---

### Step 2: Setup Python Environment (5 minutes)

```powershell
# Navigate to project
cd c:\PROJECTS\Health_Hackathon

# Create virtual environment
python -m venv .venv

# Activate
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

You'll see packages installing. Wait for completion (~3-5 minutes).

---

### Step 3: Start the Application (1 minute)

```powershell
python app.py
```

Expected output:

```
============================================================
Starting Health Hackathon RAG System v1.0.0
============================================================
✓ Connected to Ollama at http://localhost:11434
✓ Available models: ['llama3:latest']
[*] Loading embedding model: all-MiniLM-L6-v2
✓ Embedding model loaded
[INFO] Knowledge base is empty
============================================================
Starting Flask server on 0.0.0.0:5003
Patient Chat: http://localhost:5003/
Admin Panel: http://localhost:5003/admin
Admin Token: health_admin_2026
============================================================
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5003
```

---

### Step 4: Upload First Document (3 minutes)

1. Open browser: http://localhost:5003/admin
2. Enter token: `health_admin_2026`
3. Drag and drop a medical PDF
4. Wait for processing (5-30 seconds depending on size)
5. See success message with chunk count

---

### Step 5: Test the System (1 minute)

1. Open new tab: http://localhost:5003/
2. Ask a question covered in your PDF
3. Verify you get:
   - Grounded answer
   - Source citation
   - Confidence score
   - Medical disclaimer

---

## 📋 Hackathon Demo Script

### For Judges (5-Minute Demo)

**1. Introduction (30 seconds)**

> "This is a fully local RAG system for medical information. No OpenAI, no cloud APIs - everything runs on this machine using Ollama."

**2. Show Admin Panel (1 minute)**

- Open `/admin`
- Login with token
- Show upload interface
- Upload a sample medical PDF
- Show processing and chunk generation
- Display document statistics

**3. Show RAG Pipeline (2 minutes)**

- Open patient chat interface
- Ask: "What are the symptoms of [condition in your PDF]?"
- Show response with:
  - Generated answer
  - Source citation (PDF + page number)
  - Confidence score
  - Medical disclaimer
- Explain: "The system retrieved relevant chunks, sent them to Ollama, and generated a grounded response"

**4. Show Safety Features (1 minute)**

- Ask a question NOT covered in the PDF
- Show fallback response: "Information not available"
- Explain anti-hallucination mechanisms

**5. Show Architecture (30 seconds)**

- Quick walkthrough of system architecture
- Highlight local execution
- Mention production-ready features

---

## 🔧 Customization for Your Hackathon

### Change Admin Token

```python
# Edit config/settings.py
ADMIN_TOKEN = "your-custom-token-here"
```

### Change Ollama Model

```python
# Edit config/settings.py
OLLAMA_MODEL = "phi"  # or "mistral", "llama3", etc.
```

### Adjust RAG Parameters

```python
# Edit config/settings.py
TOP_K_CHUNKS = 3  # Fewer chunks = faster, less context
OLLAMA_TEMPERATURE = 0.2  # Lower = more factual, less creative
CHUNK_SIZE = 250  # Smaller chunks = more precise retrieval
```

### Change Port

```python
# Edit config/settings.py
FLASK_PORT = 8080  # Or any available port
```

---

## 🐛 Quick Troubleshooting

### Problem: Ollama not connecting

```powershell
# Check Ollama is running
ollama list

# Restart Ollama (close and reopen)
# Pull model again
ollama pull llama3
```

### Problem: Slow responses

```powershell
# Use a smaller model
ollama pull phi

# Then change config/settings.py:
OLLAMA_MODEL = "phi"
```

### Problem: Out of memory

```python
# Reduce batch size in config/settings.py
BATCH_SIZE = 50  # Default is 100

# Reduce top-K chunks
TOP_K_CHUNKS = 3  # Default is 5
```

### Problem: PDF won't upload

- Check file is actually a PDF
- Check file size < 50MB
- Check PDF has text (not just scanned images)
- Try a different PDF

---

## 📊 Testing Checklist

Before demo, verify:

- [ ] Ollama is running (`ollama list`)
- [ ] Flask server is running (check terminal output)
- [ ] Admin panel loads (http://localhost:5003/admin)
- [ ] Can login with admin token
- [ ] Can upload a PDF
- [ ] PDF processes successfully (see chunk count)
- [ ] Patient chat loads (http://localhost:5003/)
- [ ] Can ask and receive answers
- [ ] Sources appear in responses
- [ ] Confidence scores appear
- [ ] Can delete documents from admin panel

---

## 🎁 Sample Test Data

### Good Test Questions (for typical medical PDFs)

- "What are the symptoms of diabetes?"
- "How can I prevent high blood pressure?"
- "What is a balanced diet?"
- "What are the risk factors for heart disease?"
- "How much exercise should I get weekly?"

### Expected Behavior

**Question in PDF:**

- Receives detailed answer
- Sources cited
- High confidence (>60%)

**Question NOT in PDF:**

- "Information not available" message
- Recommendation to consult healthcare professional
- Confidence = 0%

---

## 💡 Pro Tips for Hackathon

1. **Pre-load Documents:** Upload all PDFs before demo starts
2. **Test Questions:** Prepare 3-5 questions you know are in your PDFs
3. **Have a Backup:** If Ollama fails, you can demo the upload/admin features
4. **Explain the "Why":** Emphasize safety, local execution, no hallucinations
5. **Show the Code:** Briefly show prompt templates or RAG pipeline code

---

## 🏆 Key Talking Points

### For Judges

**Technical Excellence:**

- "Implements complete RAG pipeline from scratch"
- "Uses sentence transformers for semantic search"
- "Ollama integration with safety prompts"
- "Clean architecture with service layer separation"

**Safety & Ethics:**

- "Anti-hallucination mechanisms prevent misinformation"
- "All responses cite sources - full transparency"
- "Medical disclaimers on every response"
- "Explicitly states when information is unavailable"

**Production-Ready:**

- "Comprehensive error handling"
- "Input validation on all endpoints"
- "Logging and monitoring"
- "Secure admin authentication"
- "Full documentation"

**Innovation:**

- "Fully local - no API costs, no privacy concerns"
- "Hackathon-ready but production-quality"
- "Extensible architecture for future enhancements"

---

## 📝 Post-Hackathon

### Cleanup

```powershell
# Deactivate virtual environment
deactivate

# Stop Flask server
# Press Ctrl+C in terminal
```

### Keep Running Permanently

```powershell
# Use waitress (production WSGI server)
pip install waitress

# Create run_production.py:
from waitress import serve
from app import app
serve(app, host='0.0.0.0', port=5003)

# Run:
python run_production.py
```

---

## 🎯 Success Criteria

Your system is hackathon-ready when:

✅ Flask server starts without errors
✅ Ollama connection success message appears
✅ Admin login works
✅ PDF upload completes successfully
✅ Knowledge base shows chunk count > 0
✅ Patient chat returns answers with sources
✅ No-context questions get safe fallback
✅ All responses include medical disclaimers

---

**You're ready to win the hackathon! 🏅**

Good luck, and remember: emphasize **safety**, **local execution**, and **production quality**!
