import torch
import os
import re
from datetime import datetime
from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig

# ---------------- SAFE GLOBALS ----------------
SAFE_GLOBALS = [
    XttsConfig,
    XttsAudioConfig,
    BaseDatasetConfig,
    XttsArgs
]

# ---------------- TEXT NORMALIZATION ----------------
def normalize_text(text: str) -> str:
    text = text.replace("•", ". ")
    text = text.replace("’", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("–", "-").replace("—", "-")
    text = text.encode("ascii", "ignore").decode()
    text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
    return " ".join(text.split())

# ---------------- TEXT SPLITTING ----------------
def split_text(text, max_chars=220):
    text = normalize_text(text)
    sentences = re.split(r'(?<=[.!?;,])\s+', text)

    chunks = []
    current = ""

    for s in sentences:
        s = s.strip()
        if not s:
            continue

        if len(s) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            for i in range(0, len(s), max_chars):
                chunks.append(s[i:i + max_chars])
            continue

        extra_space = 1 if current else 0
        if len(current) + len(s) + extra_space <= max_chars:
            current = f"{current} {s}".strip()
        else:
            chunks.append(current)
            current = s

    if current:
        chunks.append(current)

    return chunks

# ---------------- PATHS ----------------
BASE_OUTPUT_DIR = "output_voice"
CHUNKS_DIR = os.path.join(BASE_OUTPUT_DIR, "chunks")
os.makedirs(CHUNKS_DIR, exist_ok=True)

SPEAKER_WAV = "/home/systools/Documents/voice_cloning/male.wav"

# ---------------- LOAD XTTS ONCE ----------------
with torch.serialization.safe_globals(SAFE_GLOBALS):
    tts = TTS(
        model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        gpu=torch.cuda.is_available()
    )

# ---------------- MULTITHREAD AUDIO LOAD ----------------
def load_wav(path):
    return AudioSegment.from_wav(path)

# ---------------- MAIN FUNCTION ----------------
def run_tts(text: str) -> str:
    # CPU work (safe)
    chunks = split_text(text)

    wav_files = []
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    final_wav = os.path.join(
        BASE_OUTPUT_DIR, f"final_voice_{timestamp}.wav"
    )

    # GPU work (SINGLE THREAD)
    for i, chunk in enumerate(chunks):
        chunk_path = os.path.join(
            CHUNKS_DIR, f"chunk_{timestamp}_{i}.wav"
        )

        tts.tts_to_file(
            text=chunk,
            speaker_wav=SPEAKER_WAV,
            language="en",
            file_path=chunk_path
        )

        wav_files.append(chunk_path)

    # I/O multithreading (SAFE)
    with ThreadPoolExecutor(max_workers=4) as executor:
        audio_segments = list(executor.map(load_wav, wav_files))

    final_audio = AudioSegment.empty()
    pause = AudioSegment.silent(duration=300)

    for seg in audio_segments:
        final_audio += seg + pause

    final_audio.export(final_wav, format="wav")
    return final_wav

