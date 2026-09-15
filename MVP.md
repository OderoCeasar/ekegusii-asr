# MVP — what we actually build, in what order

The 12-week plan in `README.md` is the *ambition*. This file is the **scope**: the smallest thing
that counts as a working project, what we add on top if time allows, and what we deliberately refuse
to build.

**Rule for the whole project: get a thin slice working end to end before making any part of it good.**
A bad model that runs from microphone to text in Week 4 is worth far more than a great preprocessing
pipeline with nothing attached to it in Week 9. Every feature below is ordered by that principle.

---

## What "MVP" means here

> **A person speaks Ekegusii into a web page, and text comes out — with an honest accuracy number
> attached to it.**

That is the whole bar. It does not have to be accurate. It has to be **real, measured, and
reproducible**. If we have that by Week 4, everything after it is improvement rather than rescue.

---

## Release ladder

| Release | Target | Data | What it proves | Status |
|---------|--------|------|----------------|--------|
| **v0.0 Skeleton** | Week 2 | 10 minutes | The chain runs. Nothing is good yet. | in progress |
| **v0.1 MVP** | Week 4 | ≥2 h, ≥3 speakers | We have a real Ekegusii recognizer and a real WER | — |
| **v0.2 Usable** | Week 7 | ≥8 h, ≥10 speakers | It handles voices it has never heard, including conversation | — |
| **v1.0 Defensible** | Week 11 | ≥15 h, ≥15 speakers | Published dataset + model + analysis that survives questioning | — |

**If we only ever reach v0.1, we still have a complete, submittable project.** Everything past it
raises the grade; nothing past it is required for the project to exist. Plan for v1.0, protect v0.1.

---

## Tier 0 — Walking skeleton (Week 1–2)

Purpose: prove every link in the chain works *before* real data exists. Use ten minutes of any
audio in any language. Quality is irrelevant here; connectivity is everything.

| ID | Feature | Owner | Effort | Done when |
|----|---------|-------|--------|-----------|
| **F0.1** | Repo + environment | R1 | 0.5 d | `pip install -r requirements.txt` succeeds; every member has cloned the repo |
| **F0.2** | Text normalizer + character validator | R6 | 1 d | ✅ **built** — `src/prep/normalize_text.py`; `ng'` survives; unknown chars raise |
| **F0.3** | Manifest schema + validator | R6 | 1 d | ✅ **built** — `scripts/validate_manifests.py`; exits 1 on speaker leakage |
| **F0.4** | Kaggle GPU notebook runs | R8 | 0.5 d | XLS-R-300m loads on a free GPU without OOM |
| **F0.5** | Deliberate overfit on 10 clips | R8 | 1 d | WER → near 0 on those 10 clips. Proves loader + CTC head + metric all work. |
| **F0.6** | Checkpoint + resume to HF Hub | R8 | 0.5 d | Kill the session mid-run; resume from checkpoint with one flag |
| **F0.7** | Eval harness on dummy predictions | R10 | 1 d | Feed it fake predictions, get WER/CER out |

**Gate:** nobody moves to Tier 1 until F0.5 passes. An overfit run that *won't* converge means
something in the pipeline is broken, and finding that now costs a day — finding it in Week 6 costs a week.

---

## Tier 1 — MVP v0.1 (Week 2–4) · **must have**

The smallest real recognizer. **Uses found audio only — no recording drive, no hand transcription.**
That is deliberate: it removes every human-scheduling dependency from the critical path.

