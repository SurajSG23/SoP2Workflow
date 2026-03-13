from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.process import router as process_router

app = FastAPI(
    title="SOP Workflow Generator API",
    version="1.0.0",
    description="Converts SOP documents into Mermaid workflow diagrams.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(process_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
