# Ekegusii Speech Recognition (ASR)

**Goal:** a model that listens to Ekegusii (Kisii, ISO `guz`, ~2.2M speakers) and writes it down.

**Why it matters:** there is no working speech recognizer for Ekegusii. Not a bad one — *none*. Every
mainstream ASR system covers ~100 languages out of 7,000. The blocker is not algorithms; the algorithms
are public and free. The blocker is that **nobody has built the dataset.** That is the actual project.
The model is the easy half.

---

## 1. Read this part even if you read nothing else

### 1.1 What we are really building

Three things, in this order of difficulty:

| # | Thing | Difficulty | Who cares |
|---|-------|-----------|-----------|
| 1 | **A transcribed Ekegusii speech corpus** (audio + matching text) | Hard, slow, unglamorous | Everyone, forever |
| 2 | A fine-tuned ASR model trained on it | Easy — a known recipe | Us, for the grade |
| 3 | A demo you can talk into | Easy — one afternoon | Anyone we show it to |

Item 1 is ~70% of the work. If we get item 1 right, items 2 and 3 are largely a matter of running
scripts that already exist. If we get item 1 wrong, no amount of model tuning saves us. Please
internalize this: **most of this project is careful data work, not machine learning.**

### 1.2 The trick that makes this possible with no money and one semester

The pipeline in our brief reads *collect audio → transcribe → train*. Done literally, that means
sitting down and hand-transcribing hundreds of hours. Ten people transcribing at a realistic
**8–10 minutes of human time per 1 minute of audio** would need ~90 hours of labour per person to
produce a mere 10 hours of data. That kills the project.

We do not do that. We use three shortcuts, in order:

**Shortcut A — Harvest audio that is *already* transcribed.**
Ekegusii has long-form recordings whose exact text is already published: audio Scripture, recorded
religious publications, read news bulletins, audiobooks, church liturgy. That is audio + text
already paired — we just need to *align* them. Forced alignment (a free algorithm) takes a 40-minute
recording and its full text and tells us exactly which second each word lands on. That converts long
recordings into thousands of short, labelled training clips **with zero human transcription.**
This alone can realistically produce 10–30 hours in the first two weeks.

**Shortcut B — Train a rough model early, then let it do the typing.**
Once we have a rough baseline (Week 3–4), we run it over new audio. It will produce bad-but-not-random
transcripts. Humans then **correct** rather than type from scratch. Correction runs roughly 3–5× faster
than blank-page transcription. The model gets better, correction gets faster, which makes the model
better. This loop is the entire trick. It has a name: bootstrapping / human-in-the-loop.

**Shortcut C — Stand on a pretrained model.**
We never train from zero. We take a model already trained on hundreds of thousands of hours of
*other* languages, which already knows what human speech physically sounds like, and we teach it only
the Ekegusii-specific part. This is why 10 hours of data is enough to get something working, when
from-scratch training would need 1,000+.

### 1.3 The honest expectations

Say these numbers out loud now so nobody is disappointed in Week 11:

- With ~10 hours of clean read speech: expect **WER around 30–45%** on similar read speech.
- On **spontaneous conversation** (people talking naturally, overlapping, code-switching into Swahili
  and English): expect **55–75%**, and worse if we trained only on read speech.
- A word-level language model on top typically buys back **5–15 absolute WER points** for free.

WER of 35% is *not* a failure. For a language with zero prior systems, a working 35% WER model plus a
published open dataset is a genuinely novel contribution. Chasing 5% WER is not on the table this
semester and anyone who promises it is guessing.

**The single biggest risk to our grade is not model quality. It is arriving at Week 10 with
3 hours of data.** Data collection starts Week 1 and never stops.

### 1.4 Two rules that are not negotiable

**Consent.** Every person we record signs (or records a spoken) consent saying they understand the
recording will be used to build a public language dataset. No consent, no recording, no exceptions.
Kisii speakers are being asked to donate their voice to a public research artifact — we treat that
seriously, and the university will ask.

