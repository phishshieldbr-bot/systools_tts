import redis
import json
from tts_engine import run_tts

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

print("🎧 TTS Worker started...")

while True:
    _, job_data = r.blpop("tts_queue")   # blpo means take from  que
    job = json.loads(job_data)

    job_id = job["job_id"]
    text = job["text"]

    print(f"🔊 Processing job {job_id}")

    try:
        output_path = run_tts(text)

        r.hset(
            f"tts_result:{job_id}",
            mapping={
                "status": "done",
                "output": output_path
            }
        )

    except Exception as e:
        r.hset(
            f"tts_result:{job_id}",
            mapping={
                "status": "error",
                "message": str(e)
            }
        )

