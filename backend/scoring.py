"""Oral reading fluency scoring: align a transcript against a reference
passage and derive WCPM (words correct per minute) plus an error breakdown.

Modeled on the CBM-R / WRMT-III Oral Reading Fluency scoring approach taught
in the Literacy Lab training: mark additions, omissions, and substitutions,
then score = (word count - errors) / elapsed seconds.
"""

import re
from difflib import SequenceMatcher

WORD_RE = re.compile(r"[^\w']")


def normalize(word: str) -> str:
    return WORD_RE.sub("", word).lower()


def tokenize(text: str) -> list[str]:
    return [normalize(w) for w in text.split() if normalize(w)]


def score_reading(reference_text: str, transcript_text: str, elapsed_seconds: float | None) -> dict:
    ref_words = tokenize(reference_text)
    hyp_words = tokenize(transcript_text)

    matcher = SequenceMatcher(None, ref_words, hyp_words, autojunk=False)
    correct = 0
    errors = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            correct += i2 - i1
        elif tag == "delete":
            errors += [{"type": "omission", "word": w} for w in ref_words[i1:i2]]
        elif tag == "insert":
            errors += [{"type": "addition", "word": w} for w in hyp_words[j1:j2]]
        elif tag == "replace":
            ref_chunk, hyp_chunk = ref_words[i1:i2], hyp_words[j1:j2]
            for k in range(max(len(ref_chunk), len(hyp_chunk))):
                r = ref_chunk[k] if k < len(ref_chunk) else None
                h = hyp_chunk[k] if k < len(hyp_chunk) else None
                if r is None:
                    errors.append({"type": "addition", "word": h})
                elif h is None:
                    errors.append({"type": "omission", "word": r})
                else:
                    errors.append({"type": "substitution", "word": h, "expected": r})

    word_count = len(ref_words)
    error_count = len(errors)
    minutes = elapsed_seconds / 60 if elapsed_seconds else None

    return {
        "word_count": word_count,
        "words_correct": correct,
        "error_count": error_count,
        "errors": errors,
        "elapsed_seconds": elapsed_seconds,
        "wcpm": round(correct / minutes, 1) if minutes else None,
        "passage_score": round((word_count - error_count) / elapsed_seconds * 10, 1) if elapsed_seconds else None,
    }


# ponytail: no self-correction/repetition/reversal detection — flat transcript
# diff can't see mid-utterance corrections. Add if word-level timestamps come in.


def _demo():
    reference = "The cat sat on the mat and looked at the big yellow dog"
    transcript = "the cat sit on the mat and the big yellow dog ran"
    result = score_reading(reference, transcript, elapsed_seconds=30)

    assert result["word_count"] == 13
    assert result["words_correct"] == 10, result
    assert result["error_count"] == 4, result
    assert {"type": "omission", "word": "looked"} in result["errors"]
    assert {"type": "omission", "word": "at"} in result["errors"]
    assert {"type": "substitution", "word": "sit", "expected": "sat"} in result["errors"]
    assert {"type": "addition", "word": "ran"} in result["errors"]
    assert result["wcpm"] == 20.0
    assert result["passage_score"] == 3.0

    perfect = score_reading("one two three", "one two three", elapsed_seconds=6)
    assert perfect["error_count"] == 0
    assert perfect["wcpm"] == 30.0

    print("scoring.py: all checks passed")


if __name__ == "__main__":
    _demo()
