# ROLES — 10 members

Fill in the names. Each role has an **owner** (accountable) and a **backup** (covers absence, reviews
the owner's pull requests). Backups are assigned so that no two people on the same critical path back
each other up.

**Universal duty, every role, every week:** transcribe or correct **60 minutes of audio**, and recruit
at least **one speaker** during a recording drive. Specialist work is *in addition to* this, never
instead of it. Data is the bottleneck; everyone carries data.

---

## R1 · Team Lead & Integration — *(you)*
**Backup:** R10

Owns the whole, not a stage. Nobody else can see the seams between stages; you can.

- Run the weekly 30-minute standup. Two lines per person: done / blocked.
- Own the GitHub repo, the HF organization, the Project board, and merge rights.
- **Unblock people within 24 hours.** This is the majority of the job and the one nobody else can do.
- Own the master hours-of-data chart — updated weekly, posted in the group chat. Public numbers are
  what keep a ten-person team honest.
- Enforce the gates: the Week-6 test-set freeze, the 90% alignment QA threshold, "no run without a
  config in `experiments.md`".
- Integrate: make sure Stage N's output actually loads in Stage N+1. Run the end-to-end path yourself
  in Week 4 and again in Week 8.
- Write the final report's narrative; section owners supply their sections.

**Week 1:** repo + org live, everyone added, board populated with Week 1–3 tasks.

---

## R2 · Data Acquisition & Licensing Lead
**Backup:** R7

The person who makes Shortcut A possible. If R2 delivers in Week 2, the whole project is de-risked.

- Hunt **paired audio+text** first — recordings whose exact published text exists. This is the highest
  value work in the first fortnight. Audio scripture, recorded publications, read news, audiobooks,
  liturgy, school readers with recordings.
- Then unpaired audio: radio archives, YouTube channels, podcasts, church recordings, county
  government broadcasts.
- Run `yt-dlp` + `ffmpeg`; deliver 16 kHz mono WAV into `data/raw/`.
- **Own `data/SOURCES.md`.** Every row filled at download time with its licence and a
  redistributable yes/no. This column decides what we may publish — getting it wrong late is expensive.
- Where a rights holder is reachable (a local radio station, a church, a county office), **ask for
  permission in writing.** A one-paragraph email citing a university research project succeeds more
  often than people expect, and a yes turns non-redistributable audio into a publishable asset.

**Week 1:** ≥10 candidate sources logged, ≥3 confirmed paired audio+text.
**Week 3:** ≥20 hours of raw audio downloaded and catalogued.

---

## R3 · Recording & Speaker Coordinator
**Backup:** R4

Owns the data we fully own the rights to — and owns speaker diversity, which decides who our model
works for.

- Write `docs/CONSENT_FORM.md` and `docs/RECORDING_PROTOCOL.md` (§2.2 of ARCHITECTURE).
- Plan and run the recording drives (Weeks 3, 6, 9). Book quiet rooms. Brief every recorder on
  technique before they record anything.
- **Own the demographic balance chart**: gender, age band, dialect region. Report weekly against
  targets. When a cell is empty, name it and recruit into it — this is your main lever.
- Assign anonymous `speaker_id`s and maintain `speakers.csv`. Keep the identity mapping **off the repo**
  and off the group chat.
- File and track consent. **No consent, no recording** — you hold this line even under time pressure.
- Target: **≥15 speakers**, ≥20 min read + ≥10 min spontaneous each.

**Week 1:** consent form and protocol approved.
**Week 3:** first drive complete, ≥5 speakers recorded.

---

## R4 · Language & Orthography Lead *(must be a fluent Ekegusii speaker)*
**Backup:** R5

The linguistic authority. Every other role defers to R4 on what Ekegusii *is*. Assign this to your
strongest native speaker with the patience for detail — not necessarily your strongest coder.

- **Week 1, before anyone transcribes a single clip:** confirm the character set and the `ng'` /
  `ch` / `ny` / apostrophe rules in ARCHITECTURE §5.2. **The whole project's text normalization
  depends on this and it is the likeliest catastrophic bug.**
- Write and own `docs/TRANSCRIPTION_GUIDE.md`. It starts short and grows one numbered rule at a time,
  each with a real example from our data.
- Adjudicate every transcription disagreement. Each ruling becomes a guide rule — so the same argument
  never happens twice.
- Supply the number words (for "numbers written as spoken") and the code-switching policy.
- Approve the reading prompt list for character coverage before each drive.
- Sit with R9 on error analysis: only a fluent speaker can tell a model error from a label error, and
  that distinction is a third of the findings.

**Week 1:** character set confirmed in writing; Transcription Guide v1 published.

---

## R5 · Transcription QA Lead
**Backup:** R3

Owns human-generated labels — the throughput *and* the consistency.

- Run the transcription pipeline: batch clips, assign them, track completion per person.
- **Publish the weekly leaderboard** of minutes transcribed. It is not about competition; it is about
  making quietly-falling-behind visible while it is still fixable.
- Enforce **10% double-transcription**; compute inter-annotator CER weekly; escalate disagreements to R4.
- Train every member once, hands-on, on the guide and the tool. Thirty minutes of training per person
  saves days of inconsistent data.
- From Week 5, run the **correction loop**: pull the model's pre-filled transcripts in, push corrected
  text back, and log the model-vs-human delta — that delta is a free running WER measurement on fresh
  audio, and R9 will want it.

**Week 2:** guide training delivered to all 10 members.
**Weekly from Week 4:** ≥10 h corrected cumulative → ≥15 h by Week 9.

---

## R6 · Audio Pipeline Engineer
**Backup:** R8

Turns messy audio into clean, uniform, model-ready clips. Deterministic, scripted, re-runnable.

- Build `src/prep/` and `scripts/build_dataset.sh`: resample → loudness normalize → Silero VAD segment
  → length filter → quality reject (clipping, SNR, silence, music).
- Implement the **text normalizer** to R4's spec, with the **character-set validator that raises on
  unknown characters** rather than silently dropping them.
- Write `scripts/validate_manifests.py`: schema check, file-existence check, duration check, and the
  **speaker-disjoint split assertion**. Wire it into CI so a bad manifest cannot be merged.
- **Unit-test the normalizer on a fixture containing `ng'`** and commit that test in Week 2. This one
  test is the guard against the project's most dangerous bug.
- Own reject logging — `reports/prep_rejects.csv`, with a reason per rejected clip.

**Week 3:** one command rebuilds the full dataset from `raw/`.

---

## R7 · Alignment & Dataset Engineer
**Backup:** R2

Owns Shortcut A — the engine that produces training data without human transcription. The highest-
leverage technical role in the first month.

- Get forced alignment working end to end on **one** recording by Week 2. One working example beats a
  half-built general system.
- Scale it: chapter-sized chunks, VAD-snapped boundaries, confidence-based rejection.
- Run **20-clip human QA per batch** with R4 or R5; enforce the **90% pass gate**; log results in
  `reports/alignment_qa.md`. You have the authority to reject a batch — use it.
- From Week 5, re-align using **our own** Week-4 baseline model, which knows Ekegusii and will beat a
  generic multilingual aligner.
- Own dataset assembly: merge aligned + human manifests, package and version to the HF Hub, maintain
  the dataset card.
- With R1 and R3, execute the **Week 6 split freeze**.

**Week 2:** ≥1 hour aligned and spot-checked.
**Week 3:** ≥5 hours. **Week 6:** ≥10 hours, splits frozen.

---

## R8 · Model Engineer — Baseline
**Backup:** R6

Owns training. Starts in Week 1 — do not wait for data.

- **Week 1, before any real data exists:** get `facebook/wav2vec2-xls-r-300m` training in a Kaggle
  notebook and deliberately overfit ten clips of *any* language until WER hits ~0. That proves the
  environment, the data loader, the CTC head, and the metric all work, so that when real data lands
  the only new variable is the data.
- **First action item:** check whether `guz` is in `facebook/mms-1b-all`'s language list. If yes, we
  inherit a free baseline to beat and a cheap adapter-only fine-tune path. Report either way in Week 1.
- Own the checkpoint/resume discipline: push to Hub, resume with one flag, **test the resume path on a
  toy run in Week 1** — not at 2am in Week 7.
- Own `reports/experiments.md`. One row per run: ID, config hash, data version, dev WER, notes.
  Enforce it on yourself and R9: **a run not in the table did not happen.**
- Deliver the Week-4 baseline (any WER, however bad — the first number is what unlocks the
  bootstrapping loop) and the Week-7 v2 on the full corpus.
- Run the backbone comparison (XLS-R 300m vs MMS-1b vs w2v-BERT 2.0) and write down the decision.

**Week 1:** environment proven on toy data. **Week 4:** first real WER. **Week 7:** v2 + backbone decision.

---

## R9 · Model Engineer — Decoding & Language Model
**Backup:** R8

Owns everything between the acoustic model's output and the final text — where the cheapest wins live.

- Build the **text corpus** for the LM with R2's help. Target **≥1M words**. Start Week 1; this is
  independent of audio and nobody else is blocked by it.
- Train the **5-gram KenLM**; integrate `pyctcdecode` beam search; tune `alpha` / `beta` **on dev, never
  on test**. Expect **5–15 absolute WER points** for a few hours of CPU work — the best
  return-on-effort in the project.
- Run the **Whisper-small** comparison so the report covers both CTC and seq2seq. Note honestly where
  Whisper hallucinates.
- Build the **learning curve**: retrain at 1h / 2h / 5h / 10h / all, plot WER vs hours. This is the
  figure that answers "how much more data do we need?" and the one readers remember.
- Report every result as a pair — greedy and LM-decoded.

**Week 1:** text collection started. **Week 8:** measured LM delta. **Week 10:** learning curve.

---

## R10 · Evaluation, Demo & Documentation Lead
**Backup:** R1

Turns a working model into a defensible result. Undervalued by teams; heavily weighted by examiners.

- Build the **evaluation harness** in Week 2 — before there is a model. It should take a manifest plus
  predictions and emit WER, CER, sub/del/ins, and every slice from ARCHITECTURE §7d. Having it ready
  early means the Week-4 baseline is measurable the day it exists.
- Own the results tables in `reports/`. All slices: style, gender, age, dialect, source, duration,
  `label_origin`, plus `test-hard`.
- Run **error analysis** on the 50 worst dev clips **with R4**, categorized by cause. Expect ~⅓ to be
  label errors — feed those back to R5 as corrections. Finding them improves the corpus and the model
  at once.
- Build and deploy the **Gradio demo** on a free HF Space, with a greedy-vs-LM toggle so the difference
  is visible live.
- Write the **model card** and **dataset card**, including an honest limitations section.
- Own the final report's structure and the slide deck; chase section owners for their content.
- **Run the dress rehearsal in Week 12.** Live demos fail; find out in rehearsal, not in front of the panel.

**Week 2:** eval harness runs on dummy predictions. **Week 11:** demo live. **Week 12:** rehearsed.

---

## Assignment guidance

| Role | Needs most |
|------|-----------|
| R1 Lead | Follow-through and the willingness to chase people |
| R2 Acquisition | Resourcefulness; comfortable emailing strangers to ask permission |
| R3 Recording | Organization and social reach — must be able to recruit family and community |
| R4 Language | **Fluent Ekegusii** + patience for detail. Non-negotiable requirement. |
| R5 Transcription QA | Diplomacy; will be asking people to redo work |
| R6 Audio Pipeline | Solid Python; likes clean deterministic scripts |
| R7 Alignment | Strongest debugger — this role hits the most unfamiliar failure modes |
| R8 Baseline model | Comfortable with PyTorch/HF; tolerates crashed sessions |
| R9 Decoding/LM | Methodical; enjoys parameter sweeps and plots |
| R10 Eval & Docs | Writes clearly; sceptical by temperament; good at finding holes |

**If you have two fluent Ekegusii speakers, put the second at R5.** The Language Lead and the
Transcription QA Lead working side by side is the strongest pairing on the team, because it puts
linguistic authority directly next to where labels are produced.

**If someone drops out,** their backup absorbs the role and the universal quota is redistributed. Tell
R1 the day you know, not the week after.

---

## Weekly rhythm

| When | What |
|------|------|
| Monday | 30-min standup: done / blocked, two lines each. R1 posts the hours chart. |
| Mid-week | Quota check-in from R5. Anyone below 50% gets a direct message, not a public call-out. |
| Friday | Push everything. Nothing stays on a laptop over the weekend. |
| Friday | R1 updates the board and posts next week's gate. |

**The one number we watch every single week: hours of transcribed audio.** If it is not growing,
nothing else we do that week mattered.
