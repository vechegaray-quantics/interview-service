from typing import Any

from pydantic import BaseModel


class FinalizeInterviewRequest(BaseModel):
    includeTranscript: bool = False


class FinalizeInterviewResponse(BaseModel):
    report: dict[str, Any]