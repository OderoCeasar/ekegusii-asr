# START HERE — the project explained from zero

*No computer science needed to read this. If you have never heard of machine learning, this file is
written for you. Read it before anything else in the repo.*

---

## Part 1 — The problem, as a real scenario

**Moraa is 22, in Kisii town.** She wants to send her aunt a long message about a family meeting.
It's easier for her to *speak* it than to type it, and she'd rather say it in Ekegusii — that's how
her family actually talks.

So she opens WhatsApp, holds the microphone button, and speaks.

Now think about what her friend two seats away can do. That friend speaks English. She holds the
same button, speaks — and words appear on the screen. She reads them, fixes one, sends it. Thirty
seconds.

**Moraa can't do that.** There is a button for English. There is a button for Swahili. There is
nothing for Ekegusii. Two million people speak it, and the phone in her hand cannot write down a
single word of it.

That's the gap. We're going to close it.

---

## Part 2 — What we're building, in one sentence

> **Software that listens to Ekegusii and writes down what was said.**

If you've used voice typing on your phone, or seen automatic subtitles appear on a YouTube video —
that's the thing. It exists for maybe 100 languages out of 7,000. Ekegusii isn't one of them.

What it will look like when we're done: **a web page with a record button.** You press it, speak
Ekegusii, and text appears underneath. That's it. That's the demo we show.

The proper name for this kind of software is **ASR — Automatic Speech Recognition**. When you see
those three letters anywhere in this project, that's all they mean: *a computer writing down speech*.

---

## Part 3 — Who would actually use it

Four situations. These are what we say when someone asks "but why does this matter?"

**🏥 At the clinic.** An elderly woman explains her symptoms in Ekegusii. The clinical officer is from
Nakuru and speaks Swahili and English. Right now a relative has to translate, and details get lost.
With speech recognition, her words can at least be written down accurately — the first step to
anything else.

**📻 The radio archive.** A Kisii radio station has twenty years of recorded programmes sitting on
hard drives — interviews, debates, elders telling history. Nobody can find anything in it, because
you can only search *text*, not sound. Transcribe it and two decades of recordings become searchable
in an afternoon.

**📱 Typing on a phone.** Older speakers often speak Ekegusii fluently but type it slowly or not at
all. Voice input would let them message, search, and use services in their own language instead of a
second one.

**🎙️ Elders' stories.** Oral history is disappearing with the people who carry it. Recording is easy;
*writing it down* is the bottleneck, and it's why most recordings are never transcribed. This makes
that step cheap.

And underneath all four: **the dataset we build is permanent.** Even if our model is mediocre, the
collection of Ekegusii audio-with-text we create is the thing the next team — or a company, or a
university — builds on. It doesn't exist yet. After us, it will.

---

## Part 4 — How does a computer learn to hear a language?

This is the part that sounds like magic. It isn't. Here's the honest version.

### The subtitled-movie explanation

Imagine you want to learn Spanish, and your method is this: you watch **a thousand hours of Spanish
films with accurate Spanish subtitles.**

You hear a sound. At the same moment you see the written words. You don't understand at first. But
after hundreds of hours, your brain has quietly worked out the pattern: *that sound goes with those
letters.* Eventually you can hear a new Spanish sentence you've never heard before and write it down.

**That is exactly what we're doing to the computer.** We show it:

```
  [audio clip]  →  "nigo ngocha ase omobere"
  [audio clip]  →  "omong'ina nigo agenda"
  [audio clip]  →  "chinyomba chi bange"
      ...thousands of these...
```

The sound, and the matching words. Over and over. The computer finds the pattern on its own — we
never write rules like "the letter g sounds like this." We just supply the examples. The name for
this supply of examples is the **dataset**, and showing them to the computer is called **training**.

### So where's the problem?

**Nobody has ever made those subtitled examples for Ekegusii.**

That's the entire reason no Ekegusii speech tool exists. Not difficulty — *absence*. The methods are
free, published, and well known. The examples don't exist.

**So building that collection is our project.** The training part is a recipe we follow. The
collecting part is the real work.

---

## Part 5 — Why we don't need a thousand hours

