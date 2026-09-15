# Transcription Guide — Ekegusii ASR

**Owner:** R4 (Language & Orthography Lead). Every ruling R4 makes becomes a numbered rule here,
with a real example from our data. The guide only grows; rules are never deleted, only superseded.

**Version:** 0.1 (draft — R4 to confirm everything below in Week 1)

---

## 1. Character set

Allowed characters (R4: CONFIRM against standard Ekegusii orthography before Week 2):

```
a b ch e g i k m n ng ng' ny o r s t u w y   +   space   +   apostrophe '
```

**1.1** `ng'` is ONE sound (velar nasal). The apostrophe is part of the letter. Never omit it,
never substitute a plain `ng`. `omong'ina` and `omongina` are not the same word.

**1.2** Use the straight ASCII apostrophe `'` (U+0027). Not `’`, not `` ` ``. The preprocessing
script converts curly ones automatically, but type straight ones.

**1.3** Ekegusii has no native `p d f h j l q v x z`. If you typed one, either it is a typo or it is
a borrowed word (`hoteli`, `posta`, `pikipiki`). See rule 4.1.

## 2. Casing and punctuation

**2.1** Write everything in **lowercase**.
**2.2** No sentence punctuation: no `. , ? ! : ;` — the model does not predict it and inconsistent
punctuation hurts training. The apostrophe in `ng'` is not punctuation (rule 1.1) and stays.
**2.3** Hyphens: _R4 to rule. Draft: do not use them._

## 3. Numbers

**3.1** Write numbers as **spoken**, never as digits. "2019" → the words actually said.
**3.2** _R4: supply the number words 1–20, tens, hundreds, thousands, and the year convention._

## 4. Code-switching

**4.1** Swahili and English words are written **as spoken**, in their normal spelling, lowercase.
Do not translate them into Ekegusii. Do not omit them.
**4.2** Tag the clip as mixed in the manifest (`style` stays as-is; add `code_switch: true`).

## 5. Disfluency and non-speech

**5.1** False starts and repetitions are **transcribed** — they are real speech.
  _"nigo ngo- ngocha"_ → write it as said.
**5.2** Hesitation sounds: _R4 to rule on spelling. Draft: `ee`, `mm`._
**5.3** Tags, written in square brackets, lowercase:

| Tag | Use when |
|-----|----------|
| `[noise]` | background noise obscures part of the clip |
| `[laughter]` | speaker laughs |
| `[unclear]` | you genuinely cannot make out a word after three listens |
| `[overlap]` | another speaker talks over this one |

**5.4** If more than ~20% of a clip is `[unclear]`, **discard the clip** instead of transcribing it.
Mark it rejected rather than guessing. A guessed label is worse than no label.

## 6. When you are unsure

Do not guess and do not invent a convention. Post the clip ID in the transcription channel and tag R4.
R4's answer becomes a numbered rule here. If the same question comes up twice, the guide has a gap —
that is a bug in the guide, not in you.

---

## Changelog

| Date | Rule | Change | Ruled by |
|------|------|--------|----------|
| _tbd_ | — | initial draft | R1 |
