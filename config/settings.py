"""
Configuration Settings for Health Hackathon RAG System

All configurable parameters in one place.
"""

import os

# =========================
# Application Settings
# =========================
APP_NAME = "Health Hackathon RAG System"
APP_VERSION = "1.0.0"
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5003
DEBUG_MODE = True

# =========================
# Security
# =========================
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', 'health_admin_2026')  # CHANGE THIS!
SECRET_KEY = os.getenv('SECRET_KEY', 'health-hackathon-secret-key-change-me')

# =========================
# File Storage
# =========================
UPLOAD_DIR = "uploads_health"
KB_FILE = "knowledge_base_health.json"
UPLOAD_LOGS = "upload_logs_health.json"
SESSION_DIR = "flask_sessions"

# =========================
# Document Processing
# =========================
MAX_FILE_SIZE_MB = 50  # Increased for medical documents
CHUNK_SIZE = 300  # Words per chunk
MIN_CHUNK_WORDS = 40
ALLOWED_EXTENSIONS = {'pdf'}

# =========================
# RAG Settings
# =========================
TOP_K_CHUNKS = 5  # Number of chunks to retrieve
MIN_RELEVANCE_SCORE = 0.25  # Minimum similarity score
BATCH_SIZE = 100  # For processing large KBs

# =========================
# Embedding Model
# =========================
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Sentence transformer model

# =========================
# Ollama Settings
# =========================
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')  # or 'phi', 'mistral', etc.
OLLAMA_TEMPERATURE = 0.3  # Lower for factual responses
OLLAMA_MAX_TOKENS = 500
OLLAMA_TIMEOUT = 60  # seconds

# =========================
# Response Settings
# =========================
NO_ANSWER_MESSAGE = "I don't have that information in the available medical documents. Please consult a healthcare professional for accurate medical advice."
ERROR_MESSAGE = "I'm experiencing technical difficulties. Please try again or contact support."

# =========================
# Logging
# =========================
LOG_LEVEL = "INFO"
LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"

def get_config_summary():
    """Return a summary of current configuration."""
    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "port": FLASK_PORT,
        "ollama_url": OLLAMA_BASE_URL,
        "ollama_model": OLLAMA_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "top_k": TOP_K_CHUNKS,
        "chunk_size": CHUNK_SIZE,
        "max_file_size_mb": MAX_FILE_SIZE_MB
    }
