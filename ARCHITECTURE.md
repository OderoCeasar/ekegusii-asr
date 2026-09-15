# ARCHITECTURE — Ekegusii ASR

Technical design. Audience: anyone implementing a stage. Every stage below states its **inputs**,
**outputs**, **contract** (the format the next stage relies on), and **owner**.

Design rule for the whole system: **every stage reads files and writes files.** No stage holds state
in someone's notebook. Any stage can be re-run from its inputs by a different person on a different
machine. If a stage cannot be re-run from a clean checkout plus the HF dataset, it is broken.

---

## 0. System overview

```
                                  SOURCES
              ┌───────────────────────┴───────────────────────┐
     paired audio+text                              unpaired audio
   (scripture, read news,                    (radio, YouTube, conversation,
    recorded publications)                       field recordings)
              │                                             │
              ▼                                             ▼
      ┌───────────────┐                            ┌─────────────────┐
      │ S2a  FORCED   │                            │ S2b  HUMAN      │
      │     ALIGNMENT │                            │   TRANSCRIPTION │
      │  (no humans)  │                            │  ┌────────────┐ │
      └───────┬───────┘                            │  │ model pre- │ │
              │                                    │  │ fills text │◀──┐
              │                                    │  └────────────┘ │ │
              │                                    └────────┬────────┘ │
              │                                             │          │
              └──────────────────┬──────────────────────────┘          │
                                 ▼                                     │
                    ┌────────────────────────┐                         │
                    │ S3  PREPROCESS         │                         │
                    │  audio norm + segment  │                         │
                    │  text norm + vocab     │                         │
                    │  speaker-disjoint split│                         │
                    └───────────┬────────────┘                         │
                                ▼                                      │
                   data/manifests/{train,dev,test}.jsonl               │
                                │                                      │
                                ▼                                      │
                    ┌────────────────────────┐                         │
                    │ S4  FINE-TUNE          │                         │
                    │  XLS-R / MMS / w2v-BERT│                         │
                    │  CTC head, free GPU    │                         │
                    └───────────┬────────────┘                         │
                                ▼                                      │
                    ┌────────────────────────┐                         │
                    │ S5  DECODE + EVALUATE  │                         │
                    │  greedy | beam + KenLM │                         │
                    │  WER / CER + breakdown │                         │
                    └───────────┬────────────┘                         │
                                ├──────────────────────────────────────┘
                                ▼        (bootstrapping loop: model improves
                    ┌────────────────────────┐   → correction gets faster
                    │ S6  SERVE              │   → more data → better model)
                    │  Gradio on HF Spaces   │
                    └────────────────────────┘
```

---

## 1. Data contracts

Everything downstream depends on these three formats. Change them only by agreement, and if they
change, bump `schema_version` and say so in the standup.

### 1.1 Audio on disk

- **Format:** WAV, PCM 16-bit, **16 000 Hz, mono**. No MP3 anywhere past `data/raw/`.
- **Clip length:** 3–15 s for training. Hard reject <1 s or >25 s.
- **Naming:** `{source_id}_{speaker_id}_{seq:05d}.wav` — e.g. `radio-egesa_spk014_00031.wav`.
  The filename alone tells you the source and the speaker. No spaces, no capitals, no Kiswahili
  punctuation in filenames.

### 1.2 Manifest — `data/manifests/*.jsonl`

One JSON object per line. This is the single interface between data work and model work.
Committed to git (it is small — text only).

```json
{
  "id": "radio-egesa_spk014_00031",
  "audio_path": "processed/radio-egesa/radio-egesa_spk014_00031.wav",
  "duration": 6.42,
  "text": "nigo ngocha ase omobere oyio",
  "text_raw": "Nigo ngocha ase omobere oyio.",
  "speaker_id": "spk014",
  "gender": "f",
  "age_band": "25-40",
  "dialect": "rogoro",
  "source_id": "radio-egesa",
  "style": "spontaneous",
  "label_origin": "corrected",
  "confidence": "high",
  "schema_version": 1
}
```

Field rules:

| Field | Values | Why it exists |
|-------|--------|---------------|
| `audio_path` | relative to `data/` | portable across machines |
| `text` | normalized, model-ready | what the model trains on |
| `text_raw` | as the transcriber typed it | so we can re-normalize later without re-transcribing |
| `speaker_id` | stable, anonymous (`spk###`) | **drives the split.** Never a real name. |
| `style` | `read` \| `spontaneous` \| `broadcast` | lets us report WER per style |
| `label_origin` | `aligned` \| `human` \| `corrected` | aligned labels are noisier; we must be able to weight or exclude them |
| `confidence` | `high` \| `low` | low-confidence rows are excluded from **test**, allowed in train |

