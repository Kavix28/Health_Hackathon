"""
Health Hackathon RAG System - Main Application

A Flask-based RAG (Retrieval-Augmented Generation) chatbot for health information,
powered by Ollama (local LLM) with semantic search.

NO OPENAI. NO CLOUD APIs. FULLY LOCAL.

Features:
- Admin document management (upload, delete, view)
- PDF processing with intelligent chunking
- Semantic search with sentence transformers
- Ollama-powered response generation
- Anti-hallucination safeguards
- Source citation
"""

import os
import json
import time
from flask import Flask, request, jsonify, send_from_directory, session, abort
from flask_session import Session
from werkzeug.utils import secure_filename
import logging

# Import our custom services
from services.ollama_service import OllamaService
from services.retrieval_service import RetrievalService
from services.document_processor import DocumentProcessor
from config.settings import *
from config.prompts import PromptTemplates

# =========================
# Flask Setup
# =========================
app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = SECRET_KEY

app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = SESSION_DIR
app.config["SESSION_PERMANENT"] = False
Session(app)

# =========================
# Logging
# =========================
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# =========================
# Create Directories
# =========================
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)

# =========================
# Initialize Services
# =========================
logger.info("="*60)
logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
logger.info("="*60)

# Initialize services
retrieval_service = RetrievalService(model_name=EMBEDDING_MODEL)
document_processor = DocumentProcessor(chunk_size=CHUNK_SIZE, min_chunk_words=MIN_CHUNK_WORDS)

# Initialize Ollama service
try:
    ollama_service = OllamaService(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
    if ollama_service.test_connection():
        logger.info(f"✓ Ollama service ready: {OLLAMA_MODEL}")
    else:
        logger.warning(f"⚠ Ollama model '{OLLAMA_MODEL}' not found")
        logger.warning(f"⚠ Run: ollama pull {OLLAMA_MODEL}")
except Exception as e:
    logger.error(f"✗ Ollama initialization failed: {str(e)}")
    ollama_service = None

# =========================
# Knowledge Base
# =========================
kb_docs = []
kb_embeddings = None

def load_json(path):
    """Load JSON file."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_json(path, data):
    """Save JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_kb():
    """Load knowledge base and generate embeddings."""
    global kb_docs, kb_embeddings
    
    try:
        kb_docs = load_json(KB_FILE)
        
        if not kb_docs:
            kb_embeddings = None
            logger.info("[INFO] Knowledge base is empty")
            return
        
        # Validate structure
        if not isinstance(kb_docs, list) or not all(isinstance(d, dict) and "text" in d for d in kb_docs):
            logger.error(f"[ERROR] Invalid knowledge base format")
            kb_docs = []
            kb_embeddings = None
            return
        
        logger.info(f"[*] Loading {len(kb_docs)} chunks from knowledge base...")
        
        # Generate embeddings
        texts = [d["text"] for d in kb_docs]
        kb_embeddings = retrieval_service.generate_embeddings(texts, batch_size=BATCH_SIZE)
        
        logger.info(f"[OK] Knowledge base loaded: {len(kb_docs)} chunks")
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to load knowledge base: {str(e)}")
        kb_docs = []
        kb_embeddings = None

# Load KB on startup
load_kb()

# =========================
# Helper Functions
# =========================
def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_admin():
    """Check if current session is authenticated as admin."""
    return session.get('admin_authenticated') == True

# =========================
# Routes: Main Pages
# =========================
@app.route('/')
def index():
    """Serve patient chat interface."""
    return send_from_directory('static', 'chat_health.html')

@app.route('/admin')
def admin():
    """Serve admin dashboard (requires authentication)."""
    return send_from_directory('static', 'admin_health.html')

# =========================
# Routes: Admin Authentication
# =========================
@app.route('/admin/auth', methods=['POST'])
def admin_auth():
    """Authenticate admin."""
    data = request.get_json()
    token = data.get('token', '')
    
    if token == ADMIN_TOKEN:
        session['admin_authenticated'] = True
        logger.info("[ADMIN] Authentication successful")
        return jsonify({"success": True, "message": "Authenticated"})
    else:
        logger.warning("[ADMIN] Authentication failed")
        return jsonify({"success": False, "message": "Invalid token"}), 401

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    """Logout admin."""
    session.pop('admin_authenticated', None)
    logger.info("[ADMIN] Logged out")
    return jsonify({"success": True})

#=========================
# Routes: Admin Document Management
# =========================
@app.route('/admin/upload', methods=['POST'])
def admin_upload():
    """Upload and process PDF document."""
    if not is_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"success": False, "message": "Only PDF files allowed"}), 400
    
    try:
        # Secure filename
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        # Check if already exists
        if os.path.exists(filepath):
            return jsonify({"success": False, "message": "File already exists"}), 400
        
        # Save file
        file.save(filepath)
        logger.info(f"[UPLOAD] Saved: {filename}")
        
        # Validate PDF
        is_valid, msg = document_processor.validate_pdf(filepath, max_size_mb=MAX_FILE_SIZE_MB)
        if not is_valid:
            os.remove(filepath)
            return jsonify({"success": False, "message": f"Invalid PDF: {msg}"}), 400
        
        # Process PDF
        chunks = document_processor.process_pdf_to_chunks(filepath, source_name=filename)
        
        if not chunks:
            os.remove(filepath)
            return jsonify({"success": False, "message": "No text extracted from PDF"}), 400
        
        # Add to knowledge base
        global kb_docs, kb_embeddings
        
        # Assign new IDs
        next_id = max([d.get('id', 0) for d in kb_docs], default=0) + 1
        for i, chunk in enumerate(chunks):
            chunk['id'] = next_id + i
        
        kb_docs.extend(chunks)
        
        # Regenerate embeddings
        texts = [d["text"] for d in kb_docs]
        kb_embeddings = retrieval_service.generate_embeddings(texts, batch_size=BATCH_SIZE)
        
        # Save KB
        save_json(KB_FILE, kb_docs)
        
        # Log upload
        upload_logs = load_json(UPLOAD_LOGS)
        upload_logs.append({
            "filename": filename,
            "timestamp": time.time(),
            "chunks": len(chunks),
            "status": "success"
        })
        save_json(UPLOAD_LOGS, upload_logs)
        
        logger.info(f"[SUCCESS] Processed {filename}: {len(chunks)} chunks added")
        
        return jsonify({
            "success": True,
            "message": f"Successfully processed {filename}",
            "chunks_added": len(chunks),
            "total_chunks": len(kb_docs)
        })
        
    except Exception as e:
        logger.error(f"[ERROR] Upload failed: {str(e)}")
        # Clean up file if it exists
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"success": False, "message": f"Processing error: {str(e)}"}), 500

