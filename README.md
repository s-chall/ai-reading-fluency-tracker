# AI Reading Fluency Tracker

Record a student reading a passage aloud, transcribe it with Whisper, and
automatically score reading fluency (words correct per minute + an
addition/omission/substitution error breakdown) — the same error taxonomy
used by CBM-R / WRMT-III Oral Reading Fluency assessment.

## Stack
- **Backend**: Python, FastAPI, [openai-whisper](https://github.com/openai/whisper)
- **Frontend**: React (Vite)

## Run it

Backend:
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

Open the printed Vite URL, allow microphone access, record yourself (or a
student) reading the passage, and stop — the score and error breakdown
appear below.

## How scoring works

`backend/scoring.py` aligns the Whisper transcript against the reference
passage with a word-level diff (`difflib.SequenceMatcher`), classifying
mismatches as additions, omissions, or substitutions. From that:

- **WCPM** = words read correctly ÷ elapsed minutes
- **Passage score** = (word count − errors) ÷ elapsed seconds × 10

Run `python3 backend/scoring.py` to execute the built-in self-check.

Not implemented (out of scope for v1): self-correction, repetition, and
reversal detection — those need word-level audio timestamps, not just a
flat transcript diff.