| ID | Feature | Owner | Effort | Done when |
|----|---------|-------|--------|-----------|
| **F1.1** | Audio ingest script | R2 | 1 d | `scripts/ingest.sh <url>` → 16 kHz mono WAV in `data/raw/` |
| **F1.2** | Source log discipline | R2 | ongoing | Every file has a row in `data/SOURCES.md` with its licence |
| **F1.3** | VAD segmentation | R6 | 1.5 d | Long WAV → 3–15 s clips cut at silence, not mid-word |
| **F1.4** | Audio cleanup | R6 | 1 d | Resample, loudness-normalize, reject clipped/silent/music clips with a logged reason |
| **F1.5** | **Forced alignment** | R7 | 3 d | One long recording + its text → labelled clips. **The core feature of the MVP.** |
| **F1.6** | Alignment QA loop | R7+R4 | 0.5 d | 20 random clips checked by a fluent speaker; ≥90% pass or batch rejected |
| **F1.7** | Dataset builder | R7 | 1.5 d | `scripts/build_dataset.sh` → `train/dev/test.jsonl`, speaker-disjoint, validator passes |
| **F1.8** | **Fine-tune XLS-R-300m + CTC** | R8 | 2 d | Training runs to completion on Kaggle; checkpoint on the Hub |
| **F1.9** | Greedy decode + WER/CER | R10 | 1 d | A real number on a held-out speaker, logged in `reports/experiments.md` |
| **F1.10** | **Gradio demo** | R10 | 1 d | Public HF Space: record button → transcript |

**v0.1 acceptance:** ≥2 hours of aligned audio · ≥3 distinct speakers · a WER number on a speaker the
model never saw · a demo URL a stranger can open.

> At this point the project is **done in principle**. Everything below makes it better.

---

## Tier 2 — v0.2 Usable (Week 5–7) · **should have**

Now we attack the two things that make v0.1 fragile: too little data, and all of it read speech.

| ID | Feature | Owner | Effort | Done when |
|----|---------|-------|--------|-----------|
| **F2.1** | Consent form + recording protocol | R3 | 1 d | Approved, and every recorder has been briefed once |
| **F2.2** | **Read-aloud pipeline** | R3+R2 | 2 d | Found text → prompt sheets → people read them → paired data at ~2–3 min of effort per minute of audio. **Cheapest way to create new pairs.** |
| **F2.3** | Recording drive #1 | R3 | 3 d | ≥5 new speakers, ≥20 min each, consent filed |
| **F2.4** | **Correction UI** | R5 | 2 d | Gradio app, works on a phone: plays clip, shows the model's draft, saves the human's fix |
| **F2.5** | Model-in-the-loop pre-fill | R5+R8 | 1 d | Draft transcripts come from our own v0.1 model; model-vs-human delta is logged |
| **F2.6** | Spontaneous speech capture | R3 | 2 d | ≥25% of the corpus is unscripted talk, not reading |
| **F2.7** | Augmentation | R8 | 1 d | Speed perturb ×0.9/1.0/1.1 + noise, **train split only** |
| **F2.8** | Re-align with our own model | R7 | 1 d | Our Ekegusii model beats the generic aligner; batch QA re-run |
| **F2.9** | Backbone comparison | R8 | 2 d | XLS-R-300m vs MMS-1b vs w2v-BERT, decision written down |

**v0.2 acceptance:** ≥8 hours · ≥10 speakers · ≥25% spontaneous · v0.2 WER beats v0.1 on the same dev set.

---

## Tier 3 — v1.0 Defensible (Week 8–11) · **should have, in this order**

These are the features that turn "we trained a model" into "we have a result." Cheap, high-value,
and what examiners actually probe.

| ID | Feature | Owner | Effort | Why it earns marks |
|----|---------|-------|--------|--------------------|
| **F3.1** | **KenLM + beam decoding** | R9 | 2 d | 5–15 WER points for zero GPU. Best value in the project. |
| **F3.2** | Text corpus ≥1M words | R9+R2 | ongoing | Feeds F3.1. Text-only — can start Week 1, blocks nobody. |
| **F3.3** | Full eval breakdowns | R10 | 1.5 d | WER by style, gender, age, dialect, source, duration. A single average hides everything. |
| **F3.4** | **Learning curve** | R9 | 1.5 d | Train on 1/2/5/10/all hours, plot WER vs hours. Answers "how much more data?" — the question everyone asks. |
| **F3.5** | Error analysis, 50 worst clips | R10+R4 | 1.5 d | ~⅓ turn out to be *label* errors. Finding them fixes corpus and model at once. |
| **F3.6** | `test-hard` set | R10 | 0.5 d | Noisy, fast, code-switched. Scores badly on purpose — knowing your weaknesses scores well. |
| **F3.7** | Model card + dataset card | R10 | 1 d | With an honest limitations section. This is what makes it research, not homework. |
| **F3.8** | Publish to HF Hub | R7 | 0.5 d | Dataset (or reproducible recipe for non-redistributable parts) + model, public |

