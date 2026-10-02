# Certification Readiness Diagnostic

An open-source practice test engine for IT career and technical education. A student takes one diagnostic and gets back two things: **which of several related certification exams they are most likely to pass**, and **which topics to study first**. Teachers get a class view of the same results.

The first diagnostic covers three AI certifications:

| Exam | Vendor |
|---|---|
| Generative AI Foundations | Certiport / Pearson |
| Azure AI Fundamentals (AI-901) | Microsoft |
| IT Specialist: Artificial Intelligence | Certiport / Pearson |

Diagnostics for other subjects with overlapping certifications (networking, cloud) and for multi-domain exams (A+, Tech+) are planned.

**Live site:** https://amymcmullin.github.io/AI-Certification-Diagnostic/
- [AI Certification Diagnostic](https://amymcmullin.github.io/AI-Certification-Diagnostic/ai/): 45 questions, answer keys encoded
- [Demo](https://amymcmullin.github.io/AI-Certification-Diagnostic/demo/): 12 public sample questions, with answers shown after submitting
- Add `#teacher` to either address to open the Teacher view

## What it does

**For students**
- Questions and answer choices are shuffled for each student. Progress survives a page refresh. "Choose two" items need both answers right, like the real exams.
- The score report shows a readiness percentage for each exam, the recommended exam, a study plan ordered by how many points each topic is worth on that exam, and a score for every topic.
- An answer review, set by the teacher (see [review modes](docs/SCORING.md#review-modes)).
- A **results code** to turn in through Canvas or a form.

**For teachers**
- **Teacher view:** paste results codes, or a whole export that contains them, or open a Canvas Student Analysis CSV. You get class totals, a sortable student table, how many students are recommended for each exam, the two topics each student should study first, class topic averages, the most-missed questions, and a CSV export.
- **Canvas quiz package** (QTI 1.2) built from the same questions. See [docs/CANVAS.md](docs/CANVAS.md).
- Everything runs in the browser, with no server, no accounts, and no student data stored anywhere.

## How the answer keys are protected

This is an open-source tool, but the real question banks shouldn't hand students the answers.

| Part | Where it lives | Answers visible? |
|---|---|---|
| Engine, build scripts, docs | this public repo | n/a |
| Demo questions (`packs/demo`) | this public repo | yes, on purpose, to show how it works |
| Full question banks (`ai`, and future subjects) | a separate **private** repo | no |
| Published tests (`/ai/`, …) | GitHub Pages, from this repo | **encoded** |

When a private bank is published, each answer key is stored as a hash and each explanation is encoded, so the answers can't be read from the page source or found with a search. This stops casual answer-hunting. It is **not** secure against a determined student running code in the browser console. Any test that scores itself in the browser has that limit. For graded or high-stakes use, give the Canvas version, which Canvas scores on its server.

The Canvas package for a private bank contains the plain answer key. That's why it is written into the private repo, never into this one.

## Repository layout

```
engine/template.html     The app: layout, styles, scoring, Teacher view (one file, no dependencies)
build/build.py           Builds a pack into a published page, Canvas package and landing page
build/build_qti.py       Canvas QTI 1.2 builder
packs/demo/              Public sample pack (pack.json) and its builds
tests/test.js            Checks a built page against its source pack
index.html, catalog.json Landing page and the list of published diagnostics (generated)
ai/, demo/               Published diagnostics (generated; served by GitHub Pages)
docs/                    Scoring method, pack format, Canvas guide
```

## Building

Requires Python 3.9+ and Node 18+ (Node only for tests).

```bash
# public demo
python3 build/build.py packs/demo
node tests/test.js demo/index.html packs/demo/pack.json

# a private bank, cloned next to this repo
python3 build/build.py ../cert-diagnostic-banks/ai
node tests/test.js ai/index.html ../cert-diagnostic-banks/ai/pack.json
```

Then commit the generated `ai/` (or `demo/`) folder, `index.html` and `catalog.json` to this repo. Commit the pack and its `dist/` folder to the private repo.

To write a new diagnostic, see [docs/PACKS.md](docs/PACKS.md).

## Accuracy and limits

- Readiness percentages are estimates from this diagnostic, **not** official score predictions. The 75% "likely ready" line is an instructional judgment and will be adjusted against students' real exam results over time.
- Topic weights use vendor-published domain percentages where they exist (Microsoft publishes them for AI-901). Otherwise they are the author's estimates from the published objectives. See [docs/SCORING.md](docs/SCORING.md).
- Each results code belongs to one diagnostic and one version of its question bank. Adding or removing questions makes earlier codes unreadable.

## Licensing

- **Code** (engine, build scripts, tests, generated pages): [MIT](LICENSE).
- **Demo questions** in `packs/demo`: [CC BY-NC-SA 4.0](packs/demo/LICENSE.md). Free to share and adapt with credit, not for commercial use, under the same license.
- **Full question banks:** not in this repository. All rights reserved.
- **Trademarks:** this project is not affiliated with or endorsed by any exam vendor. See [TRADEMARKS.md](TRADEMARKS.md).

## Author

Amy McMullin, Computer Systems & Information Technology, Immokalee Technical College (iTECH), Collier County, Florida.
