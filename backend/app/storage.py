import os
from pathlib import Path
from uuid import uuid4

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
MSG_DIR = BASE_DIR / "messages"

def ensure_dirs():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MSG_DIR.mkdir(parents=True, exist_ok=True)

def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"

def safe_filename(name: str) -> str:
    # basic safety (remove path separators)
    return name.replace("/", "_").replace("\\", "_")

def upload_path(file_id: str, filename: str) -> Path:
    return UPLOAD_DIR / f"{file_id}__{safe_filename(filename)}"

def output_path(job_id: str, filename: str) -> Path:
    return OUTPUT_DIR / f"{job_id}__{safe_filename(filename)}"
