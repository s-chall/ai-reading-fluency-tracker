import tempfile

import whisper
from fastapi import FastAPI, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from scoring import score_reading

app = FastAPI(title="Reading Fluency Tracker")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_model = None


def get_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base.en")
    return _model


@app.post("/score")
async def score(audio: UploadFile, passage: str = Form(...), elapsed_seconds: float = Form(...)):
    with tempfile.NamedTemporaryFile(suffix=".webm") as tmp:
        tmp.write(await audio.read())
        tmp.flush()
        result = get_model().transcribe(tmp.name)

    transcript = result["text"].strip()
    scored = score_reading(passage, transcript, elapsed_seconds)
    scored["transcript"] = transcript
    return scored


@app.get("/health")
def health():
    return {"status": "ok"}
