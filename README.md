# FormulaForge AI

FormulaForge AI turns typed, scanned, and handwritten study notes into a clean, topic-wise formula sheet. It uses FastAPI, React, Tailwind CSS, EasyOCR, and a local Ollama model.

The application is deliberately isolated in this folder. It does not use or modify the existing `formula-sheet-generator` folder.

## What it supports

- Upload up to 8 PDF, TXT, DOCX, PNG, or JPG files (15 MB each)
- Extract typed PDF/DOCX/TXT content and OCR handwritten images or scanned PDFs
- Extract, deduplicate, organize, and prioritize formulas with Ollama
- Ask questions grounded only in the uploaded note context
- Download polished topic-wise PDF or TXT formula sheets
- Switch between light and dark themes

## Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer
- [Ollama](https://ollama.com) installed and running

FormulaForge defaults to `gpt-oss:120b-cloud`, as requested. Change it with the `OLLAMA_MODEL` environment variable if your local Ollama uses a different model.

## Start Ollama

Open a separate PowerShell window and run:

```powershell
ollama serve
```

Then, in another PowerShell window, make the model available:

```powershell
ollama pull gpt-oss:120b-cloud
```

Check that Ollama is working:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

Keep the `ollama serve` window open while FormulaForge is running. If Ollama has been installed as a background application already, it may start automatically and `ollama serve` can report that the port is already in use; that means it is already running.

## Backend setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API is available at `http://localhost:8000`. Confirm the model connection at `http://localhost:8000/api/health`.

## Frontend setup

Open another PowerShell window:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL Vite prints, usually `http://localhost:5173`.

## Optional model override

Set it before starting the backend:

```powershell
$env:OLLAMA_MODEL = "qwen2.5:3b"
uvicorn main:app --reload --port 8000
```

## Example questions

- `Show integration formulas`
- `Explain Ohm's law`
- `Which formulas are used in thermodynamics?`
- `List formulas involving acceleration`

## API routes

- `GET /api/health` checks whether Ollama is online and lists installed models
- `POST /api/analyze` accepts multipart `files` and returns the structured formula sheet
- `POST /api/chat` answers from the current upload session only
- `POST /api/download/pdf` produces a formatted PDF
- `POST /api/download/txt` produces a plain-text formula sheet

## Notes

EasyOCR downloads its language model files the first time handwritten content is processed, so the first OCR request may take longer. Uploaded note text and generated sheets are held only in backend memory for the active session and disappear when the backend restarts.
