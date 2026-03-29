from pydantic import BaseModel, Field


class StartInterviewRequest(BaseModel):
    inviteToken: str = Field(min_length=4)


class InterviewSessionResponse(BaseModel):
    sessionId: str
    campaignId: str
    campaignName: str
    assistantMessage: str
    sessionCompleted: bool