@app.route('/admin/documents', methods=['GET'])
def admin_list_documents():
    """List all uploaded documents with statistics."""
    if not is_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    try:
        # Get all PDF files
        files = []
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                if filename.endswith('.pdf'):
                    filepath = os.path.join(UPLOAD_DIR, filename)
                    file_size = os.path.getsize(filepath)
                    
                    # Count chunks for this file
                    chunk_count = sum(1 for d in kb_docs if d.get('source') == filename)
                    
                    files.append({
                        "filename": filename,
                        "size_mb": round(file_size / (1024 * 1024), 2),
                        "chunks": chunk_count
                    })
        
        return jsonify({
            "success": True,
            "documents": files,
            "total_documents": len(files),
            "total_chunks": len(kb_docs)
        })
        
    except Exception as e:
        logger.error(f"[ERROR] List documents failed: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/admin/delete/<filename>', methods=['DELETE'])
def admin_delete_document(filename):
    """Delete a document."""
    if not is_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    try:
        filepath = os.path.join(UPLOAD_DIR, secure_filename(filename))
        
        if not os.path.exists(filepath):
            return jsonify({"success": False, "message": "File not found"}), 404
        
        # Remove file
        os.remove(filepath)
        
        # Remove chunks from KB
        global kb_docs, kb_embeddings
        
        original_count = len(kb_docs)
        kb_docs = [d for d in kb_docs if d.get('source') != filename]
        removed_count = original_count - len(kb_docs)
        
        # Regenerate embeddings
        if kb_docs:
            texts = [d["text"] for d in kb_docs]
            kb_embeddings = retrieval_service.generate_embeddings(texts, batch_size=BATCH_SIZE)
        else:
            kb_embeddings = None
        
        # Save KB
        save_json(KB_FILE, kb_docs)
        
        logger.info(f"[DELETE] Removed {filename}: {removed_count} chunks deleted")
        
        return jsonify({
            "success": True,
            "message": f"Deleted {filename}",
            "chunks_removed": removed_count,
            "total_chunks": len(kb_docs)
        })
        
    except Exception as e:
        logger.error(f"[ERROR] Delete failed: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/admin/stats', methods=['GET'])
def admin_stats():
    """Get system statistics."""
    if not is_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    try:
        # Count documents
        doc_count = 0
        if os.path.exists(UPLOAD_DIR):
            doc_count = len([f for f in os.listdir(UPLOAD_DIR) if f.endswith('.pdf')])
        
        # Ollama status
        ollama_status = "Connected" if ollama_service and ollama_service.test_connection() else "Disconnected"
        
        config = get_config_summary()
        
        return jsonify({
            "success": True,
            "stats": {
                "total_documents": doc_count,
                "total_chunks": len(kb_docs),
                "ollama_status": ollama_status,
                "ollama_model": OLLAMA_MODEL,
                "embedding_model": EMBEDDING_MODEL,
                "config": config
            }
        })
        
    except Exception as e:
        logger.error(f"[ERROR] Stats failed: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

# =========================
# Routes: Patient Chat
# =========================
@app.route('/chat/query', methods=['POST'])
def chat_query():
    """
    Handle patient query with RAG pipeline.
    
    Pipeline:
    1. Receive question
    2. Retrieve relevant chunks
    3. Send to Ollama with context
    4. Return grounded response
    """
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"success": False, "message": "No question provided"}), 400
        
        logger.info(f"[QUERY] {question}")
        
        # Check if KB is empty
        if not kb_docs or kb_embeddings is None:
            return jsonify({
                "success": True,
                "answer": "The knowledge base is currently empty. Please ask an administrator to upload medical documents.",
                "sources": [],
                "confidence": 0.0
            })
        
        # Retrieve relevant chunks
        relevant_chunks = retrieval_service.retrieve_relevant_chunks(
            query=question,
            kb_docs=kb_docs,
            kb_embeddings=kb_embeddings,
            top_k=TOP_K_CHUNKS,
            min_score=MIN_RELEVANCE_SCORE
        )
        
        # Handle no relevant context found
        if not relevant_chunks:
            logger.info("[RESULT] No relevant context found")
            return jsonify({
                "success": True,
                "answer": PromptTemplates.build_no_context_response(question),
                "sources": [],
                "confidence": 0.0
            })
        
        # Check if Ollama is available
        if not ollama_service or not ollama_service.test_connection():
            logger.error("[ERROR] Ollama not available")
            return jsonify({
                "success": False,
                "message": "AI service unavailable. Please contact administrator."
            }), 503
        
        # Generate response with Ollama
        result = ollama_service.generate_rag_response(
            question=question,
            context_chunks=relevant_chunks,
            temperature=OLLAMA_TEMPERATURE,
            max_tokens=OLLAMA_MAX_TOKENS
        )
        
        if result.get("error"):
            logger.error(f"[ERROR] Ollama generation failed: {result['error']}")
            return jsonify({
                "success": False,
                "message": "Failed to generate response"
            }), 500
        
        # Add medical disclaimer
        answer = PromptTemplates.add_medical_disclaimer(result["answer"])
        
        logger.info(f"[RESULT] Confidence: {result['confidence']:.2f}, Sources: {len(result['sources'])}")
        
        return jsonify({
            "success": True,
            "answer": answer,
            "sources": result["sources"],
            "confidence": result["confidence"],
            "model": result["model"]
        })
        
    except Exception as e:
        logger.error(f"[ERROR] Query failed: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred processing your question"
        }), 500

# =========================
# Health Check
# =========================
@app.route('/health', methods=['GET'])
def health_check():
    """System health check."""
    ollama_ok = ollama_service and ollama_service.test_connection()
    kb_ok = len(kb_docs) > 0
    
    return jsonify({
        "status": "healthy" if (ollama_ok and kb_ok) else "degraded",
        "ollama": "ok" if ollama_ok else "error",
        "knowledge_base": "ok" if kb_ok else "empty",
        "chunks": len(kb_docs)
    })

# =========================
# Run Application
# =========================
if __name__ == '__main__':
    logger.info("="*60)
    logger.info(f"Starting Flask server on {FLASK_HOST}:{FLASK_PORT}")
    logger.info(f"Patient Chat: http://localhost:{FLASK_PORT}/")
    logger.info(f"Admin Panel: http://localhost:{FLASK_PORT}/admin")
    logger.info(f"Admin Token: {ADMIN_TOKEN}")
    logger.info("="*60)
    
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=DEBUG_MODE
    )