**Keeping `text_raw` is not optional.** Normalization rules will change in Week 5 when we discover an
orthography edge case. If we only stored normalized text, that discovery means re-transcribing
everything. With `text_raw`, it means re-running one script.

### 1.3 Speaker registry — `data/manifests/speakers.csv`

`speaker_id, gender, age_band, dialect_region, consent_ref, n_clips, total_minutes, split`

`split` is assigned **here**, per speaker, once, in Week 6 — and every manifest inherits it. This is
the mechanism that makes speaker-disjoint splits structurally impossible to get wrong. `consent_ref`
points at the signed form; it is never a name or phone number.

---

## 2. Stage 1 — Ingest

**Owner:** Data Acquisition Lead + Recording Coordinator · **Code:** `src/ingest/`

### 2.1 Found audio

```bash
yt-dlp -x --audio-format wav --audio-quality 0 -o "data/raw/%(id)s.%(ext)s" <URL>
ffmpeg -i in.wav -ac 1 -ar 16000 -c:a pcm_s16le out.wav
```

Every download appends a row to `data/SOURCES.md` **at download time**:

`source_id | title | URL | speaker(s) | licence/terms | paired text? | duration | downloaded_on | redistributable?`

The `redistributable?` column decides what we can publish. Anything marked `no` is used for training
only; we release its transcripts and timestamps, never its audio.

### 2.2 Recorded audio — protocol

Recording on phones is fine, and is what we will actually do. Quality comes from technique, not gear:

- **Quiet room.** Hard floors and bare walls echo — record in a room with soft furnishings, or drape
  a blanket. No fans, no TV, no open window onto a road.
- **Phone 15–20 cm from the mouth, slightly off-axis** so plosives (`p`, `t`, `k`) do not thump.
- **Airplane mode on.** A notification mid-take ruins the take.
- Highest-quality setting the recorder offers. Record WAV if the app allows; otherwise the highest
  bitrate available. We can downsample later; we can never un-compress.
- **One speaker per file.** Overlapping speech is nearly useless for training and we cannot fix it later.
- **Read the consent statement into the recording** at the start of the first file, then stop and save
  it separately as `consent_{speaker_id}.wav`. This makes consent auditable without paperwork.
- Two minutes of **room tone** (silence) per location — useful later for noise augmentation.

**Prompt design for read speech:** prompts come from the text corpus (Stage 1c) and must cover the
character set. Track character coverage — if `ng'` appears in three prompts out of four hundred, the
model will never learn it. The Language Lead signs off on the prompt list before the drive.

**Target per speaker:** 20–30 minutes read + 10 minutes spontaneous (describe your day, tell a story,
explain how to cook something). Spontaneous speech is harder to get and worth more.

### 2.3 Text corpus (for prompts *and* the language model)

Collect Ekegusii **text** aggressively and separately from audio. It is cheap, it is fast, it does two
jobs: it supplies reading prompts, and it trains the KenLM language model in Stage 5b that gives us a
free WER improvement. Sources: published scripture, hymnals, school readers, proverb collections,
Ekegusii Wikipedia/Wiktionary if present, Bloom Library, newspaper columns, Facebook groups writing in
Ekegusii, transcribed oral literature.

Target: **≥1 million words**. Store as plain UTF-8 text, one sentence per line, in `data/raw/text/`,
with a matching sources log. We will hit diminishing returns but more is strictly better here.

---

## 3. Stage 2a — Forced alignment (the no-human data engine)

**Owner:** Alignment & Dataset Engineer · **Code:** `src/align/`

**Input:** one long audio file + the exact text that was read.
**Output:** hundreds of 3–15 s clips, each with its text. **Zero human transcription hours.**

### Method

1. Normalize the text with the same normalizer as Stage 3 (same rules, or the alignment silently
   fails on punctuation).
2. Run a CTC forced aligner. Two viable free options:
   - **`torchaudio` MMS forced-alignment bundle** — multilingual, handles unseen languages through
     romanization. Preferred.
   - **`ctc-segmentation`** with any CTC acoustic model. Once we have our own Week-4 baseline, this
     becomes our best aligner because it actually knows Ekegusii.
3. The aligner emits per-token timestamps plus a per-segment confidence score.
4. Cut at sentence boundaries, snapping to the nearest silence found by Silero VAD so clips do not
   start mid-word.
