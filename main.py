from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import importlib

from extractor import extract_from_html


tts_engine = importlib.import_module("asytts_engine")

app = FastAPI(title="Webpage → XTTS MP3 API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return {"status": "Webpage TTS API running"}

# -------------------------------------------------
# 📦 Request schema
# -------------------------------------------------
class HTMLPayload(BaseModel):
    html: str

# -------------------------------------------------
# 🎤 HTML → BODY → XTTS → MP3
# -------------------------------------------------
@app.post("/page-tts")
async def page_tts(data: HTMLPayload, background: BackgroundTasks):

    # Extract readable text
    title, body = extract_from_html(data.html)

    if not body.strip():
        raise HTTPException(status_code=400, detail="No readable text found")

    # Generate MP3 using XTTS
    audio_path = tts_engine.run_tts(body)

    if not audio_path or not os.path.exists(audio_path):
        raise HTTPException(status_code=500, detail="Audio generation failed")

    # Auto-delete file after response
    background.add_task(os.remove, audio_path)

    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename="page_audio.mp3"
    )
