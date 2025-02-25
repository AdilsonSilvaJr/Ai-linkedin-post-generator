# README.md

# LinkedIn Post Generator

A full-stack application that generates LinkedIn posts from PDF documents using AI. Built with FastAPI and React.

## 🚀 Features

- Upload PDF documents and generate engaging LinkedIn posts
- AI-powered content generation using OpenAI
- Vector store for efficient document processing
- Modern React frontend with TypeScript
- RESTful API backend with FastAPI

## 🏗️ Project Structure

```
linkedin-post-generator/
├── backend/          # FastAPI application
├── frontend/         # React + TypeScript + Vite application
└── docs/            # Project documentation
```

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.12+
- Node.js 18+
- Yarn
- Docker (optional)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Create `.env` file:
```bash
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
```

3. Start the backend:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
yarn install
yarn dev
```

## 🐳 Docker Deployment

Run the entire stack using Docker Compose:

```bash
docker-compose up --build
```

## 📝 License

MIT License