5. **Drop low-confidence segments.** Be aggressive. A wrong label is worse than a missing one —
   a missing clip costs us one example; a wrong clip actively teaches the model something false.
6. Write manifest rows with `label_origin: "aligned"`.

### Mandatory human check

Before any aligned batch enters training, a human listens to **20 random clips** and confirms the text
matches. Log the pass rate in `reports/alignment_qa.md`. **Below 90% pass, the batch is rejected** and
the aligner is fixed — do not "just use it anyway", that poisons the training set in a way that is
extremely hard to diagnose three weeks later.

### Known failure modes

- **Text and audio drift apart.** The reader skipped a verse, or the published text has a different
  edition than the recording. Alignment confidence collapses at the drift point. Fix: align in
  chapter-sized chunks, never the whole book at once, so drift is contained.
- **Intros, outros, music, and station idents** are in the audio but not the text. Trim them first.
- **Read speech is not conversation.** A corpus made only of aligned scripture produces a model that
  transcribes sermons well and ordinary conversation badly. **Target ≥30% spontaneous speech** in the
  final corpus. This is the main reason Stage 2b exists at all.

---

## 4. Stage 2b — Human transcription & correction

**Owner:** Transcription QA Lead · **Code:** `src/serve/annotate_app.py`

### Tooling

A small **Gradio app on a free HF Space**: plays a clip, shows an editable text box, Save writes to the
dataset repo. Works on a phone, which matters — most transcription will happen on phones. Alternative:
Label Studio locally. Do not use a shared Google Sheet with manually typed filenames; filename typos
will silently corrupt the manifest and you will lose a day finding out.

From Week 5 the text box is **pre-filled by the current model**. Transcribers correct rather than type.
Log both `text_raw_model` and the human-corrected `text_raw` — the difference between them is a free,
continuously updating measurement of real-world WER on fresh audio.

### Quality control

- **Double-transcribe 10%** of clips with two independent transcribers.
- Measure agreement as **CER between the two versions**. Under ~10% CER disagreement is healthy.
  Higher means the guide is ambiguous — fix the *guide*, not the transcribers.
- The Language Lead adjudicates disagreements and every ruling becomes a numbered line in the
  Transcription Guide with an example. The guide only grows.

### Transcription Guide — must specify

Orthography and casing · punctuation policy · numbers written as spoken · code-switch tagging ·
`[noise] [laughter] [unclear] [overlap]` tags · what to do with false starts and repetitions
("transcribe them, they are real speech") · hesitation sounds · what to discard entirely.

---

## 5. Stage 3 — Preprocess

**Owner:** Audio Pipeline Engineer · **Code:** `src/prep/` · **Entry:** `scripts/build_dataset.sh`

Fully deterministic and re-runnable. One command rebuilds every derived artifact from `raw/`.

### 5.1 Audio

resample 16 kHz mono → loudness normalize (EBU R128, target −23 LUFS) → Silero VAD segmentation →
enforce 3–15 s → reject on: clipping, SNR below threshold, near-silence, detected music.
Log every rejection with its reason to `reports/prep_rejects.csv`. When someone asks in Week 10 why
the corpus is 12 hours and not 18, that file is the answer.

### 5.2 Text normalization

Order matters, and this is the Ekegusii-specific part — get it wrong and the model learns a corrupted
alphabet:

1. Unicode **NFC** normalization.
2. Convert typographic apostrophes `’ ʼ ‘` → ASCII `'`. **Then stop.**
   **Do not strip apostrophes.** In Ekegusii `ng'` is a single velar nasal phoneme and the apostrophe
   is part of the letter. A generic `[^a-z ]` regex — the default in every ASR tutorial online —
   silently destroys it. This is the single most likely catastrophic bug in the project.
3. Lowercase.
4. Strip sentence punctuation `. , ? ! : ; " ( )` — but not the apostrophe (rule 2) and not the hyphen
   until the Language Lead rules on hyphenated forms.
5. Numbers → words as spoken (Language Lead supplies the number words).
6. Collapse whitespace; strip leading/trailing space.
7. **Validate against the allowed character set.** Any character outside it raises an error naming the
   clip. Never silently drop unknown characters — an unexpected character means either a typo worth
   fixing or an orthography rule worth adding, and both are findings.

Starting character set (**Language Lead confirms against standard Ekegusii orthography in Week 1**):

```
a b ch e g i k m n ng ng' ny o r s t u w y  +  space  +  '
```