---

## Tier 4 — Nice to have · **only if Tier 3 is fully done**

| ID | Feature | Value |
|----|---------|-------|
| F4.1 | Whisper-small comparison | CTC vs seq2seq; document where Whisper hallucinates |
| F4.2 | From-scratch CNN baseline (conv → BiGRU → CTC) | Will score ~80–95% WER. Plotted next to the fine-tuned model, it *quantifies* what pretraining bought us — a strong report figure |
| F4.3 | Dialect-tagged evaluation | Does it work equally across Gusii sub-regions? |
| F4.4 | Confidence scores in the demo | Grey out low-confidence words |
| F4.5 | Longer-audio demo (upload a file) | Chunk + stitch |

---

## Won't build — explicitly out of scope

Say no to these now, so nobody quietly starts one in Week 9.

| Not building | Why |
|---|---|
| Punctuation and capitalization restoration | A separate model and a separate dataset. Our transcripts are lowercase, unpunctuated, by design. |
| Speaker diarization ("who spoke when") | Different problem entirely. We use one speaker per clip. |
| Real-time streaming transcription | Needs a streaming architecture. Record-then-transcribe is fine for a demo. |
| A mobile app | The web demo works in a phone browser. An app adds zero marks. |
| Ekegusii → English translation | A completely different model and dataset. Tempting; say no. |
| Tone marking | Tone is phonemic in Ekegusii but unwritten. Predicting it is a research project of its own. |
| Text-to-speech (the reverse direction) | Different task, different data requirements. |
| Beating any specific WER target | We report what we get. Promising a number we can't control is how teams end up fudging results. |

---

## Build order — the dependency chain

```
F0.1 env ─┬─ F0.4 GPU ── F0.5 overfit ──────────────┐
          │                                          │
          ├─ F0.2 normalizer ─┐                      │
          │                    ├─ F0.3 validator ─┐  │
          └─ F1.1 ingest ──────┴─ F1.3 VAD ───────┤  │
                                                   ├──┴─ F1.7 dataset ─ F1.8 TRAIN ─ F1.9 eval ─ F1.10 demo
                          F1.5 ALIGNMENT ──────────┘                         │                      ▲
                                 ▲                                            │                      │
                          F3.2 text corpus ── F3.1 KenLM ─────────────────────┴──────────────────────┘
                                 │
                                 └─ F2.2 read-aloud prompts ── F2.3 drive ── F2.4 correction UI
```

**Critical path: F1.5 (forced alignment).** It is the one feature with no substitute and no parallel
route — every training run waits on it. It gets our best debugger (R7) and it starts in Week 2.

**Three things that block nobody and should start in Week 1 regardless:** F3.2 text collection,
F1.2 source logging, and F0.5 the overfit test.

---

## The cut list — if we fall behind

Drop from the bottom up, in this order. Decide by **Week 8**, not Week 11.

1. Everything in Tier 4
2. F2.9 backbone comparison — just ship XLS-R-300m and say why
3. F3.6 `test-hard` set
4. F2.8 re-alignment with our own model
5. F2.7 augmentation
6. F3.4 learning curve ← *resist this one; it's cheap and it's the best figure in the report*

**Never cut:** F1.5 alignment · F1.8 training · F1.9 honest evaluation · F3.1 the language model ·
F3.7 the cards. Those five are the project.

---

## If it all goes wrong

Suppose Week 9 arrives and we have 2 hours of data and one mediocre model. **We still submit a
complete project:** the corpus we did build, published; an honest WER; a learning curve showing how
performance scales with hours; an error analysis explaining what failed; and a working demo.

A project that reports "we reached 58% WER on 2.5 hours, and here is exactly why, and here is what
15 hours would likely give" is a *good* project. A project that hides its data shortage behind a
vague accuracy claim is not. **Honest and small beats impressive and unverifiable.**
