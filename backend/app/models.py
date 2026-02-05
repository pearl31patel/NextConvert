from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

JobStatus = Literal["queued", "running", "done", "failed"]

class UploadResponse(BaseModel):
    file_id: str
    filename: str
    size: int
    mime: Optional[str] = None

class ConvertRequest(BaseModel):
    file_id: str
    target_format: str  # "pdf" | "png" | "jpg" | "docx" etc.

class ConvertResponse(BaseModel):
    job_id: str

class JobResponse(BaseModel):
    status: JobStatus
    progress: Optional[int] = None
    output_filename: Optional[str] = None
    error: Optional[str] = None

class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str
