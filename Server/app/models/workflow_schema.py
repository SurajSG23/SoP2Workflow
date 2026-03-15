from pydantic import BaseModel


class ProcessResponse(BaseModel):
    diagram: str
