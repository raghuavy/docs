"""Build the EE 8350 guide website from the lecture guide markdown.

Usage:  python3 _src/build.py
Needs:  pip install markdown latex2mathml

Reads   EE 8350_Lecture_Guide.md
Writes  index.html and lectures/*.html
Content added on top of the markdown lives in _src/pseudocode.py and _src/visuals.py.
"""
import html
import json
import re
import sys
from pathlib import Path

import markdown
from latex2mathml.converter import convert as tex_to_mathml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pseudocode import PSEUDO  # noqa: E402
from visuals import FIGURES, ARROW_DEFS, course_map  # noqa: E402
from problems import PROBLEMS  # noqa: E402

SOURCE = ROOT / "EE 8350_Lecture_Guide.md"

# Lecture key (section order in the markdown, intro is L1) -> file slug
SLUGS = {
    "L2": "01-systemverilog-review",
    "L3": "02-oop",
    "L4": "03-randomization",
    "L5": "04-coverage-basics",
    "L6": "05-interfaces",
    "L7": "06-07-threads",
    "L8": "08-uvm",
    "L9": "09-11-advanced-oop",
    "L10": "10-assertions-basics",
    "L11": "12-uvm-adder",
    "L12": "12-advanced-interfaces",
    "L13": "13-14-coverage-in-depth",
    "L14": "14-16-advanced-assertions",
    "L15": "16-18-sva",
    "L16": "19-clock-domain-crossing",
}

MD_EXT = ["md_in_html", "sane_lists"]


def md(text):
    return markdown.markdown(text, extensions=MD_EXT)


def md_inline(text):
    out = md(text).strip()
    m = re.fullmatch(r"<p>(.*)</p>", out, flags=re.S)
    return m.group(1) if m else out


def code_html(code):
    esc = html.escape(code)
    esc = re.sub(r"(//[^\n]*)", r'<span class="c">\1</span>', esc)
    return f"<pre><code>{esc}</code></pre>"


PAGE_LIST = []  # (root relative path, label), filled in build()


def page(title, body, depth, note_key, prev_link=None, next_link=None):
    up = "../" * depth
    pager = ""
    if prev_link or next_link:
        parts = []
        if prev_link:
            parts.append(f'<a class="prev" href="{prev_link[0]}"><span class="dir">Previous</span>{html.escape(prev_link[1])}</a>')
        else:
            parts.append('<span style="flex:1"></span>')
        if next_link:
            parts.append(f'<a class="next" href="{next_link[0]}"><span class="dir">Next</span>{html.escape(next_link[1])}</a>')
        else:
            parts.append('<span style="flex:1"></span>')
        pager = '<nav class="pager" aria-label="Lecture navigation">' + "".join(parts) + "</nav>"
    options = "".join(f'<option value="{up}{path}">{html.escape(label)}</option>' for path, label in PAGE_LIST)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<script>(function(){{var d=document.documentElement;try{{var s=localStorage.getItem("ee8350-size");if(s)d.setAttribute("data-size",s);var t=localStorage.getItem("ee8350-theme");if(t==="light"||t==="dark")d.setAttribute("data-theme",t);var sp=localStorage.getItem("ee8350-split");if(sp===null)sp=window.innerWidth>=1000?"on":"off";if(sp==="on"&&window.innerWidth>=1000)d.classList.add("split");var w=localStorage.getItem("ee8350-splitw");if(w)d.style.setProperty("--split-w",w+"%");}}catch(e){{}}if(window.self!==window.top){{d.classList.add("embedded");d.classList.remove("split");}}}})();</script>
<link rel="icon" href="data:,">
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to the content</a>
<header class="site">
  <a class="home" href="{up}index.html">EE 8350 Guide</a>
  <div class="controls">
    <div class="ctl sizer" role="group" aria-label="Text size">
      <span class="ctl-label">Text</span>
      <button type="button" data-size="1" aria-label="Smaller text">A</button>
      <button type="button" data-size="2" aria-label="Normal text">A</button>
      <button type="button" data-size="3" aria-label="Larger text">A</button>
    </div>
    <div class="ctl themer" role="group" aria-label="Color theme">
      <span class="ctl-label">Theme</span>
      <button type="button" data-theme-set="light">Light</button>
      <button type="button" data-theme-set="dark">Dark</button>
      <button type="button" data-theme-set="auto">Auto</button>
    </div>
    <button type="button" class="split-btn" aria-pressed="false">Split view</button>
  </div>
