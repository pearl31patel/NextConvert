from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import mimetypes
import time
from typing import Dict, Any

from .models import UploadResponse, ConvertRequest, ConvertResponse, JobResponse, ContactRequest
from .storage import ensure_dirs, new_id, upload_path, output_path, MSG_DIR
from .converters import convert_file

app = FastAPI(title="Universal Converter Backend")

# CORS (frontend is Vite default)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ensure_dirs()

# In-memory stores (MVP)
FILES: Dict[str, Dict[str, Any]] = {}
JOBS: Dict[str, Dict[str, Any]] = {}

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    file_id = new_id("file")
    filename = file.filename or "uploaded"
    save_path = upload_path(file_id, filename)

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    # basic size limit (25MB)
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 25MB for MVP)")

    save_path.write_bytes(content)

    FILES[file_id] = {
        "file_id": file_id,
        "filename": filename,
        "path": str(save_path),
        "size": len(content),
        "mime": file.content_type,
        "created_at": time.time(),
    }

    return UploadResponse(
        file_id=file_id,
        filename=filename,
        size=len(content),
        mime=file.content_type,
    )

def run_job(job_id: str):
    # background conversion
    job = JOBS[job_id]
    job["status"] = "running"
    job["progress"] = 25

    try:
        file_id = job["file_id"]
        target_format = job["target_format"]
        file_meta = FILES.get(file_id)
        if not file_meta:
            raise ValueError("Uploaded file not found")

        inp = Path(file_meta["path"])
        base_name = Path(file_meta["filename"]).stem

        # output file name
        out_name = f"{base_name}.{target_format.lower()}"
        out_path = output_path(job_id, out_name)

        job["progress"] = 60
        output_filename, _mime = convert_file(inp, target_format, out_path)

        job["progress"] = 100
        job["status"] = "done"
        job["output_filename"] = output_filename
        job["output_path"] = str(out_path)

    except Exception as e:
        job["status"] = "failed"
        job["error"] = str(e)

@app.post("/convert", response_model=ConvertResponse)
def convert(req: ConvertRequest, background: BackgroundTasks):
    # validate file id exists
    if req.file_id not in FILES:
        raise HTTPException(status_code=404, detail="file_id not found")

    job_id = new_id("job")
    JOBS[job_id] = {
        "job_id": job_id,
        "file_id": req.file_id,
        "target_format": req.target_format,
        "status": "queued",
        "progress": 5,
        "created_at": time.time(),
    }

    background.add_task(run_job, job_id)
    return ConvertResponse(job_id=job_id)

@app.get("/job/{job_id}", response_model=JobResponse)
def job_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_id not found")

    return JobResponse(
        status=job["status"],
        progress=job.get("progress"),
        output_filename=job.get("output_filename"),
        error=job.get("error"),
    )

@app.get("/download/{job_id}")
def download(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_id not found")
    if job.get("status") != "done":
        raise HTTPException(status_code=400, detail="Job not complete")

    out_path = Path(job["output_path"])
    if not out_path.exists():
        raise HTTPException(status_code=404, detail="Output file missing")

    mime, _ = mimetypes.guess_type(str(out_path))
    return FileResponse(
        path=str(out_path),
        media_type=mime or "application/octet-stream",
        filename=out_path.name,
    )

@app.post("/contact")
def contact(req: ContactRequest):
    # MVP: save message to local file
    ts = int(time.time())
    msg_file = MSG_DIR / f"message_{ts}.txt"
    msg_file.write_text(
        f"Name: {req.name}\nEmail: {req.email}\n\nMessage:\n{req.message}\n",
        encoding="utf-8",
    )
    return {"status": "sent"}
