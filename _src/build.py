"""Build the EE 8350 guide website from the lecture guide markdown.

Usage:  python3 _src/build.py
Needs:  pip install markdown latex2mathml

Reads   EE 8350_Lecture_Guide.md
Writes  index.html and lectures/*.html
Content added on top of the markdown lives in _src/pseudocode.py and _src/visuals.py.
"""
import html
import re
import sys
from pathlib import Path

import markdown
from latex2mathml.converter import convert as tex_to_mathml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pseudocode import PSEUDO  # noqa: E402
from visuals import FIGURES, ARROW_DEFS, course_map  # noqa: E402

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


def page(title, body, depth, prev_link=None, next_link=None):
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
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<script>try{{var s=localStorage.getItem("ee8350-size");if(s)document.documentElement.setAttribute("data-size",s);}}catch(e){{}}</script>
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to the content</a>
<header class="site">
  <a class="home" href="{up}index.html">EE 8350 Guide</a>
  <div class="sizer" role="group" aria-label="Text size">
    <span>Text</span>
    <button type="button" data-size="1" aria-label="Smaller text">A</button>
    <button type="button" data-size="2" aria-label="Normal text">A</button>
    <button type="button" data-size="3" aria-label="Larger text">A</button>
  </div>
</header>
{ARROW_DEFS}
<main id="main">
{body}
</main>
{pager}
<footer class="site">Study guide for EE 8350, Advanced Verification Methodologies for VLSI Systems. Built from the lecture slides, chapters 1 to 19.</footer>
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


def build_practice(body):
    """Turn the Practice and Answers lists into questions with hidden answers."""
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
    parts = ['<h3 id="practice">Practice</h3>',
             '<p>Try each one first, then open the answer.</p>',
             '<ol class="practice">']
    for i, q in enumerate(qs):
        a = ans[i] if i < len(ans) else ["(no answer written)"]
        a_html = md("\n\n".join(a))
        parts.append(
            f"<li><div>{md_inline(' '.join(q))}</div>"
            f'<details class="answer"><summary>Show answer</summary><div>{a_html}</div></details></li>'
        )
    parts.append("</ol>")
    return head + "\n\n" + "\n".join(parts) + "\n"


def wrap_traps(body):
    return re.sub(
        r"### Traps to watch for\n(.*?)(?=\n### |\n<h3 id=\"practice\">|\Z)",
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

    out_dir = ROOT / "lectures"
    out_dir.mkdir(exist_ok=True)
    for i, m in enumerate(meta):
        store = []
        body = extract_code(m["sec"]["body"], m["key"], store)
        body = insert_figures(body, m["key"], store)
        body = build_practice(body)
        body = wrap_traps(body)
        content = md(body)
        content, steps = finish_html(content, store)
        content = content.replace("<p>", '<p class="lead">', 1)
        toc = "".join(f'<li><a href="#step-{n}">{html.escape(t)}</a></li>' for n, t in steps)
        toc += '<li><a href="#traps">Traps to watch for</a></li><li><a href="#practice">Practice</a></li>'
        head = (
            f'<h1><span class="kicker">{html.escape(m["num"])}</span>{html.escape(m["name"])}</h1>'
            f'<details class="toc"><summary>Steps in this lecture ({len(steps)})</summary><ol>{toc}</ol></details>'
        )
        prev_link = (f'{meta[i - 1]["slug"]}.html', f'{meta[i - 1]["num"]}. {meta[i - 1]["name"]}') if i > 0 else None
        next_link = (f'{meta[i + 1]["slug"]}.html', f'{meta[i + 1]["num"]}. {meta[i + 1]["name"]}') if i + 1 < len(meta) else None
        html_page = page(f'{m["num"]}. {m["name"]} | EE 8350 Guide', head + content, 1, prev_link, next_link)
        (out_dir / f'{m["slug"]}.html').write_text(html_page, encoding="utf-8")

    # Home page
    store = []
    ib = intro["body"]
    ib = ib.replace("### How the lectures connect\n", "### How the lectures connect\n\nXXBLOCK0XX\n\n", 1)
    store.append(course_map())
    ib = ib.replace("### How each section is laid out", "### How each page is laid out")
    ib = ib.replace(
        "It ends with traps people fall into and practice problems that get harder as you go, with answers right after.",
        "It ends with traps people fall into and practice problems that get harder as you go. Answers stay hidden until you open them.",
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
    (ROOT / "index.html").write_text(page("EE 8350 Guide", home, 0), encoding="utf-8")
    print(f"built index.html and {len(meta)} lecture pages")


if __name__ == "__main__":
    build()
