# Scoring method

All scoring runs in the browser, in `engine/template.html` (`score`, `band`, `studyPlan`). The tables below use the AI diagnostic as the example. Each pack sets its own topics and weights in `pack.json`.

## 1. Item scoring

- **One-answer items (`mc`)** are correct when the student picks the keyed option.
- **Choose-two items (`ma`)** are correct only when the student picks exactly the two keyed options, with no partial credit. This matches how the certification exams score them. The page won't let a student pick more options than the item asks for.
- Unanswered items count as wrong.

## 2. Topic scores

The 45 items fall into 10 topics. A topic score is the share of that topic's items the student got right.

| Code | Topic | Items |
|---|---|---|
| FND | AI & Machine Learning Foundations | 4 |
| GEN | How Generative AI Works | 5 |
| PRM | Prompt Engineering & Refinement | 6 |
| CRT | Creating & Transforming Content | 3 |
| VER | Verifying Output & Limitations | 3 |
| ETH | Responsible AI, Ethics, Law & Privacy | 5 |
| AZR | Azure AI Services & Microsoft Foundry | 6 |
| DAT | Data Collection & Preparation | 5 |
| MOD | Model Training & Evaluation | 4 |
| OPS | Deployment, Monitoring & Lifecycle | 4 |

## 3. Exam readiness

Each exam assigns a weight to the topics it tests. The weights for each exam add up to 1.

```
readiness(exam) = round( 100 × Σ weight(exam, topic) × topicScore(topic) )
```

| Topic | GenAI Foundations | AI-901 | ITS AI |
|---|---|---|---|
| FND | 0.05 | 0.05 | 0.15 |
| GEN | 0.15 | 0.20 | – |
| PRM | 0.30 | 0.15 | – |
| CRT | 0.20 | – | – |
| VER | 0.10 | – | – |
| ETH | 0.20 | 0.15 | 0.10 |
| AZR | – | 0.45 | – |
| DAT | – | – | 0.30 |
| MOD | – | – | 0.25 |
| OPS | – | – | 0.20 |

How the weights were set:

- **Generative AI Foundations:** the four objective domains (Methods, Prompt Engineering, Prompt Refinement, Ethics/Law/Society), with prompting split across PRM and CRT. Certiport doesn't publish domain percentages.
- **AI-901:** Microsoft publishes 40–45% for "Identify AI concepts and capabilities" and 55–60% for "Implement AI solutions using Microsoft Foundry." The hands-on Foundry work maps mostly to AZR, and the concepts domain is split across GEN, ETH, PRM and FND.
- **ITS AI:** the five objective domains (Problem Definition; Data Collection, Processing & Engineering; Algorithms & Models; Integration & Deployment; Maintaining & Monitoring). Data and models carry the most weight, as they do in the sample items.

## 4. Readiness bands

| Readiness | Label | Meaning for the student |
|---|---|---|
| ≥ 75 | Likely ready | Take a full practice test, then schedule the exam |
| 60–74 | Almost there | Do a focused review of the study plan topics |
| 40–59 | Developing | Build these topics before scheduling |
| < 40 | Not yet | Needs instruction first |

The bands are set in `READY`, `CLOSE` and `DEV` at the top of the script.

## 5. Recommendation and study plan

- **Recommended exam** = the exam with the highest readiness. The report also names the runner-up and its score.
- **Study plan** = the topics the recommended exam tests where the student scored under 80%, sorted by `weight × (1 − topicScore)`. That is the share of exam readiness the student would gain by mastering the topic, so the most valuable topics come first.
- The Teacher view's "Study first" column shows the top two topics from each student's study plan.

## 6. Review modes

After submitting, students can review their answers. Each pack sets how much they see with `settings.review` in `pack.json`:

| Mode | Students see | Use when |
|---|---|---|
| `explain` (default) | Each answer marked right or wrong, their own choice, and the explanation. The correct option is **not** highlighted. | Everyday practice. Students learn from the attempt without keys spreading between class periods. |
| `full` | Everything in `explain`, plus the correct option highlighted in green | Public samples, or after every class has tested |
| `none` | Right or wrong and the topic only | You plan to go over the test in class, or students may retake it |

Change the setting in the pack, rebuild, and republish. Explanations sometimes name the answer, so `explain` limits sharing of the key but doesn't prevent it.

## 7. Encoded answer keys

Packs with `"encode": true` are published without plain answers:

- Each item's key is stored as `k = FNV-1a(salt | itemId | answerMask)`, written as 8 hex characters. A new random salt is made at each build.
- Each explanation is XOR-encoded with a keystream seeded from the salt and the item id, and decoded only when the review is shown.
- When the page loads, it recovers each key by trying the few possible answer combinations (at most 15 per item) against the hash.

This keeps answers out of the page source and out of text searches. It does not stop someone who runs code in the browser console, because no test that scores itself in the browser can. Use the Canvas version for graded attempts.

## 8. Results code format

```
AIDX-<base64url(payload)>.<check>
payload = 2~<pack id>~<name>~<class>~<YYYY-MM-DD>~<minutes>~<answers>
```

- `answers` has one hex character per item, in bank order. Each is a bitmask of the options the student picked, using the bank's original option order (before shuffling).
- `check` is a 4-character base-36 checksum (FNV-1a hash) of the payload. It catches hand-edited codes but is not a security measure.
- The Teacher view skips codes from a different diagnostic and reports how many it skipped.
- Codes from the first release (`1~…`, no pack id) are still read as belonging to the `ai` diagnostic.
- The Teacher view recomputes every score from the answers, so it always uses the current answer key and weights.