</header>
{ARROW_DEFS}
<div class="layout" id="layout">
<div class="pane-main" id="paneMain">
<main id="main">
{body}
</main>
{pager}
<footer class="site">Study guide for EE 8350, Advanced Verification Methodologies for VLSI Systems. Built from the lecture slides, chapters 1 to 19. Notes and progress are saved only in this browser.</footer>
</div>
<div class="divider" id="divider" role="separator" aria-orientation="vertical" aria-label="Drag to resize the two panes" tabindex="0"></div>
<aside class="pane-side" id="paneSide" aria-label="Side pane">
  <div class="side-bar">
    <div class="seg" role="tablist" aria-label="Side pane shows">
      <button type="button" role="tab" data-mode="notes" aria-selected="true">Notes</button>
      <button type="button" role="tab" data-mode="page" aria-selected="false">Another page</button>
    </div>
    <button type="button" class="side-close">Close</button>
  </div>
  <section class="side-notes" data-panel="notes">
    <div class="side-tools">
      <span class="note-status" aria-live="polite">Notes for this page, saved in this browser</span>
      <span class="tool-btns"><button type="button" class="note-dl">Download</button><button type="button" class="note-clear">Clear</button></span>
    </div>
    <textarea class="notes" data-indent="notes" data-key="{note_key}" aria-label="Notes for this page" spellcheck="true"
      placeholder="Type notes here.&#10;&#10;Enter keeps your indent. A line ending in : indents the next one.&#10;Tab indents, Shift+Tab outdents.&#10;Lines starting with - or 1. keep the list going.&#10;Press Esc, then Tab, to leave the box."></textarea>
  </section>
  <section class="side-page" data-panel="page" hidden>
    <label class="side-pick">Show <select id="pagePick">{options}</select></label>
    <iframe id="sideFrame" title="Another page of the guide"></iframe>
  </section>
