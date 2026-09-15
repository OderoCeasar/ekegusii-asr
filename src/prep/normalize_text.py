"""Ekegusii text normalization.

The one rule that matters: `ng'` is a single phoneme and the apostrophe is part of the
letter. The generic `re.sub(r"[^a-z ]", "", text)` found in every ASR tutorial destroys it.
Everything here is built around not doing that.

Owner: R6 (Audio Pipeline Engineer), to R4's (Language Lead) spec.
"""

import re
import sys
import unicodedata

# R4 confirms this set in Week 1. Letters are checked as characters, so the digraphs
# ch / ny / ng are covered by their component letters; the apostrophe is listed explicitly.
ALLOWED = set("abcegikmnorstuwy '")

# Not native to Ekegusii. Appearing = typo, or a borrowed word (hoteli, posta).
# Policy is set in TRANSCRIPTION_GUIDE rule 4.1; flip this once R4 rules.
ALLOW_BORROWED = True
BORROWED_CHARS = set("dfhjlpqvxz")

APOSTROPHES = "’‘ʼʻ´`"   # ’ ‘ ʼ ʻ ´ `
PUNCT_TO_STRIP = ".,?!:;\"()[]{}<>…“”–—/\\*_+=|~@#$%^&"

TAG_RE = re.compile(r"\[(noise|laughter|unclear|overlap)\]")


class NormalizationError(ValueError):
    """Raised when text contains characters outside the allowed set."""


def normalize(text: str, keep_tags: bool = False) -> str:
    """Normalize one transcription line to model-ready form.

    Order matters. Apostrophes are unified to ASCII and then LEFT ALONE.
    """
    # 1. Unicode NFC
    text = unicodedata.normalize("NFC", text)

    # 2. Unify apostrophe variants to ASCII -- then stop. Do NOT strip.
    for ch in APOSTROPHES:
        text = text.replace(ch, "'")

    # 3. Lowercase
    text = text.lower()

    # 4. Tags: drop or keep, before punctuation stripping eats the brackets
    if keep_tags:
        # sentinel must survive punctuation stripping below; "_" does not.
        text = TAG_RE.sub(lambda m: f"\x01{m.group(1)}\x02", text)
    else:
        text = TAG_RE.sub(" ", text)

    # 5. Strip punctuation -- note the apostrophe is NOT in PUNCT_TO_STRIP
    text = text.translate({ord(c): " " for c in PUNCT_TO_STRIP})

    if keep_tags:
        text = re.sub(r"\x01(noise|laughter|unclear|overlap)\x02", r"[\1]", text)

    # 6. Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def validate(text: str, clip_id: str = "<unknown>") -> str:
    """Raise if `text` contains characters outside the allowed set.

    Never silently drop unknown characters. An unexpected character is either a typo worth
    fixing or an orthography rule worth adding -- both are findings, not noise.
    """
    allowed = set(ALLOWED)
    if ALLOW_BORROWED:
        allowed |= BORROWED_CHARS

    stripped = TAG_RE.sub("", text)
    bad = sorted({c for c in stripped if c not in allowed})
    if bad:
        shown = ", ".join(f"{c!r} (U+{ord(c):04X})" for c in bad)
        raise NormalizationError(
            f"{clip_id}: disallowed character(s): {shown}\n  in: {text!r}"
        )
    return text


def normalize_and_validate(text: str, clip_id: str = "<unknown>", keep_tags: bool = False) -> str:
    return validate(normalize(text, keep_tags=keep_tags), clip_id)


if __name__ == "__main__":
    # Reads lines on stdin, writes normalized lines on stdout, errors on stderr.
    failures = 0
    for i, line in enumerate(sys.stdin, 1):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        try:
            print(normalize_and_validate(line, clip_id=f"line:{i}"))
        except NormalizationError as e:
            failures += 1
            print(e, file=sys.stderr)
    sys.exit(1 if failures else 0)