**Licensing.** Found audio (radio, YouTube, published recordings) is usually copyrighted. We may use
it for research. We generally may **not** redistribute the raw audio. So: we publish **transcripts,
timestamps, and our own recordings**, and for third-party audio we publish the *recipe* (source URL +
timestamps) so others can reproduce it. Every single source goes in `data/SOURCES.md` with its licence
at the moment we download it — not later, not from memory.

---

## 2. The pipeline, stage by stage, in plain language

```
 ┌──────────────┐   ┌───────────────┐   ┌──────────────┐   ┌─────────────┐   ┌──────────┐   ┌────────────┐
 │ 1. COLLECT   │──▶│ 2. TRANSCRIBE │──▶│ 3. PREPARE   │──▶│ 4. FINE-TUNE│──▶│ 5. EVAL  │──▶│ 6. SERVE   │
 │ audio + text │   │ & clean       │   │ features     │   │ pretrained  │   │ WER/CER  │   │ demo app   │
 └──────────────┘   └───────────────┘   └──────────────┘   └─────────────┘   └──────────┘   └────────────┘
        ▲                                                                            │
        └──────────────── Shortcut B: model pre-fills transcripts ◀──────────────────┘
```

### Stage 1 — Collect audio

Two streams running in parallel:

- **Found audio (fast, do first).** Long recordings already paired with published text → feeds
  Shortcut A. Also unpaired radio/YouTube speech, which becomes correction work later.
- **Recorded audio (slower, higher quality, ours to publish).** Team members and their families
  reading prompt sentences, plus natural conversation. This is the part we fully own the rights to,
  and it is the part that gives us speaker diversity — different ages, genders, and sub-dialects.

Everything lands as **16 kHz mono WAV**, with a metadata row per file: speaker ID, age band, gender,
sub-dialect/location, recording device, consent status, source, licence.

### Stage 2 — Transcribe & clean

Humans write down what was said, following one written standard (the **Transcription Guide**, owned by
the Language Lead). This is where teams silently fail: if five people spell the same word five ways,
the model is being taught that those are five different words and it learns nothing. Consistency
matters more than elegance.

Ekegusii-specific things the guide must pin down (Language Lead confirms against the standard
orthography before anyone transcribes a single clip):

- **`ng'` is one sound, and the apostrophe is part of the letter.** Our text-cleaning must never strip
  apostrophes blindly — that would destroy a phoneme. Same care for the digraphs `ch`, `ny`, `ng`.
- **Tone is phonemic but unwritten.** Two words spelled identically may differ only in tone. We accept
  that ambiguity; we do not invent tone marks.
- **Code-switching is real.** People drop Swahili and English words mid-sentence. Rule: write them as
  spoken, tag the segment as mixed. Do not "translate them back" into Ekegusii.
- One casing convention, one punctuation convention, one policy for numbers ("write them as spoken"),
  one tag set for noise/laughter/unclear audio.

### Stage 3 — Prepare features

Mechanical, scripted, no judgement calls:
resample to 16 kHz mono → normalize loudness → split long audio into **3–15 second** clips on silence →
drop clips that are too loud, too quiet, clipped, or music → normalize the text → build the character
vocabulary → write `train / dev / test` manifests.

**The one rule that decides whether our evaluation is honest:** split by **speaker**, not by clip. If
the same voice appears in both training and test, our WER is a lie and any examiner who knows ASR will
spot it in thirty seconds.

### Stage 4 — Fine-tune a pretrained model

Take a large multilingual speech model, replace its output layer with one that predicts *our*
character set, and train on our data. Runs on a free Kaggle or Colab GPU in a few hours. The
recipe is public and well-trodden; the interesting work is in what data we feed it.

### Stage 5 — Evaluate

- **WER** (Word Error Rate) — % of words wrong. The headline number.
- **CER** (Character Error Rate) — % of characters wrong. Kinder to agglutinative languages like
  Ekegusii, where a single verb carries prefixes and suffixes that would otherwise be one big
  all-or-nothing word. Report both; expect CER to be roughly a third of WER.
