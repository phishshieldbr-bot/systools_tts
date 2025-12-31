from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import importlib

from extractor import extract_from_html

tts_engine = importlib.import_module("tts_engine")

app = FastAPI(title="Webpage → XTTS API")

# -----------------------------
# 🌍 CORS (browser safe)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# 🏠 Health check
# -----------------------------
@app.get("/")
def home():
    return {"status": "Webpage TTS API running"}

# -----------------------------
# 📦 Request schema
# -----------------------------
class HTMLPayload(BaseModel):
    html: str

# -----------------------------
# 🎤 HTML → BODY → XTTS
# -----------------------------
@app.post("/page-tts")
def page_tts(data: HTMLPayload):

    title, body = extract_from_html(data.html)

    if not body.strip():
        raise HTTPException(status_code=400, detail="No readable text found")

    audio_path = tts_engine.run_tts(body)

    if not os.path.exists(audio_path):
        raise HTTPException(status_code=500, detail="Audio generation failed")

    return FileResponse(
        audio_path,
        media_type="audio/wav",
        filename="page_audio.wav"
    )

# -----------------------------
# 📜 JS SERVED DYNAMICALLY
# -----------------------------
@app.get("/pageTTS.js")
def serve_page_tts_js():

    js_code = """
    (function () {

        let audio = null;
        let audioUrl = null;

        async function generateAndPlay() {
            const html = document.documentElement.outerHTML;

            try {
                const response = await fetch("http://127.0.0.1:8081/page-tts", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ html })
                });

                if (!response.ok) {
                    throw new Error("TTS API failed");
                }

                const blob = await response.blob();
                audioUrl = URL.createObjectURL(blob);

                audio = new Audio(audioUrl);
                audio.play();

            } catch (err) {
                console.error("TTS error:", err);
            }
        }

        function pauseAudio() {
            if (audio && !audio.paused) {
                audio.pause();
            }
        }

        function playAudio() {
            if (audio) {
                audio.play();
            } else {
                generateAndPlay();
            }
        }

        function stopAudio() {
            if (audio) {
                audio.pause();
                audio.currentTime = 0;
            }
        }

        // ----------------------------
        // 🎛️ UI BUTTONS
        // ----------------------------
     function createControls() {
    const container = document.createElement("div");
    container.style.position = "fixed";
    container.style.bottom = "20px";
    container.style.right = "20px";
    container.style.zIndex = "9999";
    container.style.background = "#111";
    container.style.padding = "10px";
    container.style.borderRadius = "8px";

    // 🔒 IMPORTANT: prevent TTS from reading UI
    container.setAttribute("data-tts-ignore", "true");

    const playBtn = document.createElement("button");
    playBtn.innerText = "▶ Play";
    playBtn.onclick = playAudio;
    playBtn.setAttribute("data-tts-ignore", "true");

    const pauseBtn = document.createElement("button");
    pauseBtn.innerText = "⏸ Pause";
    pauseBtn.onclick = pauseAudio;
    pauseBtn.setAttribute("data-tts-ignore", "true");

    const stopBtn = document.createElement("button");
    stopBtn.innerText = "⏹ Stop";
    stopBtn.onclick = stopAudio;
    stopBtn.setAttribute("data-tts-ignore", "true");

    [playBtn, pauseBtn, stopBtn].forEach(btn => {
        btn.style.margin = "5px";
        btn.style.padding = "6px 10px";
        btn.style.cursor = "pointer";
    });

    container.appendChild(playBtn);
    container.appendChild(pauseBtn);
    container.appendChild(stopBtn);

    document.body.appendChild(container);
}


        window.addEventListener("DOMContentLoaded", createControls);

    })();
    """

    return Response(js_code, media_type="application/javascript")
