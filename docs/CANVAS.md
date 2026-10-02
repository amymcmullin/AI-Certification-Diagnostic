# Using the diagnostic in Canvas

There are two ways to use it in Canvas.

## Option A: Canvas quiz (graded in Canvas)

### Import

1. Course → **Settings** → **Import Course Content**.
2. Content Type: **QTI .zip file**. Choose the pack's Canvas file: `<pack>/dist/<id>-canvas-qti.zip`. For the AI diagnostic that's `ai/dist/ai-canvas-qti.zip` in the private repo. For the public sample it's `packs/demo/dist/demo-canvas-qti.zip`.
3. Choose **All content** (or select the quiz) and click **Import**.
4. The quiz arrives in Quizzes under the pack's title, unpublished.

### Settings the package sets

| Setting | Value |
|---|---|
| Questions | All items in the pack, 1 point each, ordered by topic |
| Shuffle answers | On |
| Time limit | The pack's `minutes` + 5 |
| Allowed attempts | 1 |
| Show correct answers | Off |

Each question's title starts with its number and topic (e.g. `Q12 Prompt Engineering & Refinement`), and each has the explanation set as general feedback. Turn on **Let students see their quiz responses** after the due date if you want them to see the explanations.

### Getting the readiness report

1. Open the quiz → **Quiz Statistics** → **Student Analysis** → download the CSV.
2. Open the web page's **Teacher view** and click **Open a .csv or .txt file**, or paste the CSV text.
3. The page matches each question column to the question bank by its text and reads the points earned. It reports how many of the questions it matched.

Notes:

- **Partial credit:** Canvas gives partial credit on multiple-answer ("choose two") questions. The Teacher view counts an item as correct only with full credit, matching the real exams. That's why its scores can be slightly lower than the Canvas gradebook.
- **Matching by text:** if you edit a question's wording in Canvas, the import can't match it. Edit the pack's `pack.json` and rebuild instead, so both versions stay the same.
- The import was built for the Classic Quizzes Student Analysis report.

## Option B: Web page with results codes

1. Link to the diagnostic on GitHub Pages (for example `…/AI-Certification-Diagnostic/ai/`) from a module, or upload the built `index.html` to Canvas Files.
2. Create a Canvas assignment (text entry, or a discussion) titled something like "AI Diagnostic results code."
3. Students take the test, copy their `AIDX-…` code from the score report, and submit it.
4. Download the submissions, or copy the codes from SpeedGrader. Paste them all into the **Teacher view**. Surrounding text is fine, because the page finds the codes inside it.

The Canvas package holds the plain answer key. Keep it in the private repo and don't post it where students can download it.

Option B gives students the full score report and study plan right away. Option A keeps grades in Canvas.
