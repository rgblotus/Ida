# Ida RAG Application
A full-stack RAG (Retrieval-Augmented Generation) application with FastAPI backend and React frontend.

## 📁 Project Structure

```bash
Ida/
├── backend/                    # FastAPI Application Server
│   ├── app/                    # Application Source Code
│   │   ├── api/v1/             # REST API Endpoints (Routes)
│   │   │   ├── chat.py         # Chat Interface & Message Handling
│   │   │   ├── documents.py    # Document Upload & Management
│   │   │   └── ...
│   │   ├── core/               # Core Configuration & Security
│   │   ├── domain/             # Data Models (Schemas/Pydantic)
│   │   ├── infra/              # Infrastructure & Database Layer
│   │   ├── services/           # Business Logic & Integrations
│   │   │   ├── llm_service.py  # LLM Provider Integration
│   │   │   ├── speech_service.py # TTS & Translation
│   │   │   └── rag_service.py  # RAG Logic
│   │   └── main.py             # App Entry Point
│   ├── alembic/                # DB Migrations
│   ├── tests/                  # Unit & Integration Tests
│   └── .env                    # Backend Env Config
├── frontend/                   # React Client App
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/           # Chat Components
│   │   │   └── shared/         # Buttons, Inputs, etc.
│   │   ├── services/           # API Service Layer
│   │   ├── types/              # Shared TS Types
│   │   └── main.tsx            # Client Entry Point
│   └── .env                    # Frontend Env Config
└── pyproject.toml              # Python Project Config
```


## 🚀 Quick Start

### Prerequisites

-   Python 3.12+
-   Node.js 18+
-   PostgreSQL
-   Redis
-   Milvus (for vector storage)

### 1. Backend Setup

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies (if needed)
cd backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:main --reload
```

Backend will be available at: http://localhost:8000
API docs: http://localhost:8000/api/docs

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env if needed (default: http://localhost:8000/api/v1)

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

## 🧪 Testing

### Test Backend Refactoring

```bash
# From project root
source .venv/bin/activate
python test_refactoring.py
```

### Run Backend Tests

```bash
cd backend
pytest
```

## 📚 API Documentation

Once the backend is running, visit:

-   **Swagger UI**: http://localhost:8000/api/docs
-   **ReDoc**: http://localhost:8000/redoc

## 🔑 Key Features

### Backend

-   **Async/Await**: Modern async SQLAlchemy 2.0
-   **JWT Authentication**: Secure token-based auth with refresh tokens
-   **RAG System**: Document processing with vector embeddings
-   **LLM Integration**: Ollama (local/cloud) and OpenAI support
-   **Vector Storage**: Milvus for semantic search
-   **Document Processing**: PDF, DOCX, TXT support
-   **Weather API**: OpenWeatherMap integration

### Frontend

-   **React + TypeScript**: Type-safe frontend
-   **Automatic Token Management**: Axios interceptors handle auth
-   **Real-time Chat**: Interactive chat interface
-   **Document Management**: Upload and manage documents
-   **Collection Management**: Organize documents in collections
-   **Weather Dashboard**: Beautiful weather interface

## 🔧 Configuration

### Backend (.env)

```bash
# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530

# LLM
OLLAMA_LOCAL_URL=http://localhost:11434
OLLAMA_MODEL=phi3

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Frontend (.env)

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 📖 API Endpoints

### Authentication

-   `POST /api/v1/auth/register` - Register new user
-   `POST /api/v1/auth/login` - Login
-   `POST /api/v1/auth/refresh` - Refresh token
-   `GET /api/v1/auth/me` - Get current user

### Collections

-   `GET /api/v1/collections/` - List collections
-   `POST /api/v1/collections/` - Create collection
-   `GET /api/v1/collections/{id}` - Get collection
-   `PATCH /api/v1/collections/{id}` - Update collection
-   `DELETE /api/v1/collections/{id}` - Delete collection

### Documents

-   `POST /api/v1/documents/upload` - Upload documents
-   `GET /api/v1/documents/list` - List documents
-   `GET /api/v1/documents/{id}` - Get document
-   `DELETE /api/v1/documents/{id}` - Delete document

### Chat

-   `POST /api/v1/chat/sessions` - Create chat session
-   `GET /api/v1/chat/sessions` - List sessions
-   `POST /api/v1/chat/send` - Send message
-   `GET /api/v1/chat/sessions/{id}/messages` - Get messages

### Weather

-   `GET /api/v1/weather/current` - Get current weather
-   `GET /api/v1/weather/forecast` - Get forecast

## 🛠️ Development

### Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Code Quality

```bash
# Backend
cd backend
black .                 # Format code
ruff check .           # Lint code
mypy .                 # Type checking

# Frontend
cd frontend
npm run lint           # ESLint
npm run type-check     # TypeScript check
```

## 📄 License

GPL

## 👥 Contributors

@Arun @Rajat @Vanraj @Ramavatar

## 🔗 Links

-   [FastAPI Documentation](https://fastapi.tiangolo.com/)
-   [React Documentation](https://react.dev/)
-   [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
-   [Milvus Documentation](https://milvus.io/docs)

---

