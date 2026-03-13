from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.workflow_schema import ProcessResponse
from app.services.diagram_generator import DiagramGeneratorService
from app.services.document_parser import DocumentParserError, DocumentParserService
from app.services.vision_processor import VisionProcessorService
from app.services.workflow_generator import WorkflowGeneratorService

router = APIRouter(tags=["process"])

document_parser = DocumentParserService()
vision_processor = VisionProcessorService()
workflow_generator = WorkflowGeneratorService()
diagram_generator = DiagramGeneratorService()


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
        parsed_document = document_parser.parse(file.filename, content)
    except DocumentParserError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail="Document parsing failed.") from error

    image_descriptions = vision_processor.describe_images(parsed_document.images)
    workflow_data = workflow_generator.generate(parsed_document.text, image_descriptions)
    diagram = diagram_generator.generate_mermaid(workflow_data)

    return ProcessResponse(diagram=diagram, workflow=workflow_data)