- Break the number down: read vs spontaneous, per speaker, per gender, per source. A single average
  WER hides everything interesting. "Our WER is 38% overall but 61% on female speakers" is a finding,
  and finding it is worth more marks than shaving two points off the average.

### Stage 6 — Serve

A web page with a record button that prints the transcript. Free hosting. This is what we demo, and
it takes an afternoon — but only if Stages 1–3 were done properly.

---

## 3. Free tools and services — the complete list

Nothing here costs money. No credit card required for any of it.

| Need | Tool | Notes / free limits |
|------|------|--------------------|
| GPU for training | **Kaggle Notebooks** | 30 GPU-hours/week, P100 16GB or 2×T4, 12h/session. Best free GPU available. Needs phone verification. |
| GPU, backup | **Google Colab (free)** | T4, sessions drop after a few hours. Fine for experiments, bad for long runs — checkpoint often. |
| GPU, backup 2 | **Lightning AI Studio free tier** | Monthly free GPU credits. Useful overflow. |
| Dataset + model hosting | **Hugging Face Hub** | Free, generous size limits, private repos supported. This is our source of truth for data. |
| Demo hosting | **Hugging Face Spaces (free CPU)** | A 300M CTC model transcribes faster than real time on CPU. Good enough for the demo. |
| Bulk file storage | **Google Drive** | 15 GB per account × 10 members. Staging only — HF Hub is canonical. |
| Audio download | **yt-dlp** | Extracts audio from most sites. |
| Audio conversion | **ffmpeg** | Resample, convert, trim, split. |
| Silence detection | **Silero VAD** | Tiny, fast, free, no GPU. Splits long audio at natural pauses. |
| Forced alignment | **torchaudio MMS forced aligner / ctc-segmentation** | Audio + text → per-word timestamps. This powers Shortcut A. |
| Transcription / correction UI | **Label Studio** (local) or a small **Gradio** app | Gradio + HF Space is simpler and works on phones. Recommended. |
| Long-form annotation | **ELAN** or **Audacity** | Standard in language documentation. Free. |
| Model training | **Hugging Face `transformers`** | `Wav2Vec2ForCTC` + `Trainer`. Recipe is well documented. |
| Metrics | **`jiwer` / `evaluate`** | WER and CER in two lines. |
| Language model boost | **KenLM + pyctcdecode** | Trains a text n-gram model on CPU in minutes. Cheapest WER win available. |
| Code + task tracking | **GitHub** (repo + Projects board) | Free. One repo, everything in it. |

### Pretrained models to fine-tune (pick in this order)

1. **`facebook/wav2vec2-xls-r-300m`** — 300M params, pretrained on 128 languages including African
   ones. The reliable default for low-resource CTC. Fits a free T4. **Start here.**
2. **`facebook/mms-1b-all`** — Meta's Massively Multilingual Speech, covers 1,000+ languages via
   lightweight adapters. **First action item for the model team: check whether `guz` is already in its
   language list.** If it is, we have a head start and a strong pre-existing baseline to beat. Only the
   adapter needs training, which is cheap.
3. **`facebook/w2v-bert-2.0`** — 600M, pretrained on ~4.5M hours. Often the strongest low-resource CTC
   starting point today. Heavier; try once the 300m pipeline runs end to end.
4. **`openai/whisper-small`** — different architecture (sequence-to-sequence, not CTC). Usually needs
   more data than we will have, and likes to hallucinate fluent nonsense on low-resource languages —
   but it is the obvious comparison point and the report is stronger for including it.

---

## 4. Twelve-week plan

