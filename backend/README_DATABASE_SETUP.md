# Database Setup Guide

This guide explains how to set up the PostgreSQL database for the Niki RAG application.

## 📋 Overview

The database schema has been consolidated into a single migration that includes:

-   Users table (authentication)
-   Collections table (document groupings)
-   Documents table (uploaded files)
-   Chat sessions table (conversations with AI settings)
-   Messages table (chat messages with audio/translation support)

## 🚀 Quick Start for New PostgreSQL Database

### 1. Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE niki_db;

# Create user (optional)
CREATE USER niki_user WITH PASSWORD 'your_password';

# Grant permissions
GRANT ALL PRIVILEGES ON DATABASE niki_db TO niki_user;

# Exit
\q
```

### 2. Update Environment Variables

Update your `backend/.env` file:

```env
DATABASE_URL=postgresql://niki_user:your_password@localhost:5432/niki_db
# or for local development:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/niki_db
```

### 3. Run Database Creation Script

```bash
cd backend

# Option 1: Use the consolidated creation script (recommended for fresh DB)
python scripts/create_fresh_db.py

# Option 2: Use alembic (if you want migration tracking)
alembic upgrade head
```

### 4. Initialize Default Data

```bash
# Create default user and collection
python init_db.py
```

### 5. Start the Application

```bash
# Start the server
uvicorn app.main:app --reload

# Visit API docs
open http://localhost:8000/api/docs
```

## 📊 Database Schema

### Tables Created

#### `users`

-   User authentication and profile data
-   Columns: id, email, hashed_password, is_active, created_at, updated_at

#### `collections`

-   Document collections/groupings
-   Columns: id, name, description, user_id, embedding_model, created_at, updated_at

#### `documents`

-   Uploaded document metadata
-   Columns: id, filename, file_path, file_type, file_size, collection_id, user_id, status, chunk_count, error_message, doc_metadata, created_at, processed_at

#### `chat_sessions`

-   Chat conversation sessions
-   Columns: id, title, user_id, collection_id, llm_model, temperature, max_tokens, top_k, system_prompt, custom_instructions, prompt_template, ai_personality, response_style, created_at, updated_at

#### `messages`

-   Individual chat messages
-   Columns: id, session_id, role, content, sources, llm_used, audio_url, translated_content, created_at

## 🔄 Migration History

All previous migrations have been consolidated into:

-   `1765135352_a12bfc35-03a_consolidated_schema_creation.py`

This includes:

-   ✅ Base schema creation
-   ✅ AI settings for chat sessions
-   ✅ Audio and translation support for messages

## 🛠️ Troubleshooting

### Connection Issues

```bash
# Test database connection
psql -U niki_user -d niki_db -h localhost -p 5432

# If connection fails, check:
# 1. PostgreSQL is running: sudo systemctl status postgresql
# 2. Database exists: \l in psql
# 3. User has permissions: \du in psql
```

### Migration Issues

```bash
# Reset database completely
cd backend
python scripts/create_fresh_db.py

# Or stamp alembic to specific revision
alembic stamp a12bfc35-03a1
```

### Permission Issues

```bash
# Grant schema permissions
psql -U postgres -d niki_db -c "GRANT ALL ON SCHEMA public TO niki_user;"
psql -U postgres -d niki_db -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO niki_user;"
```

## 🎯 Next Steps

After database setup:

1. Upload documents via `/api/v1/documents/upload`
2. Create chat sessions via `/api/v1/chat/sessions`
3. Start chatting with your documents!

The application now supports:

-   ✅ Full-text search with vector embeddings
-   ✅ Audio generation for AI responses
-   ✅ Text translation (Hindi support)
-   ✅ GPU acceleration (when available)
-   ✅ Multi-user authentication
