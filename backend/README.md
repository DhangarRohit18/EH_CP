# WebGuard Backend Services

This subfolder houses the dual backend engines for WebGuard:
1. **Python FastAPI Backend** (`backend/app/`): Implements the Isolation Forest anomaly detector, NLP phrase similarity scorer, and SQLAlchemy database persistence.
2. **Node.js Express Full-Stack Server** (`backend/server.ts`): Provides dev-server mounting with Vite middleware and serving the built frontend.

---

## 🐍 1. Running Python FastAPI Backend

### Prerequisites
- Python 3.10+
- `pip`

### Setup and Start
```bash
# From workspace root or inside backend/
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server on port 8000
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive Swagger documentation is available at:
`http://localhost:8000/docs`

---

## ⚡ 2. Running Node.js Express Server

### From Root Directory:
```bash
# Starts Express server on port 3000 mounting the Vite frontend
npm run dev
# or explicitly
npm run dev:backend
```

Endpoints exposed:
- `GET http://localhost:3000/api/v1/health`
- `POST http://localhost:3000/api/v1/analyze`
- `GET http://localhost:3000/api/v1/history`

---

## 🐳 3. Running with Docker

```bash
# Build and run backend container with PostgreSQL database
docker compose up --build
```
