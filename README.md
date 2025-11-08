# Agentic Model Training Platform

An autonomous AI system that takes raw data and problem descriptions, then automatically develops, trains, and deploys machine learning models using Google's Gemini and Vertex AI.

## 🎯 Hackathon Version

This is a simplified version focused on core ML pipeline functionality:
- ✅ Automated problem analysis
- ✅ Data processing and labeling
- ✅ Model selection and training
- ✅ Real-time progress tracking
- ✅ Model deployment and testing
- ❌ Authentication (removed for simplicity)
- ❌ Advanced security features
- ❌ Production deployment configs

## 🏗️ Project Structure

```
.
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Config and core utilities
│   │   ├── schemas/        # Pydantic data models
│   │   ├── services/       # Business logic
│   │   │   ├── agent/      # AI agent components
│   │   │   └── cloud/      # GCP integrations
│   │   └── utils/          # Helper utilities
│   ├── tests/              # Backend tests
│   └── pyproject.toml      # Python dependencies
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # API client
│   │   └── contexts/       # React contexts
│   └── package.json        # Node dependencies
│
├── docs/                   # Documentation
│   └── guides/             # Setup guides
│
└── docker-compose.yml      # Local development setup
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Google Cloud account with billing enabled

### 1. Google Cloud Setup

Follow the detailed guide: [docs/guides/google-cloud-setup.md](docs/guides/google-cloud-setup.md)

Quick version:
```bash
# Enable required APIs
gcloud services enable aiplatform.googleapis.com storage.googleapis.com

# Create service account and download key
gcloud iam service-accounts create agentic-platform-sa
gcloud iam service-accounts keys create gcp-key.json \
  --iam-account=agentic-platform-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Move key to credentials directory
mkdir -p gcp-credentials
mv gcp-key.json gcp-credentials/
```

### 2. Environment Configuration

```bash
# Copy example env file
cp .env.example .env

# Edit .env and update:
# - GOOGLE_CLOUD_PROJECT
# - GCS_BUCKET_NAME
# - GEMINI_API_KEY
```

### 3. Start Development Environment

```bash
# Start all services
docker-compose up

# Backend will be available at http://localhost:8000
# Frontend will be available at http://localhost:3000
```

### 4. Install Backend Dependencies

```bash
cd backend
poetry install
```

## 🛠️ Development

### Backend

```bash
cd backend

# Install dependencies
poetry install

# Run development server
poetry run uvicorn app.main:app --reload

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run ruff check .
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

## 📋 Implementation Status

See [.kiro/specs/agentic-model-training-platform/tasks.md](.kiro/specs/agentic-model-training-platform/tasks.md) for detailed task list.

**Completed:**
- ✅ Project infrastructure setup
- ✅ Docker configurations
- ✅ Environment configuration
- ✅ GCS storage structure

**In Progress:**
- 🔄 GCS storage manager and Pydantic schemas
- 🔄 Core agent components
- 🔄 API endpoints
- 🔄 Frontend UI

## 🎯 Core Features

1. **Automated Problem Analysis**: Upload data and describe your problem - the system analyzes and determines the best ML approach
2. **Smart Data Processing**: Automatic data validation, cleaning, and feature engineering
3. **Intelligent Labeling**: Zero-shot labeling for unlabeled datasets using Gemini
4. **Model Selection**: AI-powered model architecture and hyperparameter recommendations
5. **Automated Training**: Hands-off training on Vertex AI with progress monitoring
6. **Real-time Updates**: WebSocket-based live progress tracking
7. **Easy Deployment**: One-click model deployment with API endpoints
8. **Interactive Testing**: Test your models directly in the UI

## 🔧 Tech Stack

**Backend:**
- FastAPI (Python web framework)
- Google Cloud Storage (Metadata and file storage)
- Celery + Redis (Task queue)
- Google Vertex AI (Model training)
- Google Gemini (AI agent)
- Pydantic (Data validation)

**Frontend:**
- React 18 + TypeScript
- Material-UI (Components)
- React Query (Data fetching)
- React Router (Routing)
- Vite (Build tool)

**Infrastructure:**
- Docker + Docker Compose
- Google Cloud Storage
- Google Cloud Logging

## 📝 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🐛 Troubleshooting

### Service Connection Issues
```bash
# Check if services are running
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs redis
```

### GCP Authentication Issues
```bash
# Verify credentials file exists
ls -la gcp-credentials/gcp-key.json

# Test authentication
gcloud auth activate-service-account --key-file=gcp-credentials/gcp-key.json
```

### Port Already in Use
```bash
# Stop all containers
docker-compose down

# Check what's using the port
lsof -i :8000  # or :3000 for frontend
```

## 📚 Additional Resources

- [Google Cloud Setup Guide](docs/guides/google-cloud-setup.md)
- [Design Document](.kiro/specs/agentic-model-training-platform/design.md)
- [Requirements Document](.kiro/specs/agentic-model-training-platform/requirements.md)

## 🤝 Contributing

This is a hackathon project. Feel free to fork and experiment!

## 📄 License

MIT License - feel free to use this for your own projects.
