from __future__ import annotations

import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

from formula_extractor import answer_from_notes, extract_formulas
from ollama_client import health
from ocr import extract_text
from pdf_generator import as_pdf, as_text

app = FastAPI(title="FormulaForge AI", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

MAX_FILES = 8
MAX_FILE_BYTES = 15 * 1024 * 1024
ALLOWED = {".pdf", ".txt", ".docx", ".png", ".jpg", ".jpeg"}
sessions: dict[str, dict] = {}


class ChatRequest(BaseModel):
    session_id: str
    question: str = Field(min_length=1, max_length=700)


class ExportRequest(BaseModel):
    session_id: str


@app.get("/api/health")
def ollama_health():
    return health()


@app.post("/api/analyze")
async def analyze(files: list[UploadFile] = File(...)):
    if not files or len(files) > MAX_FILES:
        raise HTTPException(400, f"Upload between 1 and {MAX_FILES} files.")
    extracted, file_info = [], []
    for upload in files:
        filename = upload.filename or "untitled"
        suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if suffix not in ALLOWED:
            raise HTTPException(400, f"{filename}: unsupported type.")
        contents = await upload.read()
        if len(contents) > MAX_FILE_BYTES:
            raise HTTPException(400, f"{filename}: file exceeds 15 MB.")
        try:
            text = extract_text(filename, contents)
        except Exception as error:
            raise HTTPException(422, f"Could not read {filename}: {error}") from error
        extracted.append(f"\n\n--- {filename} ---\n{text}")
        file_info.append({"name": filename, "characters": len(text)})
    notes = "".join(extracted)
    try:
        sheet = extract_formulas(notes)
    except Exception as error:
        raise HTTPException(502, f"AI extraction failed: {error}") from error
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"notes": notes, "sheet": sheet}
    return {"session_id": session_id, "files": file_info, "sheet": sheet}


@app.post("/api/chat")
def chat(request: ChatRequest):
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(404, "Session expired. Upload your notes again.")
    try:
        return {"answer": answer_from_notes(request.question, session["notes"])}
    except Exception as error:
        raise HTTPException(502, f"Chat failed: {error}") from error


@app.post("/api/download/txt")
def download_txt(request: ExportRequest):
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(404, "Session expired. Upload your notes again.")
    return Response(as_text(session["sheet"]), media_type="text/plain", headers={"Content-Disposition": "attachment; filename=formulaforge-sheet.txt"})


@app.post("/api/download/pdf")
def download_pdf(request: ExportRequest):
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(404, "Session expired. Upload your notes again.")
    return Response(as_pdf(session["sheet"]), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=formulaforge-sheet.pdf"})
