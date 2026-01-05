from fastapi import FastAPI
from pydantic import BaseModel
import redis
import uuid
import json

app = FastAPI()

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

class TTSRequest(BaseModel):
    text: str

@app.post("/tts")
def enqueue_tts(req: TTSRequest):
    job_id = str(uuid.uuid4())

    job = {
        "job_id": job_id,
        "text": req.text
    }

    # push job to queue
    r.rpush("tts_queue", json.dumps(job))

    return {
        "status": "queued",
        "job_id": job_id
    }
