import uuid
from datetime import datetime

from pydantic import BaseModel


class Application(BaseModel):
    id: str | None = str(uuid.uuid4())  # Store ObjectId as a string
    user_id: str
    job_id: str
    message_id: int
    created_at: datetime = datetime.now()
    modified_at: datetime = datetime.now()
    active: bool = True
