import pytest
from sqlalchemy import delete

from app.db import Base, SessionLocal, engine
from app.models.interview_message import InterviewMessage
from app.models.interview_session import InterviewSession


@pytest.fixture(scope="session", autouse=True)
def create_test_tables() -> None:
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def clean_tables() -> None:
    with SessionLocal() as session:
        session.execute(delete(InterviewMessage))
        session.execute(delete(InterviewSession))
        session.commit()