A thousand hours would be impossible for ten students in one semester. We don't need it, because of
one trick.

**We don't start with an empty computer. We start with one that has already learned 128 other
languages.**

Researchers have already trained huge models on enormous amounts of speech in many languages, and
they give them away free. Think of that model as **a person who already speaks 128 languages and has
an extremely good ear.** It already knows what human speech physically is — vowels, consonants,
rhythm, where one word stops and the next begins.

It just doesn't know *ours*.

So our job is much smaller: sit that expert listener down with Ekegusii examples until it picks up
our language. Because it's already skilled, it needs about **10 to 15 hours** — not a thousand.

The technical name for this is **fine-tuning**. Whenever you see that word, it means: *take
someone else's trained model and teach it our specific thing.*

---

## Part 6 — How we'll actually do it, step by step

Six steps. Only one of them is hard.

### Step 1 — Get recordings of Ekegusii being spoken
From two places: things that already exist online (radio, YouTube, recorded publications), and things
we record ourselves on our phones — family, neighbours, church, friends.

### Step 2 — Write down what's said in them ⚠️ *the hard part*
This is the bottleneck. Typing out what you hear takes about **8–10 minutes of your time for every
1 minute of audio.** Done the obvious way, ten of us would each need ~90 hours of work to produce a
mere 10 hours of data. That would kill the project.

**So we cheat, twice:**

> **Cheat 1 — Use recordings whose words are already published.**
> Some Ekegusii recordings already have their exact text in print — audio scripture, recorded
> publications, read news bulletins. The words exist; we just don't know which *second* each word
> happens at. There's a free tool that works that out automatically. **It's the same job as syncing
> subtitles to a film.** Feed it a 40-minute recording plus the matching text, and it hands back
> hundreds of short labelled clips. **Nobody types anything.** This alone can give us 10+ hours in
> the first two weeks.
>
> **Cheat 2 — Find text, then read it aloud ourselves.**
> Ekegusii *text* is much easier to find than Ekegusii audio-with-text. So: collect any Ekegusii
> writing we can find, print it, and have people read it into a phone. Now we have audio **and** we
> already know exactly what was said — no transcription at all. This costs about 2–3 minutes per
> minute of audio instead of 8–10.
>
> **Cheat 3 — Let the half-trained model do the typing.**
> After a few weeks we'll have a rough model. It'll be bad, but not random. We run it over new audio,
> it produces a messy first draft, and we just **fix the mistakes** — 3–5× faster than typing from
> nothing. And every fix makes the model better, which makes the next round faster still.

### Step 3 — Tidy everything up
Chop long recordings into short clips (3–15 seconds). Make all audio the same format and volume. Make
spelling consistent. This is all done by scripts we run — nobody does it by hand.

### Step 4 — Train the model
Upload our data to a free borrowed computer with a powerful graphics card, run the training script,
wait a few hours. This is the part everyone imagines is the whole project. It's about 100 lines of
code that thousands of people have run before.

### Step 5 — Test it honestly
We hold back some recordings from voices the model has **never heard**, and see how it does on those.
The score is called **WER — Word Error Rate**. If the WER is 30%, it means roughly *3 words in every
10 are wrong.*

**Expect about 30–45% on clear speech.** That sounds bad. It isn't. For a language where nothing
exists at all, going from *nothing* to *most words right* is a real result. We are not competing with
Google's English.

### Step 6 — Build the demo
A web page with a record button. Free hosting. One afternoon's work.

---

## Part 7 — The must-have free tools

**Every single one of these is free. None of them needs a credit card.** This is the complete list of
what you'll actually touch.

### Accounts to create (do this today)

| Tool | What it actually is, in plain words | Why we need it |
|------|--------------------------------------|----------------|
| **Kaggle** | A company that lends you a powerful computer, free, over the web | Training needs a graphics card most laptops don't have. Kaggle gives **30 hours a week, free**. ⚠️ Verify your phone number or you won't get the GPU. |
| **Hugging Face** | A free website for sharing AI models and data — like GitHub, but for AI | Where we get the pretrained 128-language model, store our recordings, and host the final demo — all free |
| **GitHub** | A shared folder for code that tracks every change | So ten people can work without overwriting each other |
| **Google account** | Drive + Colab | Drive for staging files; Colab is a second free borrowed computer |

