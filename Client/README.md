# SOP Workflow Generator

Production-ready full-stack web application that converts SOP documents (PDF or DOCX) into Mermaid workflow diagrams.

## Tech Stack

- Frontend: React, TypeScript, SCSS, Mermaid.js
- Backend: Python, FastAPI

## Project Structure

- `src/`: React frontend
- `backend/app/`: FastAPI backend

## Frontend Setup

```bash
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`.

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend runs on `http://localhost:8000`.

## API

### `POST /process`

- Accepts multipart form-data with a `file` field (PDF or DOCX)
- Parses text and images
- Generates workflow JSON
- Returns Mermaid diagram code

Example response:

```json
{
  "diagram": "flowchart TD\nA[Login] --> B[Open Dashboard]\nB --> C[Create Invoice]",
  "workflow": {
    "steps": [
      { "id": "A", "action": "Login" },
      { "id": "B", "action": "Open Dashboard" },
      { "id": "C", "action": "Create Invoice" }
    ]
  }
}
```
