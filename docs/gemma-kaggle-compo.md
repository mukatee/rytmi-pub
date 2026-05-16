# Gemma 4 Good Hackathon — Working Competition Reference

> Purpose: a reusable reference file for this repo so future AI-assisted coding sessions can quickly understand the competition’s goals, constraints, and submission expectations.

- **Competition:** [The Gemma 4 Good Hackathon](https://www.kaggle.com/competitions/gemma-4-good-hackathon)
- **Host:** Google DeepMind
- **Prize Pool:** **$200,000**
- **Timeline:** **Start:** April 2, 2026 · **Final submission deadline:** May 18, 2026 at 11:59 PM UTC
- **Last updated in this file:** 2026-04-11
- **Source basis:** public Kaggle `Overview` and `Data` pages
- **Related living repo brief:** `docs/project-vision.md` for the evolving project-specific direction and lessons learned

---

## 1) Competition in one paragraph

This Kaggle hackathon is about building a **real-world, positive-impact solution using Gemma 4**. The organizers want either a working app or a specialized model that clearly solves an important problem and demonstrates meaningful practical value. This is **not a standard leaderboard-first prediction contest**; it is much closer to a **product + demo + technical proof** challenge, where the strongest submissions combine a compelling story, visible real-world usefulness, and credible engineering.

---

## 2) Official goal

### Core mission
Create a solution that addresses a **real-world challenge** using **Gemma 4 models**, whether that is:
- an application that could help many people, or
- a specialized model or workflow that could unlock impact in a focused domain.

### What the organizers explicitly emphasize
- **Positive change / global impact**
- **Local or edge intelligence**
- **Native function calling**
- **Multimodal understanding**
- **Post-training / domain adaptation / retrieval / grounding**
- Real, working implementations rather than concept-only demos

### Theme areas highlighted by Kaggle
- **Health & Sciences**
- **Global Resilience**
- **Future of Education**
- **Digital Equity & Inclusivity**
- **Safety & Trust**

---

## 3) What actually wins here

The competition page makes this very clear:

1. **Tell a strong story**
   - Show the problem clearly.
   - Show why it matters.
   - Show why your Gemma 4 solution is a strong answer.

2. **Deliver a compelling demo video**
   - The video is the most important presentation asset.
   - It should show the product in action and create a genuine “wow” factor.

3. **Back the story with real engineering**
   - Public code repo
   - Kaggle writeup
   - Live demo or demo files if applicable
   - Technical explanation proving the system is real

> Practical takeaway: this hackathon rewards **impact + clarity + demonstration quality** as much as raw model sophistication.

---

## 4) Submission requirements

A valid submission must be a **Kaggle Writeup** with required supporting assets.

| Required item | What it needs to include | Notes |
|---|---|---|
| **Kaggle Writeup** | Project summary, technical explanation, track selection | Should act as the main technical proof of work |
| **Public video** | YouTube link, **3 minutes or less** | This is the most important part of the submission |
| **Public code repository** | Public GitHub/Kaggle Notebook/etc. | Must clearly show how Gemma 4 is used |
| **Live demo** | Public URL or demo files | Lets judges interact with or inspect the project |
| **Media gallery** | Images and/or video assets | A cover image is required |

### Writeup expectations
- Explain the architecture of the app/system
- Explain **how Gemma 4 is specifically used**
- Describe challenges and technical choices
- Provide links to supporting assets
- Select a submission track
- Keep the writeup to **1,500 words or fewer**

### Additional notes from the competition page
- Each team can submit **one writeup**
- The writeup can be unsubmitted/edited/resubmitted before the deadline
- If private Kaggle resources are attached to a public writeup, they may become public after the deadline
- If training a model, organizers ask participants to **publish weights and benchmarks**
- If building an app, participants should **explain the architecture and demonstrate real-world utility**

---

## 5) Evaluation rubric

Submissions are judged primarily through the **video demo**, then validated through the writeup and repo.

| Criterion | Points | What it means |
|---|---:|---|
| **Impact & Vision** | **40** | Does the project address a meaningful real-world problem and have believable positive impact? |
| **Video Pitch & Storytelling** | **30** | Is the demo exciting, clear, compelling, and well presented? |
| **Technical Depth & Execution** | **30** | Is the Gemma 4 usage real, functional, innovative, and well engineered? |

### Key interpretation
This is effectively a **show-your-working product hackathon**, not a hidden-test-score optimization contest.

---

## 6) Tracks and awards

### Main Track — **$100,000**
- **1st:** $50,000
- **2nd:** $25,000
- **3rd:** $15,000
- **4th:** $10,000

### Impact Track — **$50,000 total**
Five prizes of **$10,000** each:
- Health & Sciences
- Global Resilience
- Future of Education
- Digital Equity & Inclusivity
- Safety & Trust

### Special Technology Track — **$50,000 total**
Five prizes of **$10,000** each:
- **Cactus** — local-first mobile or wearable app with intelligent task routing
- **LiteRT** — best use of Google AI Edge’s LiteRT implementation of Gemma 4
- **llama.cpp** — strongest Gemma 4 implementation on resource-constrained hardware
- **Ollama** — best project showcasing Gemma 4 locally via Ollama
- **Unsloth** — best fine-tuned Gemma 4 model for a specific impactful task

> A project may be eligible for both a **Main Track** prize and a **Special Technology** prize.

---

## 7) Data description

### Important: this competition does **not** provide a real benchmark dataset
According to the Kaggle `Data` page:
- the competition includes **no provided dataset** for training/evaluation,
- the data tab only contains a tiny `NOTE.md`,
- the challenge is therefore centered on **building and presenting a solution**, not competing on a shared held-out dataset.

### What this implies for project planning
- You will likely need to use:
  - your own dataset,
  - public/open datasets,
  - generated or curated evaluation examples,
  - or a live/interactive demo workflow.
- You should keep careful notes about:
  - data sources,
  - licenses/permissions,
  - evaluation methodology,
  - and reproducibility.

### For this repo specifically
This repo already contains audio/music-related samples and analysis code. That means the project can likely position itself as a:
- **music / rhythm learning assistant**,
- **education-focused audio coach**,
- **accessible local-first creative tool**, or
- **multimodal rhythm analysis + explanation system**
using Gemma 4 as the explanation, reasoning, tutoring, or retrieval layer.

---

## 8) Gemma 4 usage expectations

The overview text strongly suggests judges want Gemma 4 to be **central**, not just lightly attached.

Good signs for a strong submission:
- Gemma 4 is visibly involved in the user workflow
- The model improves reasoning, tutoring, explanation, summarization, multimodal interpretation, or agent behavior
- Any retrieval or adaptation steps are clearly documented
- The repo/demo makes it obvious why **Gemma 4** is a better fit than a generic baseline

Weak positioning to avoid:
- Gemma 4 only appears as a token API call with no real product value
- the system could work identically without Gemma 4
- no clear demo of user impact or technical credibility

---

## 9) Useful project framing ideas for `kaggle-gemma4-rytmi`

These are **project-fit ideas**, not official competition text.

### Strong possible angles
1. **Future of Education**
   - Build a rhythm/music tutor that explains timing, groove, meter, and practice feedback in plain language.
2. **Digital Equity & Inclusivity**
   - Make a local-first music learning assistant that works with limited connectivity and supports multiple languages.
3. **Safety & Trust**
   - Emphasize transparent explanations of how rhythm judgments are produced from audio features.
4. **Cactus / Ollama / llama.cpp / LiteRT**
   - If the app runs locally on constrained hardware, it may also fit a Special Technology Track.

### Good narrative hook
A strong story for this repo could be:
> “Use local audio analysis plus Gemma 4 reasoning to help people understand rhythm, timing, and practice feedback in an accessible, engaging way.”

---

## 10) Recommended deliverables for this repo

To align this project with the competition, aim for:
- a working demo app or notebook flow
- clear evidence of Gemma 4 in the core loop
- a small but believable evaluation/demo scenario
- a concise project architecture diagram
- a public repository with setup instructions
- a short, polished 3-minute demo video outline
- a Kaggle writeup draft tailored to the scoring rubric

---

## 11) Suggested “definition of done” for a competition-ready version

A solid submission from this repo should be able to answer **yes** to all of these:

- Does it solve a real problem, not just a toy ML task?
- Is Gemma 4 central to the experience?
- Can the value be understood within the first 30–60 seconds of a demo video?
- Is there a real working prototype?
- Is the code public and understandable?
- Is the writeup clear about architecture, data, and limitations?
- Is the impact story memorable?

---

## 12) Citation / source note

Competition citation from Kaggle:

> Ian Ballantyne, Glenn Cameron, María Cruz, Olivier Lacombe, Kristen Quan, and Omar Sanseviero. *The Gemma 4 Good Hackathon*. Kaggle, 2026. https://kaggle.com/competitions/gemma-4-good-hackathon

---

## 13) Quick-reference summary for future AI coding sessions

When using AI tools for this repo, assume the project should optimize for:
- **real-world impact**,
- **clear Gemma 4 integration**,
- **demo quality**,
- **educational / inclusive value**,
- **local-first practicality where possible**, and
- **a strong narrative backed by real implementation**.

In short:

> **This competition is about building a believable, inspiring, technically real Gemma 4 project with a strong story — not just chasing a benchmark score.**
