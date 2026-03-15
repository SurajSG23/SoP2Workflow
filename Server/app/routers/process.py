from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.workflow_schema import ProcessResponse
from app.services.document_parser import DocumentParserError, DocumentParserService
from app.services.workflow_generator import WorkflowGeneratorService

router = APIRouter(tags=["process"])

document_parser = DocumentParserService()
workflow_generator = WorkflowGeneratorService()


@router.post("/process", response_model=ProcessResponse)
async def process_document(file: UploadFile = File(...)) -> ProcessResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A valid filename is required.")

    extension = file.filename.lower().rsplit(".", maxsplit=1)[-1]
    if extension not in {"pdf", "docx"}:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        parsed = document_parser.parse(file.filename, content)
    except DocumentParserError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail="Document parsing failed.") from error

    diagram = workflow_generator.generate(parsed.text)

    return ProcessResponse(diagram=diagram)
