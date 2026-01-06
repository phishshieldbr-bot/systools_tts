import torch
import os
import re
import hashlib
from datetime import datetime
from pydub import AudioSegment
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig

# --------------------------------------------------
# SAFE GLOBALS
# --------------------------------------------------
SAFE_GLOBALS = [
    XttsConfig,
    XttsAudioConfig,
    BaseDatasetConfig,
    XttsArgs
]

# --------------------------------------------------
# TEXT NORMALIZATION
# --------------------------------------------------
def normalize_text(text: str) -> str:
    text = text.replace("•", ". ")
    text = text.replace("’", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("–", "-").replace("—", "-")
    text = text.encode("ascii", "ignore").decode()
    text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
    return " ".join(text.split())

# --------------------------------------------------
# TEXT SPLITTING
# --------------------------------------------------
def split_text(text, max_chars=220):
    text = normalize_text(text)
    sentences = re.split(r'(?<=[.!?;,])\s+', text)

    chunks, current = [], ""

    for s in sentences:
        if len(s) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            for i in range(0, len(s), max_chars):
                chunks.append(s[i:i + max_chars])
            continue

        if len(current) + len(s) + 1 <= max_chars:
            current = f"{current} {s}".strip()
        else:
            chunks.append(current)
            current = s

    if current:
        chunks.append(current)

    return chunks

# --------------------------------------------------
# HASH (TEXT ONLY)
# --------------------------------------------------
def text_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

# --------------------------------------------------
# MERGE WAVS
# --------------------------------------------------
def merge_wavs(wav_files, output_file, pause_ms=300):
    final = AudioSegment.empty()
    pause = AudioSegment.silent(duration=pause_ms)

    for f in wav_files:
        final += AudioSegment.from_wav(f) + pause

    final.export(output_file, format="wav")

# --------------------------------------------------
# PATHS
# --------------------------------------------------
BASE_OUTPUT_DIR = "output_voice"
CHUNKS_DIR = os.path.join(BASE_OUTPUT_DIR, "chunks")
os.makedirs(CHUNKS_DIR, exist_ok=True)

SPEAKER_WAV = "/home/systools/Documents/voice_cloning/male.wav"

# --------------------------------------------------
# LOAD XTTS ONCE
# --------------------------------------------------
with torch.serialization.safe_globals(SAFE_GLOBALS):
    tts = TTS(
        model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        gpu=torch.cuda.is_available()
    )

# --------------------------------------------------
# MAIN FUNCTION
# --------------------------------------------------
def run_tts(text: str) -> str:
    chunks = split_text(text)
    wav_files = []

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    final_wav = os.path.join(BASE_OUTPUT_DIR, f"final_voice_{timestamp}.wav")

    for chunk in chunks:
        chunk = chunk.strip()
        chunk_id = text_hash(chunk)
        chunk_path = os.path.join(CHUNKS_DIR, f"{chunk_id}.wav")

        # ✅ TEXT-ONLY CACHE
        if not os.path.exists(chunk_path):
            print("🎙 Generating:", chunk[:40])
            tts.tts_to_file(
                text=chunk,
                speaker_wav=SPEAKER_WAV,
                language="en",
                file_path=chunk_path
            )
        else:
            print("⚡ Using cache:", chunk[:40])

        wav_files.append(chunk_path)

    merge_wavs(wav_files, final_wav)
    return final_wav

