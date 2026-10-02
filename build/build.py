"""Build a diagnostic from a question pack.

Usage (from the repo root):
    python3 build/build.py packs/demo
    python3 build/build.py ../cert-diagnostic-banks/ai      # a private pack

For each pack this writes:
    <id>/index.html                    the published test (served by GitHub Pages)
    <pack dir>/dist/<id>-artifact.html the same page without the html/head wrapper, for a Claude artifact
    <pack dir>/dist/<id>-canvas-qti.zip   Canvas quiz import (contains the answer key)
and refreshes catalog.json and the landing page (index.html).

A pack with "encode": true in its settings is published with hashed answer keys and
encoded explanations, so the answers can't be read from the page source. Its Canvas
package still holds the plain key, which is why it is written next to the private pack,
never into this public repo.
"""
import base64
import html
import json
import pathlib
import secrets
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_qti import build_qti  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENGINE = ROOT / "engine" / "template.html"
CATALOG = ROOT / "catalog.json"
REVIEW_MODES = {"full", "explain", "none"}

HEAD = (
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    "<style>body{margin:0}[hidden]{display:none!important}"
    "*,*::before,*::after{box-sizing:border-box}</style></head><body>"
)


# --- must match fnv() and stream() in engine/template.html ---
def fnv(s):
    h = 0x811C9DC5
    for ch in s:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def stream(seed):
    x = seed or 1
    while True:
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        yield x & 255


def encode_pack(pack):
    """Replace plain keys and explanations with a hash and an XOR encoding."""
    salt = secrets.token_hex(8)
    items = []
    for it in pack["items"]:
        mask = sum(1 << a for a in it["answer"])
        iid = it["id"]
        ks = stream(fnv(f"{salt}|w|{iid}"))
        why = bytes(b ^ next(ks) for b in it["why"].encode("utf-8"))
        enc = {k: v for k, v in it.items() if k not in ("answer", "why")}
        enc["k"] = "%08x" % fnv(f"{salt}|{iid}|{mask}")
        enc["w"] = base64.b64encode(why).decode("ascii")
        items.append(enc)
    return {**pack, "salt": salt, "items": items}


def validate(pack):
    s = pack.get("settings", {})
    errors = []
    if not s.get("id") or not s["id"].replace("-", "").isalnum():
        errors.append("settings.id must be letters, digits or dashes")
    if s.get("review", "explain") not in REVIEW_MODES:
        errors.append(f"settings.review must be one of {sorted(REVIEW_MODES)}")
    ids = set()
    for it in pack["items"]:
        if it["id"] in ids:
            errors.append(f"duplicate item id {it['id']}")
        ids.add(it["id"])
        if it["topic"] not in pack["topics"]:
            errors.append(f"{it['id']}: unknown topic {it['topic']}")
        if not all(0 <= a < len(it["options"]) for a in it["answer"]):
            errors.append(f"{it['id']}: answer index out of range")
        if (it["type"] == "ma") != (len(it["answer"]) > 1):
            errors.append(f"{it['id']}: type does not match number of answers")
        if len(it["options"]) > 4:
            errors.append(f"{it['id']}: at most 4 options (results codes store one hex digit per item)")
    for code, ex in pack["exams"].items():
        total = sum(ex["weights"].values())
        if abs(total - 1) > 1e-6:
            errors.append(f"exam {code}: weights add up to {total}, not 1")
        for t in ex["weights"]:
            if t not in pack["topics"]:
                errors.append(f"exam {code}: unknown topic {t}")
    if errors:
        sys.exit("Pack has problems:\n  " + "\n  ".join(errors))