| Week | Milestone | Gate — we do not move on until this is true |
|------|-----------|--------------------------------------------|
| 1 | Repo live, roles assigned, consent form + Transcription Guide v1 written, sources scouted | Every member can run `git clone` and open a Kaggle notebook |
| 2 | Found-audio harvest; forced alignment working on ONE recording end to end | ≥1 hour of aligned clips exists and a human has spot-checked 20 of them |
| 3 | Alignment scaled up; first recording drive; preprocessing pipeline scripted | ≥5 hours aligned; manifests build with one command |
| 4 | **Baseline model trained** on whatever we have | A WER number exists, however bad. First number beats no number. |
| 5 | Correction UI live; model pre-fills transcripts; everyone starts correcting | ≥1 hour of human-corrected spontaneous speech |
| 6 | Second recording drive, targeting missing speaker demographics | ≥10 hours total; ≥15 distinct speakers; speaker-disjoint splits frozen |
| 7 | **Mid-project review.** Model v2 on the full corpus. Compare backbones. | v2 beats v1; backbone choice decided and written down |
| 8 | KenLM language model + decoder integration | Measured WER delta from the LM, both numbers in the table |
| 9 | Data push: correction sprint, focus on spontaneous + underrepresented speakers | ≥15 hours total |
| 10 | **Final model.** Full evaluation: per-speaker, per-gender, per-source breakdowns | Results table complete, error analysis written |
| 11 | Gradio demo deployed; dataset card + model card published on HF | Someone outside the group can use the demo unaided |
| 12 | Report, slides, dress rehearsal | Rehearsed once, end to end, with a live demo |

**Freeze the test set in Week 6 and never look at it again until Week 10.** Every intermediate
decision is made on the dev set. Tuning against the test set is how teams quietly cheat themselves and
then cannot explain their own numbers under questioning.

---

## 5. What every member does, regardless of role

1. **Transcribe / correct your weekly quota.** Everyone. No exceptions, including me. Specialist roles
   are *in addition to* the quota, not instead of it. Data is the bottleneck, so everyone carries data.
2. **Recruit speakers.** Family, neighbours, church, market, campus. We need old and young, men and
   women, and speakers from different parts of Gusii. A corpus of ten male university students is a
   corpus that only works for ten male university students.
3. **Commit your work to the repo.** Work that lives on your laptop does not exist.
4. **Log what you did in the weekly standup thread.** Two lines: what you finished, what is blocking you.

**If you are blocked, say so within 24 hours.** A blocked member who stays quiet for a week costs us
more than a wrong turn we catch early.

---

## 6. Repository layout

```
ekegusii-asr/
├── README.md              ← you are here (team brief)
├── ARCHITECTURE.md        ← technical design: formats, stages, specs
├── ROLES.md               ← who owns what
├── configs/               ← YAML training + preprocessing configs
├── data/
│   ├── SOURCES.md         ← every source + licence. Filled in as we go, never retroactively.
│   ├── raw/               ← untouched downloads & recordings (gitignored)
│   ├── interim/           ← resampled, segmented (gitignored)
│   ├── processed/         ← final 16 kHz clips (gitignored, lives on HF Hub)
│   └── manifests/         ← train/dev/test JSONL — SMALL, committed to git
├── docs/
│   ├── TRANSCRIPTION_GUIDE.md
│   ├── CONSENT_FORM.md
│   └── RECORDING_PROTOCOL.md
├── src/{ingest,align,prep,train,eval,serve}/
├── notebooks/             ← Kaggle/Colab training notebooks
├── scripts/               ← one-command entry points
└── reports/               ← results tables, error analysis, final report
```

Audio never goes into git. Manifests and code do. The Hugging Face dataset repo is where audio lives.

---

## 7. Where to start today

1. Read this file and `ARCHITECTURE.md`.
2. Find your name in `ROLES.md` and read your deliverables.
3. Create accounts: **GitHub**, **Hugging Face**, **Kaggle** (verify your phone — required for GPU).
4. Post your three usernames in the group chat so I can add you to the org.
5. Data-side members: start scouting sources *today*. Model-side members: get
   `facebook/wav2vec2-xls-r-300m` to load in a Kaggle notebook and overfit deliberately on ten clips
   of any language — that proves your environment works before real data arrives.

Nobody waits for data to start working. There is a first task for every role in Week 1.
