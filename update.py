import torch
import os
import re
from datetime import datetime
from queue import Queue
from threading import Thread
from pydub import AudioSegment
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
os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

SPEAKER_WAV = "/home/systools/Documents/voice_cloning/male.wav"

# ---------------- LOAD XTTS ONCE ----------------
with torch.serialization.safe_globals(SAFE_GLOBALS):
    tts = TTS(
        model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        gpu=torch.cuda.is_available()
    )

# ---------------- TENSOR → AUDIOSEGMENT ----------------
def tensor_to_audiosegment(audio_tensor, sr=24000):
    if audio_tensor.dim() == 2:
        audio_tensor = audio_tensor.squeeze(0)

    pcm = (
        audio_tensor
        .clamp(-1, 1)
        .mul(32767)
        .short()
        .cpu()
        .numpy()
    )

    return AudioSegment(
        data=pcm.tobytes(),
        sample_width=2,
        frame_rate=sr,
        channels=1
    )

# ---------------- MAIN FUNCTION ----------------
def run_tts(text: str) -> str:
    # -------- CPU WORK --------
    chunks = split_text(text)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    final_wav = os.path.join(
        BASE_OUTPUT_DIR, f"final_voice_{timestamp}.wav"
    )

    queue = Queue(maxsize=4)
    pause = AudioSegment.silent(duration=300)

    # -------- GPU PRODUCER --------
    def producer():
        with torch.no_grad():
            for chunk in chunks:
                audio = tts.tts(
                    text=chunk,
                    speaker_wav=SPEAKER_WAV,
                    language="en"
                )
                queue.put(audio.cpu())
        queue.put(None)  # stop signal

    # -------- CPU CONSUMER --------
    def consumer():
        final_audio = AudioSegment.empty()

        while True:
            audio = queue.get()
            if audio is None:
                break

            segment = tensor_to_audiosegment(audio)
            final_audio += segment + pause

        # ✅ DISK WRITE ONLY ONCE
        final_audio.export(final_wav, format="wav")

    # -------- START PIPELINE --------
    t1 = Thread(target=producer)
    t2 = Thread(target=consumer)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    return final_wav
