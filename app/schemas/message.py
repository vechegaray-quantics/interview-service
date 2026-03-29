from pydantic import BaseModel, Field


class InterviewMessageRequest(BaseModel):
    message: str = Field(min_length=1)


class InterviewTurnResponse(BaseModel):
    assistantMessage: str
    sessionCompleted: bool