def build(pack_dir):
    pack_dir = pathlib.Path(pack_dir).resolve()
    pack = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
    validate(pack)
    s = pack["settings"]
    pid = s["id"]

    published = encode_pack(pack) if s.get("encode") else pack
    body = ENGINE.read_text(encoding="utf-8").replace(
        "/*BANK*/null", json.dumps(published, ensure_ascii=False)
    )
    body = body.replace("<title>Certification Diagnostic</title>", f"<title>{html.escape(s.get('title', 'Certification Diagnostic'))}</title>", 1)

    site = ROOT / pid
    site.mkdir(exist_ok=True)
    (site / "index.html").write_text(HEAD + body + "</body></html>", encoding="utf-8")
    dist = pack_dir / "dist"
    dist.mkdir(exist_ok=True)
    (dist / f"{pid}-artifact.html").write_text(body, encoding="utf-8")
    n = build_qti(pack, dist / f"{pid}-canvas-qti.zip")

    catalog = json.loads(CATALOG.read_text()) if CATALOG.exists() else []
    catalog = [c for c in catalog if c["id"] != pid]
    catalog.append({
        "id": pid,
        "title": s.get("title", pid),
        "heading": s.get("heading", ""),
        "exams": [e["name"] for e in pack["exams"].values()],
        "questions": n,
        "minutes": s.get("minutes", 40),
        "public_keys": not s.get("encode", False),
    })
    catalog.sort(key=lambda c: (c["id"] == "demo", c["title"]))
    CATALOG.write_text(json.dumps(catalog, indent=1, ensure_ascii=False) + "\n")
    write_landing(catalog)
    print(f"{pid}: {n} questions -> {pid}/index.html, {dist.relative_to(pack_dir.parent)}/{pid}-canvas-qti.zip"
          + (" (keys encoded)" if s.get("encode") else " (keys public)"))


def write_landing(catalog):
    cards = "\n".join(
        f"""<article class="card"><div class="eyebrow">{c['questions']} questions · about {c['minutes']} min{' · sample' if c['public_keys'] else ''}</div>
<h2>{html.escape(c['title'])}</h2><p>{html.escape(' · '.join(c['exams']))}</p>
<p class="links"><a href="{c['id']}/">Take the diagnostic</a><a href="{c['id']}/#teacher">Teacher view</a></p></article>"""
        for c in catalog
    )
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Certification Readiness Diagnostics</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Bricolage+Grotesque:opsz,wght@12..96,800&family=JetBrains+Mono:wght@500&display=swap">
<style>
:root{{--bg:#F2F4F7;--surface:#FFF;--ink:#15212C;--muted:#56636F;--line:#D8DDE4;--accent:#2346A0;color-scheme:light}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0E151C;--surface:#16202A;--ink:#E5EBF1;--muted:#9AA8B5;--line:#2A3846;--accent:#93AAF2;color-scheme:dark}}}}
*{{box-sizing:border-box}}body{{margin:0;padding:0 16px;background:var(--bg);color:var(--ink);font:17px/1.55 "Atkinson Hyperlegible",system-ui,sans-serif}}
main{{max-width:780px;margin:0 auto;padding-block:40px 64px;display:flex;flex-direction:column;gap:20px}}
h1,h2{{font-family:"Bricolage Grotesque",system-ui,sans-serif;font-weight:800;line-height:1.15;margin:0;text-wrap:balance}}
h1{{font-size:clamp(1.9rem,5vw,2.6rem)}}h2{{font-size:1.35rem}}p{{margin:0}}
.eyebrow{{font-family:"JetBrains Mono",monospace;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}}
.card{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:20px;display:flex;flex-direction:column;gap:8px}}
.links{{display:flex;flex-wrap:wrap;gap:8px 20px;margin-top:4px}}a{{color:var(--accent);font-weight:700}}
footer{{font-size:.82rem;color:var(--muted);border-top:1px solid var(--line);padding-top:14px}}
</style></head><body><main>
<header style="display:flex;flex-direction:column;gap:10px"><div class="eyebrow">Open-source diagnostic</div><h1>Certification readiness diagnostics</h1>
<p style="color:var(--muted);max-width:62ch">Practice tests that show which certification exam a student is closest to passing and what to study first. Built for IT career and technical education.</p></header>
{cards}
<footer>Source code: MIT License. Sample questions: CC BY-NC-SA 4.0. Not affiliated with or endorsed by any exam vendor; exam names are trademarks of their owners. <a href="https://github.com/amymcmullin/AI-Certification-Diagnostic">GitHub</a></footer>
</main></body></html>
"""
    (ROOT / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for d in sys.argv[1:]:
        build(d)
