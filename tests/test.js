// Checks a built diagnostic: question data, key decoding, scoring, results codes,
// and the Canvas CSV import.
//
//   node tests/test.js demo/index.html packs/demo/pack.json
//   node tests/test.js ai/index.html ../cert-diagnostic-banks/ai/pack.json
//
// The pack file is the plain source, used to confirm that an encoded page
// decodes to exactly the right answers and explanations.
const fs = require("fs");
const vm = require("vm");
const assert = require("assert");

const [pagePath, packPath] = process.argv.slice(2);
if (!pagePath || !packPath) { console.error("usage: node tests/test.js <built page> <pack.json>"); process.exit(2); }
const html = fs.readFileSync(pagePath, "utf8");
const pack = JSON.parse(fs.readFileSync(packPath, "utf8"));
const js = html.match(/<script>([\s\S]*)<\/script>/)[1].replace(/\/\* ---------- boot[\s\S]*$/, "");
const sandbox = { document: { getElementById: () => ({}) }, location: { hash: "" }, btoa, atob, TextEncoder, TextDecoder };
vm.createContext(sandbox);
vm.runInContext(js + ";globalThis.__app={ITEMS,TOPICS,EXAMS,EXAM_KEYS,CFG,keyMask,score,makeCode,parseCodes,exampleCodes,parseCanvas,decodeWhy};", sandbox);
const { ITEMS, TOPICS, EXAMS, EXAM_KEYS, CFG, keyMask, score, makeCode, parseCodes, exampleCodes, parseCanvas, decodeWhy } = sandbox.__app;
const N = ITEMS.length;

// Published page matches the source pack
assert.strictEqual(N, pack.items.length);
assert.strictEqual(CFG.id, pack.settings.id);
if (pack.settings.encode) {
  assert.ok(!/"answer"\s*:/.test(html), "encoded page must not contain plain answers");
  assert.ok(!html.includes(pack.items[0].why), "encoded page must not contain plain explanations");
}
pack.items.forEach((src, i) => {
  assert.deepStrictEqual([...ITEMS[i].answer], src.answer, `${src.id}: decoded key`);
  assert.strictEqual(decodeWhy(ITEMS[i]), src.why, `${src.id}: decoded explanation`);
});
for (const e of EXAM_KEYS) {
  const sum = Object.values(EXAMS[e].weights).reduce((a, b) => a + b, 0);
  assert.ok(Math.abs(sum - 1) < 1e-9, `${e} weights add up to 1`);
}

// Scoring
const perfect = ITEMS.map(keyMask);
let r = score(perfect);
assert.strictEqual(r.total, N);
EXAM_KEYS.forEach(e => assert.strictEqual(r.exam[e], 100));
r = score(ITEMS.map(() => 0));
assert.strictEqual(r.total, 0);
const half = ITEMS.map(it => (it.type === "ma" ? 1 << it.answer[0] : keyMask(it)));
assert.strictEqual(score(half).total, ITEMS.filter(it => it.type === "mc").length, "choose-two needs both answers");

// Results codes
const code = makeCode({ name: "José O'Neil", period: "AM", date: "2026-10-01", minutes: 31, masks: perfect });
const parsed = parseCodes("pasted text " + code + " more text");
assert.strictEqual(parsed.rows.length, 1);
assert.strictEqual(parsed.rows[0].name, "José O'Neil");
assert.ok(parsed.rows[0].verified);
assert.strictEqual(score(parsed.rows[0].masks).total, N);
const tampered = code.slice(0, -1) + (code.endsWith("a") ? "b" : "a");
assert.strictEqual(parseCodes(tampered).rows[0].verified, false);
assert.strictEqual(parseCodes(exampleCodes()).rows.length, 6);
// A code from another diagnostic is skipped, not misread
const foreign = "AIDX-" + Buffer.from(["2", "other", "X", "", "2026-10-01", "5", "0".repeat(N)].join("~")).toString("base64url") + ".0000";
const pf = parseCodes(foreign);
assert.strictEqual(pf.rows.length, 0);
assert.strictEqual(pf.other, 1);

// Canvas Student Analysis CSV (mock in Canvas's column layout)
const q = v => '"' + String(v).replace(/"/g, '""') + '"';
const head = ["name", "id", "sis_id", "section", "section_id", "section_sis_id", "submitted", "attempt"];
ITEMS.forEach((it, i) => { head.push(`${400 + i}: ${it.stem}`); head.push("1.0"); });
head.push("n correct", "n incorrect", "score");
const row = ["Ana Ruiz", "1", "", "CSIT AM", "", "", "2026-10-02 09:14:00 UTC", "1"];
ITEMS.forEach((it, i) => { row.push(it.options[it.answer[0]]); row.push(i % 2 ? "1.0" : it.type === "ma" ? "0.5" : "0.0"); });
row.push("0", "0", "0");
const canvas = parseCanvas([head, row].map(r => r.map(q).join(",")).join("\n"));
assert.strictEqual(canvas.length, 1);
assert.strictEqual(canvas[0].matched, N);
assert.strictEqual(score(canvas[0].masks).total, Math.floor(N / 2), "partial credit counts as wrong");

console.log(`${CFG.id}: all tests passed (${N} questions, keys ${pack.settings.encode ? "encoded" : "public"}).`);
