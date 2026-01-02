import torch
import os
import re
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

def normalize_text(text: str) -> str:
    # Replace dangerous unicode symbols
    text = text.replace("•", ". ")
    text = text.replace("’", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("–", "-").replace("—", "-")

    # Remove any remaining non-ascii characters
    text = text.encode("ascii", "ignore").decode()

    # Fix spacing after punctuation
    text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)

    # Collapse whitespace
    text = " ".join(text.split())

    return text




def split_text(text, max_chars=220):
    text = normalize_text(text)

    # 1️⃣ Split using natural pause points
    sentences = re.split(r'(?<=[.!?;,])\s+', text)

    chunks = []
    current = ""

    for s in sentences:
        s = s.strip()
        if not s:
            continue

        # 2️⃣ Handle very long sentence safely
        if len(s) > max_chars:
            # Save whatever came before
            if current:
                chunks.append(current)
                current = ""

            # Split long sentence by characters (last fallback)
            for i in range(0, len(s), max_chars):
                chunks.append(s[i:i + max_chars])
            continue

        # 3️⃣ Safe length check (counts space)
        extra_space = 1 if current else 0
        if len(current) + len(s) + extra_space <= max_chars:
            current = f"{current} {s}".strip()
        else:
            chunks.append(current)
            current = s

    # 4️⃣ Save leftover text
    if current:
        chunks.append(current)

    return chunks



#merging code
 #--------------------------------------------------
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
# LOAD XTTS ONCE (IMPORTANT)
# --------------------------------------------------
with torch.serialization.safe_globals(SAFE_GLOBALS):
    tts = TTS(
        model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        gpu=torch.cuda.is_available()
    )

# --------------------------------------------------
# MAIN FUNCTION (CALLED BY FASTAPI)
# --------------------------------------------------
def run_tts(text: str) -> str:
    chunks = split_text(text)
    wav_files = []

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    final_wav = os.path.join(BASE_OUTPUT_DIR, f"final_voice_{timestamp}.wav")

    for i, chunk in enumerate(chunks):
        chunk_path = os.path.join(CHUNKS_DIR, f"chunk_{timestamp}_{i}.wav")

        tts.tts_to_file(
            text=chunk,
            speaker_wav=SPEAKER_WAV,
            language="en",
            file_path=chunk_path
        )

        wav_files.append(chunk_path)

    merge_wavs(wav_files, final_wav)
    return final_wav