Ekegusii has no native `p d f h j l q v x z`. Their appearance is a signal: either a transcription
typo, or a genuine borrowed word (`hoteli`, `posta`). Decide the policy once, write it in the guide,
and let the validator enforce it forever.

### 5.3 Splitting — the rule that protects our numbers

```
assign split PER SPEAKER, never per clip
```

- `test` ~10% · `dev` ~10% · `train` ~80%, measured in **minutes of audio**, not clip count.
- **No speaker appears in more than one split.** Enforced in `speakers.csv` and asserted by
  `scripts/validate_manifests.py`, which fails CI if violated.
- **No source document spans splits** — if the same scripture chapter is in train and test, the
  language model has memorized the text and the WER is meaningless.
- `dev` and `test` must each contain **both** read and spontaneous speech, and both genders.
- Freeze `test` in Week 6. Every tuning decision uses `dev`.

Also build a small **`test-hard`** set: noisy, spontaneous, fast, code-switched, unusual dialect. It
will score badly and that is the point — it is where the honest discussion in the report comes from,
and examiners reward a team that knows its own weaknesses.

---

## 6. Stage 4 — Fine-tune

**Owner:** Model Engineer (Baseline) · **Code:** `src/train/` · **Runs on:** Kaggle / Colab

### Architecture

Self-supervised transformer speech encoder (XLS-R / MMS / w2v-BERT) + a fresh linear **CTC** head over
our character vocabulary. The encoder already knows what speech sounds like from hundreds of thousands
of hours of other languages; we teach the head to map its representations onto Ekegusii letters.

**Why CTC and not sequence-to-sequence:** CTC is monotonic — it cannot invent text that was not spoken.
With very little data, seq2seq models (Whisper) hallucinate fluent, plausible, entirely fabricated
sentences. For under ~50 hours, CTC is both more accurate and more honest. We still fine-tune
Whisper-small as a comparison because the report is stronger for it.

### Starting hyperparameters

```yaml
model: facebook/wav2vec2-xls-r-300m
freeze_feature_encoder: true        # the CNN front end; always freeze at this data scale
attention_dropout: 0.05
hidden_dropout: 0.05
feat_proj_dropout: 0.05
mask_time_prob: 0.05                # SpecAugment — raise to 0.08 if overfitting
layerdrop: 0.05
ctc_loss_reduction: mean

learning_rate: 3e-4                 # 1e-4 if loss is unstable
warmup_steps: 500
num_train_epochs: 30                # small corpora need many passes
per_device_train_batch_size: 8      # 16 GB GPU
gradient_accumulation_steps: 2      # effective batch 16
fp16: true
gradient_checkpointing: true        # trades ~20% speed for a much bigger batch
eval_strategy: steps
eval_steps: 400
save_steps: 400
save_total_limit: 2
load_best_model_at_end: true
metric_for_best_model: wer
greater_is_better: false
group_by_length: true               # big speedup: batches clips of similar duration
```

### Kaggle/Colab survival rules

Sessions die. Assume it.

- `save_steps` small enough that you never lose more than ~20 minutes.
- Push checkpoints to the HF Hub, not to the session disk — the session disk vanishes.
- Every run resumes from the last checkpoint with one flag. Test the resume path on day one, on a
  toy run, *before* you need it at 2am.
- One config file per run, committed. A result you cannot reproduce is not a result.
- Log every run in `reports/experiments.md`: run ID, config hash, data version, dev WER, notes.
  **A run that is not in that table did not happen.**

### Augmentation (cheap, effective at this data scale)

speed perturbation ×0.9 / ×1.0 / ×1.1 (triples the corpus) · SpecAugment (built in via `mask_time_prob`) ·
additive room-tone noise at varied SNR · light reverb. Apply to **train only** — never to dev or test.

---

## 7. Stage 5 — Decode & evaluate

**Owner:** Model Engineer (Decoding) + Evaluation Lead · **Code:** `src/eval/`

### 7a. Greedy decoding

Argmax per frame, collapse repeats, drop blanks. The baseline number. Fast, no extra dependencies.

### 7b. Beam search + KenLM — the cheapest win available

Train a **5-gram word-level KenLM** on the text corpus from §2.3 (CPU, minutes) and decode with
`pyctcdecode`. Tune `alpha` (LM weight) and `beta` (word insertion bonus) **on dev, never on test**.

Typical gain: **5–15 absolute WER points**, for a few hours of work and zero GPU. This is the highest
return-on-effort action in the entire project. It works because the acoustic model hears
"omo-bere" ambiguously, and the LM knows which Ekegusii word actually exists.