</aside>
</div>
<script src="{up}assets/site.js"></script>
</body>
</html>
"""


def split_sections(text):
    lines = text.split("\n")
    sections = []
    cur = None
    for line in lines:
        if line.startswith("## "):
            cur = {"title": line[3:].strip(), "lines": []}
            sections.append(cur)
        elif cur is not None:
            cur["lines"].append(line)
    for s in sections:
        s["body"] = "\n".join(s["lines"]).strip("\n")
    return sections


def extract_code(body, key, store):
    """Replace fenced code with placeholders. SystemVerilog gets pseudocode first."""
    out, buf, lang, inside, n_sv = [], [], "", False, 0
    for line in body.split("\n"):
        if line.startswith("```"):
            if not inside:
                inside, lang, buf = True, line[3:].strip(), []
                continue
            inside = False
            code = "\n".join(buf)
            if lang == "systemverilog":
                n_sv += 1
                pk = f"{key}-{n_sv}"
                pseudo = PSEUDO.get(pk)
                if pseudo is None:
                    raise SystemExit(f"missing pseudocode for {pk}")
                frag = (
                    '<div class="pair">'
                    f'<div class="pseudo"><div class="label">Pseudocode</div><pre>{html.escape(pseudo.strip())}</pre></div>'
                    f'<details class="code"><summary>Show the SystemVerilog</summary>{code_html(code)}</details>'
                    "</div>"
                )
            elif lang == "latex":
                frag = tex_to_mathml(code.strip(), display="block")
            else:
                frag = f'<div class="cmd"><span class="label">Command</span>{code_html(code)}</div>'
            store.append(frag)
            out += ["", f"XXBLOCK{len(store) - 1}XX", ""]
            continue
        if inside:
            buf.append(line)
        else:
            out.append(line)
    return "\n".join(out)


def insert_figures(body, key, store):
    lines = body.split("\n")
    for (fkey, anchor), figs in FIGURES.items():
        if fkey != key:
            continue
        frag = "".join(figs)
        if anchor == "embed":
            for i, line in enumerate(lines):
                if "embedded content" in line:
                    store.append(frag)
                    lines[i] = f"XXBLOCK{len(store) - 1}XX"
                    break
            else:
                raise SystemExit(f"no embed line in {key}")
            continue
        idx = next((i for i, l in enumerate(lines) if l.startswith(f"### {anchor}.") or l.strip() == f"### {anchor}"), None)
        if idx is None:
            raise SystemExit(f"no heading {anchor} in {key}")
        # after the first paragraph that follows the heading
        j = idx + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        while j < len(lines) and lines[j].strip():
            j += 1
        store.append(frag)
        lines[j:j] = ["", f"XXBLOCK{len(store) - 1}XX", ""]
    return "\n".join(lines)


def difficulty(i, n):
    if i < round(n * 0.4):
        return "Easy"
    if i < round(n * 0.75):
        return "Medium"
    return "Hard"


def answer_inputs(pid, spec):
    t = spec["t"]
    if t in ("fields", "custom"):
        rows = []
        for k, f in enumerate(spec["f"]):
            fid = f"{pid}-f{k}"
            if f.get("opt"):
                opts = '<option value="">choose</option>' + "".join(
                    f'<option value="{html.escape(o)}">{html.escape(o)}</option>' for o in f["opt"])
                ctl = f'<select id="{fid}" data-k="{k}">{opts}</select>'
            else:
                ctl = f'<input id="{fid}" data-k="{k}" type="text" autocomplete="off" spellcheck="false">'
            rows.append(f'<div class="fld"><label for="{fid}">{html.escape(f["l"])}</label>{ctl}</div>')
        return '<div class="fields">' + "".join(rows) + "</div>"
    if t in ("choice", "multi"):
        kind = "radio" if t == "choice" else "checkbox"
        rows = "".join(
            f'<label class="opt"><input type="{kind}" name="{pid}" value="{k}"><span>{html.escape(o)}</span></label>'
            for k, o in enumerate(spec["o"]))
        return f'<fieldset class="opts"><legend class="sr">Options</legend>{rows}</fieldset>'
    if t == "order":
        return (f'<div class="fields"><div class="fld wide"><label for="{pid}-f0">Your order</label>'
                f'<input id="{pid}-f0" data-k="0" type="text" autocomplete="off" spellcheck="false" '
                'placeholder="first, second, third, ..."></div></div>')
    if t == "code":
        return (f'<div class="editor code-ed"><pre class="gutter" aria-hidden="true">1</pre>'
                f'<textarea data-indent="code" data-key="ans-{pid}" spellcheck="false" aria-label="Your code" '
                'placeholder="Write your SystemVerilog here. Enter keeps the indent, Tab indents."></textarea></div>')
    return (f'<div class="editor prose-ed"><textarea data-indent="notes" data-key="ans-{pid}" aria-label="Your answer" '
            'placeholder="Write your answer in your own words."></textarea></div>')


def build_practice(body, key):
    """Turn the Practice and Answers lists into a LeetCode style problem set."""
    if "### Practice" not in body or "### Answers" not in body:
        return body
    head, rest = body.split("### Practice", 1)
    practice, answers = rest.split("### Answers", 1)

    def items(text):
        found, tail = [], []
        for line in text.strip().split("\n"):
            m = re.match(r"^(\d+)\.\s+(.*)$", line)
            if m:
                found.append([m.group(2)])
            elif line.strip():
                (tail if not found or line.startswith("XXBLOCK") else found[-1]).append(line)
        return found, tail

    qs, _ = items(practice)
    ans, extra = items(answers)
    if extra:
        target = next((i for i in range(len(ans) - 1, -1, -1) if "below" in " ".join(ans[i])), len(ans) - 1)
        ans[target] += extra
    specs = PROBLEMS[key]
    if len(specs) != len(qs) or len(ans) != len(qs):
        raise SystemExit(f"{key}: {len(qs)} questions, {len(ans)} answers, {len(specs)} problem specs")
    n = len(qs)
    rows, panels = [], []
    for i, (q, a, (title, spec)) in enumerate(zip(qs, ans, specs)):
        pid = f"p-{key}-{i + 1}"
        diff = difficulty(i, n)
        dcls = diff.lower()
        rows.append(
            f'<li><button type="button" class="prob-row" data-i="{i}" aria-controls="{pid}">'
            f'<span class="pnum">{i + 1}.</span><span class="ptitle">{html.escape(title)}</span>'
            f'<span class="diff {dcls}">{diff}</span><span class="pstat" aria-label="not solved yet"></span></button></li>'
        )
        statement = md_inline(" ".join(q))
        extra_q = spec.get("q", "")
        if spec["t"] == "order":
            extra_q = "Type the names in order, separated by commas."
        if spec["t"] == "multi" and not extra_q:
            extra_q = "Select every option that applies."
        if spec["t"] in ("code", "explain"):
            extra_q = "Write your answer, press Submit, then compare with the reference solution and mark it."
        sol = md("\n\n".join(a)).replace('<details class="code">', '<details class="code" open>')
        panels.append(
            f'<div class="prob" id="{pid}" data-i="{i}" data-id="{pid}" '
            f'data-check="{html.escape(json.dumps(spec), quote=True)}">'
            f'<div class="prob-title"><h4>{i + 1}. {html.escape(title)}</h4><span class="diff {dcls}">{diff}</span></div>'
            f'<div class="prob-statement"><p>{statement}</p>' + (f'<p class="hint">{extra_q}</p>' if extra_q else "") + "</div>"
            + answer_inputs(pid, spec)
            + '<div class="prob-actions"><button type="button" class="btn primary submit">Submit</button>'
            '<button type="button" class="btn show-sol">Show solution</button></div>'
            '<div class="verdict" role="status" aria-live="polite"></div>'
            f'<div class="solution" hidden><div class="label">Solution</div>{sol}</div>'
            '<div class="prob-nav"><button type="button" class="btn prev-p">Previous problem</button>'
            '<button type="button" class="btn next-p">Next problem</button></div>'
            "</div>"
        )
    html_out = (
        f'<section class="problems" id="practice" data-lecture="{key}">'
        f'<div class="prob-head"><h3>Problems</h3><span class="prob-progress">0 of {n} solved</span></div>'
        '<p class="prob-intro">Pick a problem from the list. Short answers are checked for you. '
        "For code and explanations, you compare with the reference and mark it yourself.</p>"
        f'<ol class="prob-list">{"".join(rows)}</ol>'
        f'<div class="prob-panels">{"".join(panels)}</div>'
        "</section>"
    )
    return head + "\n\n" + html_out + "\n"


def wrap_traps(body):
    return re.sub(
        r"### Traps to watch for\n(.*?)(?=\n### |\n<section class=\"problems\"|\Z)",
        lambda m: '<section class="traps" markdown="1">\n\n### Traps to watch for\n' + m.group(1) + "\n\n</section>\n",
        body,
        flags=re.S,
    )


def finish_html(text, store):
    steps = []

    def step(m):
        n, rest = m.group(1), m.group(2)
        steps.append((n, re.sub(r"<[^>]+>", "", rest)))
        return f'<h3 id="step-{n}"><span class="stepno">Step {n}</span>{rest}</h3>'

    text = re.sub(r"<h3>Step (\d+)\. (.*?)</h3>", step, text)
    text = text.replace("<h3>Traps to watch for</h3>", '<h3 id="traps">Traps to watch for</h3>')
    text = re.sub(r"<p>XXBLOCK(\d+)XX</p>", lambda m: store[int(m.group(1))], text)
    text = re.sub(r"XXBLOCK(\d+)XX", lambda m: store[int(m.group(1))], text)
    return text, steps


def build():
    src = SOURCE.read_text(encoding="utf-8")
    sections = split_sections(src)
    intro, lectures = sections[0], sections[1:]
    meta = []
    for i, sec in enumerate(lectures):
        key = f"L{i + 2}"
        num, _, name = sec["title"].partition(". ")
        first_para = sec["body"].split("\n\n")[0]
        gist = re.split(r"(?<=\.)\s", first_para)[0]
        meta.append({"key": key, "num": num, "name": name, "slug": SLUGS[key], "gist": gist, "sec": sec})

    PAGE_LIST.clear()
    PAGE_LIST.append(("index.html", "Home, all lectures"))
    PAGE_LIST.extend((f'lectures/{m["slug"]}.html', f'{m["num"]}. {m["name"]}') for m in meta)
    out_dir = ROOT / "lectures"
    out_dir.mkdir(exist_ok=True)
    for i, m in enumerate(meta):
        store = []
        body = extract_code(m["sec"]["body"], m["key"], store)
        body = insert_figures(body, m["key"], store)
        body = build_practice(body, m["key"])
        body = wrap_traps(body)
        content = md(body)
        content, steps = finish_html(content, store)
        content = content.replace("<p>", '<p class="lead">', 1)
        toc = "".join(f'<li><a href="#step-{n}">{html.escape(t)}</a></li>' for n, t in steps)
        toc += '<li><a href="#traps">Traps to watch for</a></li><li><a href="#practice">Problems</a></li>'
        head = (
            f'<h1><span class="kicker">{html.escape(m["num"])}</span>{html.escape(m["name"])}</h1>'
            f'<details class="toc"><summary>Steps in this lecture ({len(steps)})</summary><ol>{toc}</ol></details>'
        )
        prev_link = (f'{meta[i - 1]["slug"]}.html', f'{meta[i - 1]["num"]}. {meta[i - 1]["name"]}') if i > 0 else None
        next_link = (f'{meta[i + 1]["slug"]}.html', f'{meta[i + 1]["num"]}. {meta[i + 1]["name"]}') if i + 1 < len(meta) else None
        html_page = page(f'{m["num"]}. {m["name"]} | EE 8350 Guide', head + content, 1, m["slug"], prev_link, next_link)
        (out_dir / f'{m["slug"]}.html').write_text(html_page, encoding="utf-8")

    # Home page
    store = []
    ib = intro["body"]
    ib = ib.replace("### How the lectures connect\n", "### How the lectures connect\n\nXXBLOCK0XX\n\n", 1)
    store.append(course_map())
    ib = ib.replace("### How each section is laid out", "### How each page is laid out")
    ib = ib.replace(
        "It ends with traps people fall into and practice problems that get harder as you go, with answers right after.",
        "It ends with traps people fall into and a set of problems that get harder as you go, checked in the page like LeetCode.",
    )
    ib += (
        "\n\nEvery code example has a pseudocode version in plain words first. "
        "The real SystemVerilog sits underneath behind a Show button, so you only see it when you want it."
    )
    intro_html, _ = finish_html(md(ib), store)
    cards = "".join(
        f'<li><a href="lectures/{m["slug"]}.html"><span class="num">{html.escape(m["num"])}</span>'
        f'<span class="name">{html.escape(m["name"])}</span><span class="gist">{md_inline(m["gist"])}</span></a></li>'
        for m in meta
    )
    home = (
        '<h1><span class="kicker">EE 8350, Fall 2026</span>Advanced Verification, Lectures 1 to 19</h1>'
        '<p class="lead">A calm, one lecture at a time walkthrough of the course slides. '
        "Pick a lecture below, or read the short orientation first.</p>"
        '<h2 id="lectures">Lectures</h2>'
        f'<ol class="lectures">{cards}</ol>'
        '<h2 id="orientation">Orientation</h2>'
        + intro_html
    )
    (ROOT / "index.html").write_text(page("EE 8350 Guide", home, 0, "home"), encoding="utf-8")
    print(f"built index.html and {len(meta)} lecture pages")


if __name__ == "__main__":
    build()
