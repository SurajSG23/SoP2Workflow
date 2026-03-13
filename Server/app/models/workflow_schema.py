from pydantic import BaseModel, Field


class WorkflowStep(BaseModel):
    id: str = Field(..., description="Unique node identifier used in Mermaid")
    action: str = Field(..., description="Human-readable action for this workflow step")


class WorkflowData(BaseModel):
    steps: list[WorkflowStep] = Field(default_factory=list)


class ProcessResponse(BaseModel):
    diagram: str
    workflow: WorkflowData
