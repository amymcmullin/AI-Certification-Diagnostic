# Writing a question pack

Each diagnostic is one **pack**: a folder holding a `pack.json`. The engine, scoring and Teacher view are shared by every pack. To add a new subject you only write data.

```
packs/demo/pack.json                         public sample (this repo)
../cert-diagnostic-banks/ai/pack.json        real bank (private repo)
../cert-diagnostic-banks/networking/pack.json   future
```

## `pack.json`

```json
{
  "settings": {
    "id": "networking",
    "title": "Networking Certification Diagnostic",
    "eyebrow": "iTECH · Networking certification readiness",
    "heading": "Which networking exam are you ready for?",
    "intro": "",
    "minutes": 40,
    "review": "explain",
    "encode": true
  },
  "exams": {
    "NETP": { "name": "CompTIA Network+", "short": "Network+", "vendor": "CompTIA",
              "weights": { "CON": 0.23, "IMP": 0.20, "OPS": 0.19, "SEC": 0.14, "TRB": 0.24 } }
  },
  "topics": {
    "CON": { "name": "Networking Concepts",
             "study": "What to study for this topic, in one or two sentences.",
             "objectives": "Network+ 1.1–1.8" }
  },
  "items": [
    { "id": "CON1", "topic": "CON", "type": "mc",
      "stem": "Question text",
      "options": ["A", "B", "C", "D"],
      "answer": [2],
      "why": "Explanation shown in the review." }
  ]
}
```

(The weights above only show the format. Use the vendor's current published domain percentages.)

| Field | Notes |
|---|---|
| `settings.id` | Short, unique, letters, digits and dashes. It becomes the web address (`/networking/`) and is stamped into results codes. **Don't change it after students have taken the test.** |
| `settings.review` | `explain`, `full` or `none`. See [review modes](SCORING.md#review-modes). |
| `settings.encode` | `true` for real banks, `false` only for public samples. |
| `exams.<code>.weights` | The share of the exam each topic covers. Must add up to 1. A topic an exam doesn't test is left out. |
| `exams.<code>.short` | Label for table columns and legends. |
| `topics.<code>.study` | Appears in the student's study plan. |
| `items[].type` | `mc` (one answer) or `ma` (choose two, scored all-or-nothing). |
| `items[].answer` | Option indexes, counting from 0. Put correct answers in varied positions. |
| `items[].options` | At most 4. |

The build checks the pack (duplicate ids, unknown topics, weights that don't add up to 1, bad answer indexes) and stops with a list of any problems.

## Planning a new subject

1. **List the exams** that overlap. For networking, for example: CompTIA Network+, Cisco CCST Networking, IT Specialist: Networking.
2. **Collect each exam's official objectives** and domain percentages from the vendor's exam page.
3. **Define 8–12 shared topics** that cover all the objectives. Topics tested by several exams separate students less, and topics unique to one exam drive the recommendation, so you need both.
4. **Set the weights.** Use published domain percentages where they exist and spread them across your topics. Where none exist, estimate from the objectives and note it in the topic's `objectives` text.
5. **Write at least 3–4 items for each topic** (40–50 items total) so each topic score means something. Write original questions to the objectives. Don't copy vendor practice items.
6. **Build, test, and try it yourself:**
   ```bash
   python3 build/build.py ../cert-diagnostic-banks/networking
   node tests/test.js networking/index.html ../cert-diagnostic-banks/networking/pack.json
   ```
7. Commit the published folder to this repo and the pack to the private repo.

## Multi-domain single exams (A+, Tech+)

For one exam with official domains, the topics are the exam's domains and the weights are its domain percentages. A+ needs two exams, Core 1 and Core 2, in one pack. The engine already scores these. The report's "which exam" wording will be adjusted when the first single-exam pack is built.

## Changing a pack after students have tested

| Change | Old results codes | Canvas CSV import |
|---|---|---|
| Fix wording of a stem or option | still work | re-import the Canvas quiz |
| Change a key or an explanation | still work, rescored with the new key | re-import |
| Change topic weights or study text | still work | still works |
| Add, remove or reorder items | **stop working** | re-import |

To add or remove items, finish collecting the current term's codes first, or give the new version a new `id` (for example `ai-v2`).
