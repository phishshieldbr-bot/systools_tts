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

# --------------------------------------------------
# TEXT NORMALIZATION
# --------------------------------------------------

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


# --------------------------------------------------
# TEXT SPLITTING (XTTS SAFE)
# --------------------------------------------------
def split_text(text, max_chars=220):
    text = normalize_text(text)
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current = ""

    for s in sentences:
        if len(s) > max_chars:
            for i in range(0, len(s), max_chars):
                chunks.append(s[i:i + max_chars])
            continue

        if len(current) + len(s) <= max_chars:
            current = current + " " + s if current else s
        else:
            chunks.append(current)
            current = s

    if current:
        chunks.append(current)

    return chunks

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



# # if the character go above 220 sometime it split the word so i add a new logic
# import re
# # --------------------------------------------------
# # ✂️ SMART CHUNKING (MEANING AWARE)
# # --------------------------------------------------
# def smart_split_text(text: str, max_chars: int = 220):
#     text = normalize_text(text)

#     # 1️⃣ split by sentence first
#     sentences = re.split(r'(?<=[.!?])\s+', text)

#     chunks = []
#     current = ""

#     # helper: split long sentence safely
#     def split_long_sentence(sentence):
#         results = []

#         # 2️⃣ split by commas / pauses
#         parts = re.split(r'(?<=[,;:])\s+', sentence)

#         temp = ""
#         for p in parts:
#             if len(temp) + len(p) <= max_chars:
#                 temp = temp + " " + p if temp else p
#             else:
#                 results.append(temp)
#                 temp = p
#         if temp:
#             results.append(temp)

#         # 3️⃣ split by words if still long
#         final = []
#         for r in results:
#             if len(r) <= max_chars:
#                 final.append(r)
#             else:
#                 words = r.split()
#                 wtemp = ""
#                 for w in words:
#                     if len(wtemp) + len(w) <= max_chars:
#                         wtemp = wtemp + " " + w if wtemp else w
#                     else:
#                         final.append(wtemp)
#                         wtemp = w
#                 if wtemp:
#                     final.append(wtemp)

#         return final

#     # main loop
#     for s in sentences:
#         if len(s) > max_chars:
#             for part in split_long_sentence(s):
#                 chunks.append(part)
#             continue

#         if len(current) + len(s) <= max_chars:
#             current = current + " " + s if current else s
#         else:
#             chunks.append(current)
#             current = s

#     if current:
#         chunks.append(current)

#     return chunks