### Software we run

| Tool | What it actually is | Used in |
|------|---------------------|---------|
| **Python** | The programming language everything is written in | Everywhere |
| **ffmpeg** | A converter for audio and video files | Step 3 — making all audio the same format |
| **yt-dlp** | Downloads audio from websites | Step 1 — collecting found audio |
| **Silero VAD** | Detects where the silences are in a recording | Step 3 — chopping long audio into clips at natural pauses |
| **Forced aligner** | Syncs text to audio — the "subtitle syncing" tool | **Cheat 1.** The most important tool in the project. |
| **Hugging Face `transformers`** | The library that loads and trains the model | Step 4 |
| **`jiwer`** | Calculates the error rate | Step 5 — the score |
| **KenLM** | Learns which Ekegusii word sequences are plausible | Fixes many mistakes for free, no GPU needed |
| **Gradio** | Turns a Python script into a web page with buttons | Step 6 — the demo |
| **Audacity** | A free audio recorder and editor | Recording sessions, trimming |
| **Your phone's voice recorder** | Yes, really | Most of our own recordings |

**The model itself is also free:** `facebook/wav2vec2-xls-r-300m` — that's the "expert listener who
already knows 128 languages" from Part 5. Anyone can download it.

**Total project cost: zero shillings.**

---

## Part 8 — What this means for *you*, personally

Every week, whatever your specific role:

- **Transcribe or correct 60 minutes of audio.** Everyone does this, including the team lead.
- **Recruit at least one speaker** when there's a recording drive — family, neighbours, church,
  market. We need old and young, men and women, and people from different parts of Gusii. A dataset
  of ten young men only works for ten young men.
- **Two lines at the Monday standup:** what you finished, what's blocking you.

**If you get stuck, say so within 24 hours.** Someone quietly stuck for a week costs the group far
more than a wrong turn caught early. Nobody here is expected to already know how to do this.

---

## Part 9 — Questions you're probably about to ask

**"I don't know machine learning. Can I still contribute?"**
Yes — and more than you'd think. About **70% of this project is collecting and checking data**, which
needs care and language knowledge, not coding. The single most important person on this team is the
fluent Ekegusii speaker who decides how words get spelled. No ML required.

**"Has this ever actually worked for a language like ours?"**
Yes. This exact approach — take a big pretrained multilingual model, fine-tune it on a small local
dataset — is the standard method for low-resource languages, and it's been done for many African
languages. We're not inventing a technique. We're applying a known one to a language nobody has
bothered to apply it to.

**"What if the model turns out bad?"**
Then we report *how* bad, honestly, and explain why. A project that says "we got 58% WER on 2.5 hours,
here's exactly why, and here's what 15 hours would likely give" is a **good** project. Hiding a data
shortage behind a vague accuracy claim is not. Honest and small beats impressive and unverifiable.

**"How much work is this really?"**
About 1 hour of transcription per week, plus your role's tasks — realistically 3–5 hours a week.
The risk isn't that it's overwhelming; it's that it's easy to skip a week, and ten people skipping a
week each is the whole project.

**"Why does one person keep going on about an apostrophe?"**
Because in Ekegusii, `ng'` is a **single sound**, and the apostrophe is part of the letter — not
punctuation. Nearly every text-cleaning script on the internet deletes apostrophes automatically. If
that happens to us, every transcript is silently corrupted and we might not notice for a month. It's
the most likely disaster in the project, and there's already a test guarding against it.

---

## Where to go next

| You want | Read |
|---|---|
| The version to read out at a meeting | `docs/EXPLAIN.md` |
| The strategy, timeline and full tool list | `README.md` |
| Exactly which features we build, in order | `MVP.md` |
| Your specific job | `ROLES.md` |
| How the system is put together, technically | `ARCHITECTURE.md` |
| How to write transcripts consistently | `docs/TRANSCRIPTION_GUIDE.md` |