Report both numbers. "WER 41% greedy → 29% with LM" is a better result *and* a better story than a
single number.

### 7c. Metrics

| Metric | Definition | Why |
|--------|-----------|-----|
| **WER** | word-level edit distance ÷ reference words | The standard. Report it first. |
| **CER** | character-level | Fairer to agglutinative morphology, where one prefix error kills a whole "word" |
| **Sub / Del / Ins** | error breakdown | Tells you *which* problem you have (see below) |

Reading the breakdown:
- **Deletions dominant** → the model is under-confident, or clips are too long, or audio is too quiet.
- **Insertions dominant** → LM weight `alpha` is too high, or the audio has background speech.
- **Substitutions dominant** → normal; look at *which* characters confuse (a confusion matrix over
  characters will point straight at orthography problems, e.g. `ng` vs `ng'`).

### 7d. Required breakdowns — the actual analytical contribution

Report WER/CER **sliced by**: speech style (read vs spontaneous) · speaker gender · age band ·
dialect region · source · clip duration bucket · `label_origin`. Plus the `test-hard` set.

Deliver a **learning curve**: train on 1h, 2h, 5h, 10h, all, and plot WER against hours. This single
chart answers "how much more data would we need?" — which is the question every reader of the report
will have — and it is the most cited figure in low-resource ASR papers for exactly that reason.

### 7e. Error analysis

Pull the 50 worst-scoring dev clips and listen to them. Categorize by hand: bad reference text?
overlapping speakers? code-switching? dialect the model never saw? genuinely hard audio? Roughly a
third of "model errors" in a first-pass corpus turn out to be *label* errors — finding them improves
the corpus and the model at once, and writing that up is worth more marks than another training run.

---

## 8. Stage 6 — Serve

**Owner:** Demo & Documentation Lead · **Code:** `src/serve/app.py`

Gradio app on a free HF Space: microphone in → transcript out, with a toggle for greedy vs LM decoding
so viewers can see the difference live. Free-tier CPU is sufficient — a 300M CTC model runs faster than
real time on CPU because there is no autoregressive decoding loop.

Also publish:
- **Model card** — training data, hours, speaker count, licence, WER/CER table, and an explicit
  **limitations** section (dialect coverage, noise robustness, code-switching).
- **Dataset card** — collection method, consent procedure, speaker demographics, licence per source,
  and known gaps.

These are not paperwork. They are the artifacts that make this *research* rather than a class project,
and they are what makes the work usable by the next person who tries to build on Ekegusii.

---

## 9. Risks and the decision made in advance

| Risk | Probability | Mitigation — decided now, not in Week 9 |
|------|------------|------------------------------------------|
| Too little data by Week 10 | **High** | Forced alignment from Week 2; weekly per-person quotas; hours tracked publicly on a chart in the group chat |
| Transcription inconsistency | **High** | Written guide before any transcription; 10% double-transcription; one named adjudicator |
| Apostrophe / `ng'` destroyed by text cleaning | **Medium, catastrophic** | Explicit rule in §5.2; character-set validator that errors out; unit test on a fixture containing `ng'` |
| Speaker leakage between splits | Medium, invalidates everything | Split assigned per speaker in `speakers.csv`; CI assertion |
| Free GPU quota exhausted | Medium | Kaggle (30h/wk) primary + Colab + Lightning; checkpoint to Hub; small experiments first |
| Aligned data is wrong but looks fine | Medium | 20-clip human QA per batch, hard 90% pass gate |
| Corpus is all read speech, model fails on conversation | **High if unmanaged** | ≥30% spontaneous target, tracked weekly; reported as a separate WER slice |
| Member disengages | Medium | Weekly two-line standup; every role has a named backup in `ROLES.md` |
| Copyright complaint | Low, serious | `SOURCES.md` filled at download time; never redistribute audio marked non-redistributable |

---

## 10. Definition of done

- [ ] ≥15 hours of transcribed Ekegusii speech, ≥15 speakers, ≥30% spontaneous
- [ ] Speaker-disjoint train/dev/test, frozen and documented
- [ ] Fine-tuned model published to the HF Hub with a model card
- [ ] Dataset (or the fully reproducible recipe for the non-redistributable parts) published with a dataset card
- [ ] WER and CER, greedy and LM-decoded, with all slices from §7d
- [ ] Learning curve (WER vs training hours)
- [ ] Error analysis of 50 worst clips, categorized
- [ ] Live demo anyone can use from a phone
- [ ] Every result reproducible from a clean checkout: `git clone` → config → notebook → same number
