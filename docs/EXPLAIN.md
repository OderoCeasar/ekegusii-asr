# The project in plain language

*For the first team meeting. Read it out, or paste it in the group.*

---

## The one-paragraph version

We're building software that listens to someone speaking Ekegusii and writes down what they
said — like the voice typing on your phone, which works for English and Swahili but not for our
language. About 2 million people speak Ekegusii and there is currently **no working tool that can
do this**. We're going to build the first one.

## Why doesn't it exist already?

Not because it's impossible. The code and the methods are free and public — people have done this
for other languages. It doesn't exist because **nobody has ever collected the data**. A computer
can only learn Ekegusii if you show it thousands of examples of "here is some audio, and here is
exactly what was said in it." Nobody has ever sat down and made that collection.

**So that collection is the project.** We build it, then we use it to teach the computer.

## How it actually works — the simple version

Think of it like teaching a person.

**We are not teaching a baby.** If we were starting from nothing, we'd need thousands of hours of
recordings — impossible for us. Instead we start with a model that has already been trained on
hundreds of thousands of hours of speech in about 128 other languages. Think of it as someone who
already speaks many languages fluently and has an excellent ear. It already knows what human speech
*sounds* like — vowels, consonants, rhythm, where words end. **It just doesn't know Ekegusii yet.**

Our job is to sit that "person" down with Ekegusii examples until it picks up our language. Because
it's already a skilled listener, it only needs about **10–15 hours** of Ekegusii, not thousands.

That's what "fine-tuning a pretrained model" means. That's the whole idea.

## So what will we actually be doing?

Five things, and only one of them is hard:

1. **Gather recordings of people speaking Ekegusii.** Radio, YouTube, church recordings, and our own
   recordings of family and friends on our phones.
2. **Write down what is said in them.** ← *This is the hard part. Most of our time goes here.*
3. **Clean it up.** Chop long recordings into short clips, make the audio uniform, make the spelling
   consistent. Scripted, automatic.
4. **Train the model.** Free GPUs on Kaggle. A few hours per run.
5. **Test it and build a demo** — a web page with a record button that prints what you said.

## "Writing down hours of audio" sounds brutal. It is. Here's how we avoid most of it.

Transcribing from scratch takes roughly **8–10 minutes of your time per 1 minute of audio**. If ten
of us did it the obvious way, we'd each need ~90 hours of work just to get 10 hours of data. That
would kill the project. So we use two tricks:

**Trick 1 — Use recordings where the words are already written down somewhere.**
Some Ekegusii recordings already have published text: audio scripture, recorded publications, read
news. The words already exist in print — we just don't know *which second* each word happens at.
There is a free tool that figures that out automatically. It's like software that syncs subtitles to
a movie. Feed it a 40-minute recording plus the text, and it hands back hundreds of short labelled
clips. **Zero typing.** This can give us 10+ hours in the first two weeks.

**Trick 2 — Let the model do the typing once it's half-trained.**
After a few weeks we'll have a rough model. It won't be good, but it won't be random either. We run
it over new audio and it produces a messy first draft. Then we just **fix the mistakes** instead of
typing from scratch — about 3–5× faster. And every correction makes the model better, which makes
the next round of corrections faster still.

## What does success look like?

Be realistic, so nobody panics later: our model will get roughly **1 word in 3 wrong** on clear
speech, and more on fast conversation. That sounds bad. It is **not** a failure.

For a language where nothing exists at all, a working model plus a public dataset is a real
contribution — the kind of thing people cite and build on. We are not competing with Google's
English. We are going from **nothing** to **something**, and nobody has done that for Ekegusii.

## What everyone has to do, every week

- **Transcribe or correct 60 minutes of audio.** Everyone, including the team lead. No exceptions.
- **Recruit speakers** — family, neighbours, church, market. We need old and young, men and women,
  and people from different parts of Gusii. A dataset of ten young men only works for ten young men.
- **Say something at the Monday standup**: what you finished, what's blocking you. Two lines.

**If you're stuck, say so within 24 hours.** Someone quietly stuck for a week costs us far more than
a wrong turn caught early.

## The one number we watch

**Hours of transcribed audio.** It goes on a chart, updated weekly, posted in the group. If that
number isn't growing, nothing else we did that week mattered.

---

**Full details:** `README.md` (strategy and plan) · `ARCHITECTURE.md` (technical design) ·
`ROLES.md` (your specific job)
