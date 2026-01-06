import torch
import os
import re
import hashlib
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
# TEXT SPLITTING (XTTS SAFE)
# --------------------------------------------------
def split_text(text, max_chars=220):
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

        if len(current) + len(s) + 1 <= max_chars:
            current = f"{current} {s}".strip()
        else:
            chunks.append(current)
            current = s

    if current:
        chunks.append(current)

    return chunks

# --------------------------------------------------
# HASH FUNCTIONS
# --------------------------------------------------
def full_text_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def chunk_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

# --------------------------------------------------
# MERGE WAV FILES
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
os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

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
# MAIN TTS FUNCTION
# --------------------------------------------------
def run_tts(text: str) -> str:
    text = normalize_text(text)

    # 1️⃣ FULL TEXT → FINAL AUDIO CACHE
    final_id = full_text_hash(text)
    final_wav = os.path.join(BASE_OUTPUT_DIR, f"final_{final_id}.wav")

    # ✅ FULL AUDIO EXISTS → RETURN
    if os.path.exists(final_wav):
        print("⚡ Using cached FINAL audio")
        return final_wav

    # 2️⃣ FINAL NOT FOUND → BUILD USING CHUNKS
    chunks = split_text(text)
    wav_files = []

    for chunk in chunks:
        chunk = chunk.strip()
        cid = chunk_hash(chunk)
        chunk_path = os.path.join(CHUNKS_DIR, f"{cid}.wav")

        # ✅ CHUNK CACHE
        if not os.path.exists(chunk_path):
            print("🎙 Generating chunk:", chunk[:40])
            tts.tts_to_file(
                text=chunk,
                speaker_wav=SPEAKER_WAV,
                language="en",
                file_path=chunk_path
            )
        else:
            print("⚡ Reusing chunk:", chunk[:40])

        wav_files.append(chunk_path)

    # 3️⃣ MERGE ONCE AND SAVE FINAL
    merge_wavs(wav_files, final_wav)
    return final_wav
