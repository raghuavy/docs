"""Inline SVG diagrams for the guide.

Every drawing uses CSS classes from assets/style.css, so colors follow the
page theme (light or dark). FIGURES maps (lecture key, "Step N") to the
figures placed after the first paragraph of that step.
"""
import html
import math


def esc(s):
    return html.escape(str(s))


ARROW_DEFS = (
    '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
    + "".join(
        f'<marker id="{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" '
        f'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="{i}"/></marker>'
        for i in ("ah", "aha", "ahw")
    )
    + "</defs></svg>"
)


# ---------------------------------------------------------------- helpers
def svg(w, h, body, label):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">{body}</svg>'


def fig(svg_str, caption):
    return f'<figure class="fig">{svg_str}<figcaption>{esc(caption)}</figcaption></figure>'


def t(x, y, s, size=19, anchor="middle", cls="", bold=False):
    c = f' class="{cls}"' if cls else ""
    b = ' font-weight="700"' if bold else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}"{c}{b}>{esc(s)}</text>'


def rect(x, y, w, h, cls="bx", rx=10):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>'


def box(x, y, w, h, lines, cls="bx", size=19, sub=16):
    """Box with centered lines. First line bold, later lines smaller and muted."""
    out = [rect(x, y, w, h, cls)]
    n = len(lines)
    sizes = [size] + [sub] * (n - 1)
    gaps = [s * 1.3 for s in sizes]
    total = sum(gaps[1:])
    cy = y + h / 2
    yy = cy - total / 2 + sizes[0] * 0.35
    for i, line in enumerate(lines):
        if i > 0:
            yy += gaps[i]
        out.append(t(x + w / 2, round(yy, 1), line, sizes[i], "middle", "" if i == 0 else "tm", i == 0))
    return "".join(out)


def path(d, cls="ln", arrow=True, dash=False):
    marker = {"ln": "ah", "lna": "aha", "lnw": "ahw", "lng": "ah"}.get(cls, "ah")
    m = f' marker-end="url(#{marker})"' if arrow else ""
    c = cls + (" dash" if dash else "")
    return f'<path d="{d}" class="{c}"{m}/>'


def diamond(x, y, r=9, cls="filla"):
    return f'<path d="M{x} {y - r}L{x + r} {y}L{x} {y + r}L{x - r} {y}Z" class="{cls}"/>'


def dot(x, y, r=7, cls="filla"):
    return f'<circle cx="{x}" cy="{y}" r="{r}" class="{cls}"/>'


def vgrid(xs, y1, y2):
    return "".join(f'<path d="M{x} {y1}V{y2}" class="grid dash"/>' for x in xs)


def wave_path(x_levels, y, h, x_end, cls="ln"):
    """x_levels: list of (x, high_bool) change points, in order. Draws a digital waveform."""
    hi, lo = y, y + h
    x0, lev = x_levels[0]
    d = f"M{x0} {hi if lev else lo}"
    for x, l in x_levels[1:]:
        d += f"H{x}V{hi if l else lo}"
    d += f"H{x_end}"
    return path(d, cls, arrow=False)


def clock(x0, y, cw, n, h=26):
    d = f"M{x0} {y + h}"
    for i in range(n):
        x = x0 + i * cw
        d += f"V{y}H{x + cw / 2}V{y + h}H{x + cw}"
    return path(d, "ln", arrow=False)


# ---------------------------------------------------------------- figures
def f_x_hiding():
    b = box(20, 65, 190, 80, ["DUT output", "value is X"])
    b += box(380, 20, 170, 76, ["logic q", "holds X"])
    b += box(380, 114, 170, 76, ["bit q", "becomes 0"], "bxw")
    b += path("M210 105H300", arrow=False)
    b += path("M300 105V58H380") + path("M300 105V152H380")
    b += t(566, 52, "four state", 17, "start", "tm") + t(566, 76, "bug stays visible", 17, "start")
    b += t(566, 146, "two state", 17, "start", "tm") + t(566, 170, "bug is hidden", 17, "start", "tw")
    return fig(svg(760, 210, b, "An X stored in a two state variable becomes 0"),
               "A two state variable has no X, so an unknown value from the DUT silently becomes 0.")


def f_struct_union():
    b = t(20, 28, "Packed struct: one 13 bit vector", 18, "start", "", True)
    groups = [("a", 0, 4, "bxa"), ("b", 4, 8, "bxg"), ("c", 12, 1, "bxw")]
    x0, cw, y = 55, 50, 70
    for name, start, count, cls in groups:
        for k in range(start, start + count):
            b += rect(x0 + k * cw, y, cw, 46, cls, 0)
        b += t(x0 + (start + count / 2) * cw, y - 12, name, 19, "middle", "", True)
    for k, label in [(0, "12"), (3, "9"), (4, "8"), (11, "1"), (12, "0")]:
        b += t(x0 + k * cw + cw / 2, y + 72, label, 15, "middle", "tm")
    b += t(20, 186, "Packed union: the same 4 bits, read two ways", 18, "start", "", True)
    for k, v in enumerate("1101"):
        b += rect(60 + k * 60, 206, 60, 52, "bx", 0) + t(90 + k * 60, 240, v, 22, "middle", "", True)
    b += path("M300 232H330", arrow=False) + path("M330 232V214H362") + path("M330 232V256H362")
    b += t(372, 220, "read as u (unsigned): 8 + 4 + 1 = 13", 17, "start")
    b += t(372, 262, "read as s (signed): -8 + 4 + 1 = -3", 17, "start")
    return fig(svg(760, 285, b, "Bit layout of a packed struct and a packed union"),
               "Top: the first field of a packed struct sits at the top bits, so a is bits 12 to 9. "
               "Bottom: a union stores one set of bits and lets you read it as unsigned or signed.")


def f_packed_unpacked():
    b = t(20, 28, "Unpacked int b[4]: four separate elements", 18, "start", "", True)
    for i in range(4):
        b += box(30 + i * 180, 46, 150, 66, [f"b[{i}]", "32 bits"])
    b += t(20, 160, "Packed bit [3:0][7:0] word: one 32 bit vector", 18, "start", "", True)
    for i in range(4):
        b += box(30 + i * 172, 178, 172, 66, [f"word[{3 - i}]", "8 bits"], "bxa")
    b += t(30, 272, "bit 31", 15, "start", "tm") + t(718, 272, "bit 0", 15, "end", "tm")
    return fig(svg(760, 285, b, "Unpacked array versus packed array"),
               "Unpacked dimensions come after the name and give separate elements. "
               "Packed dimensions come before the name and give one contiguous vector.")


def f_class_objects():
    b = t(120, 30, "class", 16, "middle", "tm") + t(400, 30, "objects", 16, "middle", "tm") + t(635, 30, "handles", 16, "middle", "tm")
    b += box(20, 95, 200, 100, ["class simple", "the blueprint"], "bxq")
    b += box(310, 40, 180, 64, ["object 1"]) + box(310, 160, 180, 64, ["object 2"])
    b += path("M220 145H265V72H310") + path("M265 145V192H310")
    b += t(258, 64, "new()", 16, "end", "tm")
    b += box(590, 50, 90, 44, ["s"], "bxa") + box(590, 170, 90, 44, ["t"], "bxa") + box(590, 250, 90, 44, ["u"], "bxa")
    b += path("M590 72H490") + path("M590 192H490")
    b += t(694, 278, "null", 17, "start", "tm")
    return fig(svg(760, 310, b, "One class, objects built with new, handles pointing at objects"),
               "The class is only a plan. new() builds objects from it. A handle points at one object, "
               "and a handle you never assigned holds null.")


def f_copy_levels():
    b = ""
    titles = ["Copy the handle", "Shallow copy", "Deep copy"]
    for p, x0 in enumerate((10, 270, 530)):
        b += t(x0 + 120, 26, titles[p], 18, "middle", "", True)
        b += box(x0 + 20, 48, 80, 40, ["a1"], "bxa") + box(x0 + 140, 48, 80, 40, ["a2"], "bxa")
        if p == 0:
            b += box(x0 + 50, 140, 140, 56, ["object"])
            b += path(f"M{x0 + 60} 88V140") + path(f"M{x0 + 180} 88V140")
            b += box(x0 + 50, 250, 140, 56, ["inner"])
            b += path(f"M{x0 + 120} 196V250")
        else:
            b += box(x0 + 10, 140, 100, 56, ["object"]) + box(x0 + 130, 140, 100, 56, ["object"])
            b += path(f"M{x0 + 60} 88V140") + path(f"M{x0 + 180} 88V140")
            if p == 1:
                b += box(x0 + 50, 250, 140, 56, ["inner", "shared"], "bxw")
                b += path(f"M{x0 + 70} 196V250") + path(f"M{x0 + 170} 196V250")
            else:
                b += box(x0 + 10, 250, 100, 56, ["inner"]) + box(x0 + 130, 250, 100, 56, ["inner"])
                b += path(f"M{x0 + 60} 196V250") + path(f"M{x0 + 180} 196V250")
    b += '<path d="M260 20V310M520 20V310" class="grid"/>'
    return fig(svg(760, 320, b, "Handle copy, shallow copy and deep copy"),
               "Left: two handles, one object. Middle: new a1 makes a second object, but objects inside are still shared. "
               "Right: a copy method you write rebuilds the inner objects too.")


def f_crt_loop():
    b = box(20, 108, 180, 74, ["generator", "random inputs"])
    b += box(300, 24, 170, 70, ["DUT"]) + box(300, 196, 170, 70, ["reference", "model"])
    b += box(570, 108, 170, 74, ["compare", "pass or fail"], "bxa")
    b += path("M200 145H250V59H300") + path("M250 145V231H300")
    b += path("M470 59H520V130H570") + path("M470 231H520V160H570")
    b += t(478, 48, "actual", 16, "start", "tm") + t(478, 222, "expected", 16, "start", "tm")
    return fig(svg(760, 285, b, "Constrained random test loop"),
               "The same random inputs go to the DUT and to a reference model. A checker compares the two answers.")


def f_dist():
    b = ""
    panels = [("100 := 1,  [200:201] := 4", "each value in the range gets weight 4", [("100", 1, "1/9"), ("200", 4, "4/9"), ("201", 4, "4/9")], 9),
              ("100 := 1,  [200:201] :/ 4", "the range shares weight 4", [("100", 1, "1/5"), ("200", 2, "2/5"), ("201", 2, "2/5")], 5)]
    for p, (title, sub, rows, total) in enumerate(panels):
        y0 = 10 + p * 155
        b += t(20, y0 + 20, title, 18, "start", "", True) + t(20, y0 + 44, sub, 16, "start", "tm")
        for r, (val, w, frac) in enumerate(rows):
            yy = y0 + 58 + r * 30
            width = 600 * w / total
            b += t(70, yy + 18, val, 16, "end", "tm") + rect(80, yy + 2, width, 22, "bxa", 4)
            b += t(90 + width, yy + 19, frac, 16, "start")
    return fig(svg(760, 315, b, "Probabilities from := and :/ in a dist constraint"),
               "Bar length is the chance of each value. With := the range gets 4 per value. With :/ the range splits 4 between its values.")


def f_solve_before():
    b = box(20, 150, 110, 44, ["pick x"])
    b += box(220, 50, 110, 44, ["x = 0"]) + box(220, 214, 110, 44, ["x = 1"])
    b += path("M130 172H175V72H220") + path("M175 172V236H220")
    b += t(183, 110, "1/2", 16, "start", "tm") + t(183, 214, "1/2", 16, "start", "tm")
    b += box(450, 50, 120, 44, ["y = 0"], "bxa") + path("M330 72H450") + t(390, 64, "always", 15, "middle", "tm")
    for k, cy in enumerate((184, 236, 288, 340)):
        b += box(450, cy - 22, 120, 44, [f"y = {k}"], "bxa" if k == 0 else "bx")
        b += path(f"M390 236V{cy}H450") if cy != 236 else path("M390 236H450")
        b += t(590, cy + 6, "1/8", 17, "start")
    b += path("M330 236H390", arrow=False) + t(360, 264, "1/4 each", 14, "middle", "tm")
    b += t(590, 78, "1/2", 17, "start")
    return fig(svg(760, 380, b, "Probability tree for solve x before y"),
               "x is chosen first. y = 0 happens on the whole top branch (1/2) plus one leaf of the bottom branch (1/8), so 5/8 in total.")


def f_bins():
    x0, cw = 56, 42
    hits = {10, 11, 12, 14}
    b = t(48, 68, "value", 15, "end", "tm") + t(48, 136, "bin", 15, "end", "tm")
    for v in range(16):
        b += rect(x0 + v * cw, 40, cw, 44, "bxa" if v in hits else "bx", 0)
        b += t(x0 + v * cw + cw / 2, 68, v, 16)
    for k in range(8):
        hit = (2 * k in hits) or (2 * k + 1 in hits)
        b += rect(x0 + k * 2 * cw + 3, 108, 2 * cw - 6, 42, "bxg" if hit else "bx", 8)
        if hit:
            b += t(x0 + k * 2 * cw + cw, 135, "hit", 16)
        b += t(x0 + k * 2 * cw + cw, 174, f"[{2 * k}:{2 * k + 1}]", 14, "middle", "tm")
    b += t(56, 210, "3 of 8 bins hit, 37.5 percent", 18, "start", "", True)
    return fig(svg(760, 225, b, "Automatic bins with auto_bin_max set to 8"),
               "Shaded values are the four samples. Each bin covers two values and counts as hit if any of its values appeared.")


def f_transition():
    b = ""
    xs = (110, 290, 470, 650)
    for x, v in zip(xs, (7, 8, 9, 7)):
        b += f'<circle cx="{x}" cy="70" r="34" class="bx"/>' + t(x, 78, v, 24, "middle", "", True)
    for i in range(3):
        cls = "lna" if i == 2 else "ln"
        b += path(f"M{xs[i] + 34} 70H{xs[i + 1] - 36}", cls)
    b += t(200, 126, "7 then 8", 16, "middle", "tm") + t(380, 126, "8 then 9", 16, "middle", "tm")
    b += t(560, 126, "9 then 7: hit", 17, "middle", "ta", True)
    b += t(380, 176, "7 is never followed directly by 9, so from_7_to_9 stays empty", 16, "middle", "tm")
    return fig(svg(760, 195, b, "Transition bins on the sequence 7, 8, 9, 7"),
               "A transition bin needs the two values on back to back samples.")


def f_cross_grid():
    x0, y0, c = 70, 40, 21
    pts = {(1, 8), (3, 10), (5, 12), (7, 14)}
    b = ""
    for i in range(16):
        for j in range(16):
            b += f'<rect x="{x0 + i * c}" y="{y0 + (15 - j) * c}" width="{c}" height="{c}" class="{"filla" if (i, j) in pts else "grid"}"/>'
    b += t(x0, y0 + 16 * c + 24, "0", 15, "middle", "tm") + t(x0 + 16 * c, y0 + 16 * c + 24, "15", 15, "middle", "tm")
    b += t(x0 + 8 * c, y0 + 16 * c + 50, "x value", 16, "middle", "tm")
    b += t(x0 - 12, y0 + 16 * c, "0", 15, "end", "tm") + t(x0 - 12, y0 + 12, "15", 15, "end", "tm")
    b += t(x0 - 12, y0 + 8 * c, "y", 16, "end", "tm")
    tx = 450
    b += t(tx, 110, "cpx: 4 of 16 bins", 18, "start") + t(tx, 150, "cpy: 4 of 16 bins", 18, "start")
    b += t(tx, 190, "cpxy: 4 of 256 bins", 18, "start", "", True) + t(tx, 224, "only 1.56 percent", 17, "start", "tw")
    return fig(svg(760, 440, b, "Cross coverage grid of 16 by 16 bins with four hits"),
               "Each square is one (x, y) combination. Four samples fill four squares out of 256.")


def f_layers():
    rows = [("Test layer", "the test, functional coverage"),
            ("Scenario layer", "generator"),
            ("Functional layer", "agent, scoreboard, checker"),
            ("Command layer", "driver, monitor, assertions"),
            ("Signal layer", "the DUT and its wires")]
    b = ""
    for i, (name, items) in enumerate(rows):
        y = 16 + i * 74
        b += rect(20, y, 720, 62, "bxa" if i == 4 else "bx")
        b += t(40, y + 38, name, 19, "start", "", True) + t(300, y + 38, items, 18, "start")
    return fig(svg(760, 395, b, "Layered testbench, from test down to signals"),
               "Each layer talks only to its neighbors. The test sits on top, the DUT at the bottom.")


def f_bundle():
    b = box(20, 40, 110, 190, ["test"]) + box(250, 40, 110, 190, ["arb"])
    for k, name in enumerate(("clk", "rst", "request", "grant")):
        y = 80 + k * 38
        b += path(f"M130 {y}H250", arrow=False) + t(190, y - 7, name, 15, "middle", "tm")
    b += box(400, 40, 110, 190, ["test"]) + box(630, 40, 110, 190, ["arb"])
    b += box(510, 110, 120, 50, ["arb_if"], "bxa")
    b += t(190, 262, "plain ports: 4 separate wires", 16, "middle", "tm")
    b += t(570, 262, "one interface, one connection", 16, "middle", "tm")
    return fig(svg(760, 275, b, "Separate wires compared with one interface"),
               "With an interface, adding a signal means editing one place instead of three.")


def f_clocking():
    x0, cw = 130, 150
    edges = [x0 + i * cw for i in range(5)]
    b = t(116, 52, "clk", 17, "end") + t(116, 122, "grant", 17, "end") + t(116, 192, "request", 17, "end")
    b += vgrid(edges, 28, 214)
    b += clock(x0, 32, cw, 4, 28)
    b += wave_path([(x0, False), (x0 + cw + 70, True)], 104, 28, x0 + 4 * cw)
    b += wave_path([(x0, False), (x0 + 2 * cw + 14, True), (x0 + 3 * cw + 14, False)], 174, 28, x0 + 4 * cw)
    for e in edges[1:4]:
        b += dot(e - 12, 118 if e > x0 + cw + 70 else 132, 6)
    b += diamond(x0 + 2 * cw + 14, 188, 8) + diamond(x0 + 3 * cw + 14, 188, 8)
    b += t(130, 244, "dot: cb samples grant just before the edge", 16, "start", "tm")
    b += t(130, 268, "diamond: cb drives request just after the edge", 16, "start", "tm")
    return fig(svg(760, 280, b, "Clocking block sample and drive timing"),
               "Sampling before the edge and driving after it means the testbench and the DUT never race on the same edge.")


def f_fork():
    x0, s = 200, 20
    b = '<path d="M200 40H710" class="ln"/>'
    for tt in range(0, 26, 5):
        b += f'<path d="M{x0 + tt * s} 34V46" class="ln"/>' + t(x0 + tt * s, 26, tt, 15, "middle", "tm")
    b += t(186, 82, "thread A", 17, "end") + rect(x0, 64, 10 * s, 28, "bxa", 6) + t(x0 + 5 * s, 84, "#10", 15)
    b += t(186, 122, "thread B", 17, "end") + rect(x0, 104, 20 * s, 28, "bxa", 6) + t(x0 + 10 * s, 124, "#20", 15)
    for k, (name, at) in enumerate((("join", 20), ("join_any", 10), ("join_none", 0))):
        y = 180 + k * 44
        b += t(186, y + 6, name, 17, "end", "", True)
        b += f'<path d="M{x0} {y}H{x0 + at * s}" class="grid"/>' + diamond(x0 + at * s, y, 9)
        b += t(x0 + at * s + 18, y + 6, f"continues at {at}", 16, "start", "tm")
    return fig(svg(760, 290, b, "When the parent continues for join, join_any and join_none"),
               "Both threads start at time 0. The join keyword only decides when the code after the fork continues.")


def f_loop_bug():
    b = t(190, 26, "without automatic", 18, "middle", "", True) + t(570, 26, "with automatic k = j", 18, "middle", "", True)
    for k, x in enumerate((20, 140, 260)):
        b += box(x, 50, 100, 44, [f"thread {k + 1}"])
    b += box(140, 150, 100, 56, ["j = 3"], "bxw")
    b += path("M70 94L170 150") + path("M190 94V150") + path("M310 94L210 150")
    b += t(190, 248, "prints 3 3 3", 18, "middle", "tw", True)
    for k, x in enumerate((400, 520, 640)):
        b += box(x, 50, 100, 44, [f"thread {k + 1}"])
        b += box(x, 150, 100, 56, [f"k = {k}"], "bxg")
        b += path(f"M{x + 50} 94V150")
    b += t(570, 248, "prints 0 1 2", 18, "middle", "", True)
    b += '<path d="M380 20V250" class="grid"/>'
    return fig(svg(760, 265, b, "Loop variable shared by threads versus private copies"),
               "join_none threads run after the loop ends. Without a private copy they all read the final j.")


def f_semaphore():
    b = box(40, 40, 180, 60, ["thread 1", "holds the key"], "bxa")
    b += box(40, 130, 180, 60, ["thread 2", "waits in get()"])
    b += box(320, 70, 160, 90, ["room", "1 key"])
    b += path("M220 70H320") + path("M220 160H270V140H320", dash=True)
    b += t(510, 100, "when thread 1 calls put(),", 17, "start") + t(510, 128, "thread 2 gets the key", 17, "start")
    return fig(svg(760, 215, b, "A semaphore with one key guarding a shared resource"),
               "A one key semaphore lets only one thread use the resource at a time.")


def f_mailbox():
    b = box(20, 70, 150, 64, ["producer"]) + box(590, 70, 150, 64, ["consumer"])
    b += t(380, 58, "mailbox, first in first out", 16, "middle", "tm")
    for i in range(4):
        b += rect(260 + i * 60, 72, 60, 60, "bxa" if i >= 2 else "bx", 0)
    b += path("M170 102H260") + path("M500 102H590")
    b += t(215, 92, "put()", 15, "middle", "tm") + t(545, 92, "get()", 15, "middle", "tm")
    b += t(380, 178, "put() waits while a bounded mailbox is full. get() waits while it is empty.", 16, "middle", "tm")
    return fig(svg(760, 200, b, "Producer and consumer connected by a mailbox"),
               "A mailbox is a queue of handles between two threads.")


def f_uvm():
    b = t(24, 30, "Stimulus flows down to the DUT, results flow back to the scoreboard", 17, "start", "", True)
    for (x, y, w, h, label) in ((16, 48, 728, 520, "top module"), (32, 80, 536, 476, "test (uvm_test_top)"),
                                (48, 172, 504, 372, "env"), (64, 206, 240, 244, "agent")):
        b += rect(x, y, w, h, "grid", 10) + t(x + 16, y + 24, label, 16, "start", "tm", True)
    b += box(84, 108, 200, 44, ["sequence (an object)"], "bxq", 17)
    b += box(84, 240, 200, 44, ["sequencer"], "bx", 17)
    b += box(84, 316, 200, 44, ["driver"], "bx", 17)
    b += box(84, 392, 200, 44, ["monitor"], "bx", 17)
    b += box(64, 476, 172, 48, ["predictor"], "bx", 17)
    b += box(300, 476, 172, 48, ["scoreboard"], "bx", 17)
    b += box(600, 304, 128, 140, ["DUT", "reached through", "the interface"], "bxa", 19, 15)
    b += path("M184 152V240") + path("M184 284V316") + path("M284 338H600") + path("M600 414H284")
    b += path("M150 436V476") + path("M250 436V456H386V476") + path("M236 500H300")
    b += t(194, 196, "seq.start(sequencer)", 15, "start", "tm") + t(194, 305, "one item at a time", 15, "start", "tm")
    b += t(442, 330, "pin wiggles", 15, "middle", "tm") + t(442, 406, "pins sampled", 15, "middle", "tm")
    b += t(158, 462, "write()", 15, "start", "tm") + t(394, 470, "actual", 15, "start", "tm") + t(268, 492, "expected", 15, "middle", "tm")
    return fig(svg(760, 580, b, "UVM testbench structure and data flow"),
               "Who builds whom, and the path one transaction takes.")


def f_phases():
    items = [("build", "function", "top down"), ("connect", "function", "wire up ports"),
             ("run", "task", "time passes"), ("report", "function", "print results")]
    b = ""
    for i, lines in enumerate(items):
        x = 20 + i * 185
        b += box(x, 40, 165, 96, list(lines), "bxa" if i == 2 else "bx")
        if i < 3:
            b += path(f"M{x + 165} 88H{x + 185}")
    b += t(380, 176, "Every component runs each phase, and all of them move on together.", 16, "middle", "tm")
    return fig(svg(760, 195, b, "The four main UVM phases in order"), "Only the run phase consumes simulation time, so it is the only task.")


def f_handshake():
    sx, dx = 190, 570
    b = box(sx - 100, 20, 200, 44, ["sequence"]) + box(dx - 100, 20, 200, 44, ["driver"])
    b += f'<path d="M{sx} 64V330M{dx} 64V330" class="grid dash"/>'
    b += path(f"M{dx} 104H{sx + 4}") + t(380, 94, "get_next_item(): ready for one", 15, "middle", "tm")
    b += t(sx - 10, 146, "start_item returns,", 15, "end") + t(sx - 10, 166, "randomize the item", 15, "end")
    b += path(f"M{sx} 196H{dx - 4}") + t(380, 186, "finish_item(): here it is", 15, "middle", "tm")
    b += t(dx + 10, 236, "drive the pins", 15, "start")
    b += path(f"M{dx} 270H{sx + 4}") + t(380, 260, "item_done()", 15, "middle", "tm")
    b += t(sx - 10, 310, "finish_item returns,", 15, "end") + t(sx - 10, 330, "next item", 15, "end")
    return fig(svg(760, 345, b, "Handshake between a sequence and the driver"),
               "start_item waits for the driver to ask. finish_item waits until the driver says item_done.")


def f_virtual():
    b = box(20, 90, 190, 64, ["tr", "Transaction handle"], "bxa")
    b += box(270, 90, 180, 64, ["object", "really a BadTr"])
    b += path("M210 122H270")
    b += box(530, 30, 210, 70, ["virtual method", "BadTr::calc_csm runs"], "bxg")
    b += box(530, 150, 210, 70, ["not virtual", "Transaction::calc_csm"], "bxw")
    b += path("M450 122H490V65H530") + path("M490 122V185H530")
    b += t(380, 228, "tr.calc_csm()", 17, "middle", "", True)
    return fig(svg(760, 245, b, "Which method runs through a base handle"),
               "With virtual, the object's real type picks the method. Without it, the handle's type does.")


def f_blueprint():
    b = box(30, 100, 210, 74, ["blueprint", "randomized each loop"], "bxa")
    for i in range(3):
        b += rect(330 + i * 60, 107, 60, 60, "bxa" if i > 0 else "bx", 0)
    b += t(420, 96, "mailbox", 16, "middle", "tm")
    b += box(560, 100, 180, 74, ["driver"])
    b += path("M240 137H330") + t(285, 127, "copy()", 15, "middle", "tm") + path("M510 137H560")
    b += box(30, 230, 210, 50, ["BadTr object"], "bxq") + path("M135 230V174", dash=True)
    b += t(150, 210, "the test can swap the blueprint", 15, "start", "tm")
    return fig(svg(760, 295, b, "The blueprint pattern"),
               "The generator only knows how to randomize and copy its blueprint, so the test can hand it a different kind of object.")


def f_callbacks():
    steps = [("get item", "bx"), ("pre_tx hooks", "bxa"), ("transmit", "bx"), ("post_tx hooks", "bxa")]
    b = ""
    for i, (name, cls) in enumerate(steps):
        x = 20 + i * 185
        b += box(x, 50, 165, 64, [name], cls)
        if i < 3:
            b += path(f"M{x + 165} 82H{x + 185}")
    b += path("M657 114V150H102V114") + t(380, 142, "forever", 15, "middle", "tm")
    b += box(180, 210, 210, 64, ["Driver_cbs_drop", "added by the test"], "bxq")
    b += path("M287 210V114", dash=True) + t(405, 246, "plugged in with push_back", 16, "start", "tm")
    return fig(svg(760, 290, b, "Driver loop with callback hooks"),
               "The driver calls whatever callback objects are in its list. The test adds behavior without editing the driver.")


def f_req_grant():
    x0, cw = 130, 70
    e = [x0 + i * cw for i in range(9)]
    b = vgrid(e, 30, 296)
    for i in range(9):
        b += t(e[i], 24, i, 14, "middle", "tm")
    b += t(118, 62, "clk", 16, "end") + clock(x0, 44, cw, 8, 24)
    b += t(118, 122, "req", 16, "end")
    b += wave_path([(x0, False), (e[1] - 30, True), (e[1] + 30, False), (e[3] - 30, True), (e[3] + 30, False)], 104, 24, e[8])
    b += t(118, 182, "grant", 16, "end")
    b += wave_path([(x0, False), (e[7] - 30, True), (e[7] + 30, False)], 164, 24, e[8])
    b += t(118, 236, "check 1", 16, "end") + path(f"M{e[1]} 230H{e[5]}", "lnw", arrow=False) + dot(e[5], 230, 8, "fillw")
    b += t(e[5] + 14, 222, "grant low at 5: fails", 15, "start", "tw")
    b += t(118, 286, "check 2", 16, "end") + path(f"M{e[3]} 280H{e[7]}", "lng", arrow=False) + dot(e[7], 280, 8, "fillg")
    b += t(e[7] - 14, 272, "grant high at 7: passes", 15, "end")
    return fig(svg(760, 305, b, "Two overlapping requests, each with its own check"),
               "req at 1 and req at 3 each start their own 4 cycle check. The counter version forgets the first one.")


def f_pipeline():
    b = ""
    for i in range(4):
        x = 20 + i * 150
        b += box(x, 70, 120, 64, [f"stage {i + 1}", "bug here"] if i == 1 else [f"stage {i + 1}"], "bxw" if i == 1 else "bx")
        if i < 3:
            b += path(f"M{x + 120} 102H{x + 150}")
    b += path("M590 102H620") + box(620, 70, 120, 64, ["scoreboard"])
    b += t(230, 48, "an assertion here fires the same cycle", 16, "middle", "ta", True)
    b += t(740, 170, "a scoreboard sees it 2 cycles later", 16, "end", "tm")
    return fig(svg(760, 190, b, "Assertion at the source versus scoreboard at the output"),
               "An assertion points at the stage that broke. A scoreboard only sees the result after it travels.")


def f_adder(bug=False):
    b = ""
    for i in range(4):
        x = 30 + i * 180
        cx = x + 65
        b += box(x, 90, 130, 70, [f"FA{i}"], "bxw" if (bug and i == 2) else "bx")
        b += t(cx, 56, f"a[{i}] b[{i}]", 15, "middle", "tm") + path(f"M{cx} 64V90")
        b += path(f"M{cx} 160V196") + t(cx, 218, f"sum[{i}]", 15, "middle", "tm")
        if i < 3:
            nxt = x + 180
            if bug and i == 1:
                b += path(f"M{x + 130} 125H{nxt}", arrow=False, dash=True) + t(x + 155, 182, "c1 unused", 13, "middle", "tm")
            else:
                b += path(f"M{x + 130} 125H{nxt}") + t(x + 155, 117, f"c{i}", 14, "middle", "tm")
    b += path("M700 125H730V196") + t(730, 218, "sum[4]", 15, "middle", "tm")
    b += t(12, 130, "0", 15, "start", "tm") + path("M22 125H30", arrow=False)
    if bug:
        b += path("M160 104H180V76H375V104H390", "lnw") + t(270, 30, "c0 wired to FA2 by mistake", 14, "middle", "tw", True)
    title = "Ripple carry adder with the planted bug" if bug else "Four bit ripple carry adder"
    cap = ("Stage 2 takes c0 instead of c1. Inputs where those two carries differ give a wrong sum, and the scoreboard flags them."
           if bug else "Each full adder passes its carry to the next one. The last carry becomes sum bit 4.")
    return fig(svg(760, 235, b, title), cap)


def f_one_class():
    b = box(20, 138, 170, 84, ["class Driver", "written once"], "bxq")
    for i, cy in enumerate((58, 138, 218, 298)):
        b += box(270, cy - 28, 180, 56, [f"drv[{i}]"])
        b += box(560, cy - 28, 180, 56, [f"Rx{i} bundle"], "bxa")
        b += path(f"M190 180H230V{cy}H270") if cy != 180 else ""
        b += path(f"M450 {cy}H560") + t(505, cy - 8, f"vRx[{i}]", 14, "middle", "tm")
    return fig(svg(760, 340, b, "One driver class connected to four interfaces through handles"),
               "Each driver object holds a virtual interface handle, so the same code drives whichever port it was given.")


def f_xmr():
    b = t(190, 24, "port list", 18, "middle", "", True) + t(570, 24, "cross module reference", 18, "middle", "", True)
    for x0 in (20, 400):
        b += rect(x0, 40, 340, 200, "grid") + t(x0 + 16, 64, "top", 15, "start", "tm", True)
        b += box(x0 + 130, 80, 120, 50, ["arbif"], "bxa")
        b += box(x0 + 220, 170, 100, 50, ["arb"])
        b += box(x0 + 40, 170, 120, 50, ["test"])
        b += path(f"M{x0 + 210} 130V150H{x0 + 270}V170")
    b += path("M210 130V150H100V170")
    b += path("M480 170V105H530", dash=True) + t(488, 156, "top.arbif", 14, "start", "tm")
    b += t(190, 264, "passed in through ports", 16, "middle", "tm") + t(570, 264, "the test reaches in by path", 16, "middle", "tm")
    return fig(svg(760, 280, b, "Port list compared with a cross module reference"),
               "An XMR lets top gain new interfaces without changing the test's ports, at the cost of depending on top's names.")


def f_feedback():
    b = box(40, 40, 250, 74, ["run the test", "with many seeds"])
    b += box(470, 40, 250, 74, ["any design bugs?", "fix them first"], "bxw")
    b += box(470, 196, 250, 74, ["merge coverage", "from clean runs"])
    b += box(40, 196, 250, 74, ["100 percent?", "if not, adjust"], "bxa")
    b += path("M290 77H470") + path("M595 114V196") + path("M470 233H290") + path("M165 196V114")
    b += t(607, 160, "no bugs", 15, "start", "tm") + t(153, 160, "not yet", 15, "end", "tm")
    return fig(svg(760, 290, b, "The coverage feedback loop"),
               "When coverage is short, try more seeds first, then new constraints, then directed tests for the last corners.")


def f_saturation():
    X0, X1, Y0, Y1 = 90, 720, 250, 40

    def pt(fx, cov):
        return X0 + fx * (X1 - X0), Y0 - cov / 100 * (Y0 - Y1)

    pts = []
    for k in range(101):
        fx = k / 100
        cov = 85 * (1 - math.exp(-fx * 6)) if fx < 0.6 else 85 * (1 - math.exp(-3.6)) + (100 - 85 * (1 - math.exp(-3.6))) * (1 - math.exp(-(fx - 0.6) * 9))
        pts.append(pt(fx, cov))
    d = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    b = f'<path d="M{X0} {Y1}V{Y0}H{X1}" class="ln"/>'
    b += f'<path d="M{X0} {Y1}H{X1}" class="grid dash"/>' + t(X0 - 10, Y1 + 6, "100", 15, "end", "tm") + t(X0 - 10, Y0 + 6, "0", 15, "end", "tm")
    b += path(d, "lna", arrow=False)
    xs = X0 + 0.6 * (X1 - X0)
    b += f'<path d="M{xs:.0f} {Y1 + 10}V{Y0}" class="grid dash"/>'
    b += t(xs - 10, 120, "flattens out", 15, "end", "tm") + t(xs + 10, 214, "new constraints", 15, "start", "ta", True)
    b += t((X0 + X1) / 2, Y0 + 34, "number of runs", 16, "middle", "tm")
    b += t(X0 - 10, 26, "coverage, percent", 15, "start", "tm")
    return fig(svg(760, 300, b, "Coverage rises fast, flattens, then jumps after new constraints"),
               "An illustration of the shape described in the slides, not measured data.")


def f_cross_trim():
    rows = ["zero", "lo", "8", "9", "10", "11", "12", "13", "14", "15"]
    x0, y0, cw, ch = 120, 60, 52, 30
    b = t(x0 + 4 * cw, 24, "port", 16, "middle", "tm") + t(20, 44, "kind bin", 15, "start", "tm")
    for c in range(8):
        b += t(x0 + c * cw + cw / 2, 52, c, 15, "middle", "tm")
    for r, name in enumerate(rows):
        b += t(x0 - 10, y0 + r * ch + 21, name, 15, "end", "tm")
        for c in range(8):
            ignored = c == 7 or name == "lo" or (c == 0 and name in ("9", "10", "11"))
            b += f'<rect x="{x0 + c * cw}" y="{y0 + r * ch}" width="{cw}" height="{ch}" class="{"filldim" if ignored else "fillsoft"}" style="stroke:var(--bg);stroke-width:2"/>'
    lx = 580
    b += rect(lx, 90, 26, 22, "fillsoft", 3) + t(lx + 36, 107, "counted", 16, "start")
    b += rect(lx, 126, 26, 22, "filldim", 3) + t(lx + 36, 143, "ignored", 16, "start")
    b += t(lx, 196, "60 of 80", 19, "start", "", True) + t(lx, 222, "cross bins left", 16, "start", "tm")
    return fig(svg(760, 370, b, "Cross of kind bins and port values with ignored cells"),
               "The misc default bin is never part of a cross, so 10 kind bins times 8 ports gives 80. Three ignore rules remove 20 of them.")


def f_regions():
    names = [("Preponed", "sample"), ("Active", "design"), ("Inactive", "#0"), ("NBA", "q <= d"),
             ("Observed", "assertions"), ("Reactive", "programs"), ("Postponed", "$strobe")]
    b = ""
    for i, (n, s) in enumerate(names):
        b += box(10 + i * 106, 40, 98, 74, [n, s], "bxa" if i in (0, 4) else "bx", 15, 14)
    b += path("M10 146H744") + t(377, 174, "one simulation time step, left to right", 16, "middle", "tm")
    return fig(svg(760, 190, b, "Scheduling regions inside one time step"),
               "Assertions read values in Preponed and evaluate in Observed, so they never see a value halfway through a time step.")


def f_glitch():
    x0, xe, tc = 150, 700, 400
    b = t(136, 58, "b", 17, "end") + wave_path([(x0, True), (tc, False)], 40, 28, xe)
    b += t(136, 128, "c", 17, "end") + wave_path([(x0, False), (tc, True)], 110, 28, xe)
    b += t(136, 198, "a = b | c", 17, "end") + wave_path([(x0, True)], 180, 28, xe)
    b += f'<path d="M{tc} 180V208H{tc + 26}V180" class="lnw dash"/>'
    b += f'<path d="M{tc} 26V222" class="grid dash"/>'
    b += t(tc + 40, 202, "zero width dip if b updates before c", 15, "start", "tw")
    return fig(svg(760, 240, b, "A zero width glitch on a = b | c"),
               "b falls and c rises at the same time. a should stay 1, but the order of updates can make it read 0 for an instant.")


def f_implication():
    x0, cw = 200, 120
    e = [x0 + i * cw for i in range(5)]
    b = vgrid(e, 30, 222)
    for i in range(5):
        b += t(e[i], 22, f"edge {i + 1}", 14, "middle", "tm")
    b += t(186, 74, "A matches", 17, "end") + diamond(e[1], 68, 10)
    b += t(186, 140, "A |-> B", 17, "end", "", True) + diamond(e[1], 134, 10, "fillg") + t(e[1] + 20, 140, "B checked on the same edge", 15, "start", "tm")
    b += t(186, 206, "A |=> B", 17, "end", "", True) + diamond(e[2], 200, 10, "fillg") + t(e[2] + 20, 206, "B checked on the next edge", 15, "start", "tm")
    return fig(svg(760, 230, b, "Overlapped and non overlapped implication"),
               "If A never matches, nothing is checked and the property passes vacuously.")


def f_delays():
    x0, cw = 170, 85
    e = [x0 + i * cw for i in range(7)]
    b = vgrid(e, 30, 214)
    for i in range(7):
        b += t(e[i], 22, i, 14, "middle", "tm")
    b += t(156, 86, "a ##2 b", 17, "end", "", True) + diamond(e[1], 80, 10) + diamond(e[3], 80, 10, "fillg")
    b += t(e[1], 112, "a", 15, "middle", "tm") + t(e[3], 112, "b", 15, "middle", "tm")
    b += t(156, 176, "a ##[1:3] b", 17, "end", "", True)
    b += rect(e[2] - 18, 154, e[4] - e[2] + 36, 40, "fillsoft", 8) + diamond(e[1], 174, 10)
    b += t(e[1], 206, "a", 15, "middle", "tm") + t((e[2] + e[4]) / 2, 210, "b may come on any of these", 14, "middle", "tm")
    return fig(svg(760, 225, b, "Fixed delay versus a delay range"),
               "##2 means exactly two edges later. ##[1:3] allows one, two or three edges later.")


def f_repetition():
    x0, cw = 190, 48
    e = [x0 + (i - 1) * cw for i in range(1, 13)]
    b = vgrid(e, 30, 312)
    for i in range(12):
        b += t(e[i], 22, i + 1, 14, "middle", "tm")
    b += t(176, 68, "b", 16, "end", "", True)
    lv = [(x0 - 20, False)]
    for k in (2, 5, 9):
        lv += [(e[k - 1] - 14, True), (e[k - 1] + 14, False)]
    b += wave_path(lv, 50, 24, e[11] + 10)
    b += t(176, 134, "b[->3] ##1 done", 15, "end", "", True)
    b += diamond(e[9], 128, 10, "fillg") + t(e[9] + 16, 134, "done exactly here", 14, "start", "tm")
    b += t(176, 200, "b[=3] ##1 done", 15, "end", "", True)
    b += rect(e[9] - 16, 178, e[11] - e[9] + 32, 42, "fillsoft", 8) + t(e[9] - 26, 205, "done anywhere here", 14, "end", "tm")
    b += t(176, 272, "c[*3]", 15, "end", "", True)
    b += rect(e[2] - 14, 256, e[4] - e[2] + 28, 26, "bxa", 6) + t(e[4] + 24, 275, "c high three clocks in a row", 14, "start", "tm")
    return fig(svg(760, 320, b, "Goto, nonconsecutive and consecutive repetition"),
               "b is high at clocks 2, 5 and 9. The goto form needs done right after the third b. "
               "The [=3] form allows done later, as long as no fourth b comes first.")


def f_throughout():
    x0, cw = 210, 70
    e = [x0 + i * cw for i in range(8)]
    b = vgrid(e, 30, 238)
    for i in range(8):
        b += t(e[i], 22, i + 1, 14, "middle", "tm")
    b += t(196, 66, "start, done", 16, "end") + diamond(e[0], 60, 9) + diamond(e[3], 60, 9, "fillg")
    b += t(196, 112, "en", 16, "end", "", True) + rect(e[0] - 10, 96, e[3] - e[0] + 20, 26, "bxg", 6)
    b += t(e[3] + 20, 114, "en throughout the whole span", 14, "start", "tm")
    b += t(196, 178, "s2", 16, "end", "", True) + rect(e[0] - 10, 162, e[7] - e[0] + 20, 26, "bx", 6)
    b += t(196, 222, "s1", 16, "end", "", True) + rect(e[2] - 10, 206, e[4] - e[2] + 20, 26, "bxa", 6)
    b += t(e[4] + 20, 224, "s1 within s2", 14, "start", "tm")
    return fig(svg(760, 250, b, "throughout and within"),
               "throughout keeps a condition true for every clock of a sequence. within places one sequence inside the time span of another.")


def f_mtbf():
    X0, X1, YB, YT = 90, 720, 290, 40

    def ymap(v):
        return YB - (v + 10) / 50 * (YB - YT)

    def xmap(s):
        return X0 + s / 1000 * (X1 - X0)

    def logm(s):
        return s / 10 * math.log10(math.e) - math.log10(2e6)

    b = f'<path d="M{X0} {YT}V{YB}H{X1}" class="ln"/>'
    for v in (-10, 0, 10, 20, 30, 40):
        b += f'<path d="M{X0 - 5} {ymap(v):.1f}H{X0}" class="ln"/>' + t(X0 - 10, ymap(v) + 5, v, 14, "end", "tm")
    for s in (0, 250, 500, 750, 1000):
        b += t(xmap(s), YB + 22, s, 14, "middle", "tm")
    b += t((X0 + X1) / 2, YB + 46, "S, settle time in picoseconds", 15, "middle", "tm")
    b += t(X0 - 6, 24, "log10 of MTBF in seconds", 15, "start", "tm")
    for v, label in ((math.log10(3.156e7), "1 year"), (math.log10(1e10 * 3.156e7), "age of the universe")):
        b += f'<path d="M{X0} {ymap(v):.1f}H{X1}" class="grid dash"/>' + t(X1, ymap(v) - 6, label, 14, "end", "tm")
    b += path(f"M{xmap(0):.1f} {ymap(logm(0)):.1f}L{xmap(1000):.1f} {ymap(logm(1000)):.1f}", "lna", arrow=False)
    b += dot(xmap(0.1), ymap(logm(0.1)), 7) + t(xmap(0.1) + 22, 284, "S = 0.1 ps: 505 ns", 14, "start")
    b += dot(xmap(1000), ymap(logm(1000)), 7) + t(xmap(1000) - 14, ymap(logm(1000)) + 6, "S = 1 ns: about 4 x 10^29 years", 14, "end")
    return fig(svg(760, 350, b, "MTBF grows exponentially with settle time"),
               "Computed from the slide's numbers: tau 10 ps, TW 20 ps, fC 1 GHz, fD 100 MHz. On a log scale MTBF is a straight line in S.")


def f_sync2():
    b = t(110, 24, "source clock domain", 16, "middle", "tm") + t(500, 24, "destination clock domain", 16, "middle", "tm")
    b += '<path d="M220 36V230" class="grid dash"/>'
    b += box(30, 80, 120, 80, ["source", "flop"])
    b += box(290, 80, 130, 80, ["meta"], "bxw") + box(500, 80, 130, 80, ["q_sync"], "bxa")
    b += path("M150 120H290") + path("M420 120H500") + path("M630 120H730")
    b += t(232, 110, "d_async", 14, "start", "tm") + t(680, 110, "safe", 14, "middle", "tm")
    b += t(355, 190, "may go metastable", 15, "middle", "tw") + t(565, 190, "a full clock to settle", 15, "middle", "tm")
    return fig(svg(760, 215, b, "Two flop synchronizer across a clock domain boundary"),
               "The first flop may land between 0 and 1. The second samples it a clock later, after it has almost surely settled.")


def f_incoherence():
    x0, cw = 200, 120
    e = [x0 + i * cw for i in range(5)]
    b = vgrid(e, 30, 250)
    for i in range(5):
        b += t(e[i], 22, f"dst edge {i}", 13, "middle", "tm")
    b += f'<rect x="{e[1]}" y="150" width="{cw}" height="100" class="fillw" opacity="0.18"/>'
    rows = [("X[1]", 250), ("X[0]", 250), ("Y[1]", e[2]), ("Y[0]", e[1])]
    for k, (name, rise) in enumerate(rows):
        y = 44 + k * 52 + (20 if k >= 2 else 0)
        b += t(186, y + 20, name, 16, "end", "", True) + wave_path([(x0 - 40, False), (rise, True)], y, 24, e[4] + 20)
    b += t(e[1] + cw / 2, 276, "Y reads 01 here, a value X never had", 15, "middle", "tw", True)
    return fig(svg(760, 290, b, "Bus bits resolving on different cycles"),
               "X goes from 00 to 11 at once, but each bit crosses through its own synchronizer and may arrive a cycle apart.")


def f_async_fifo():
    b = t(200, 24, "write clock domain", 16, "middle", "tm") + t(560, 24, "read clock domain", 16, "middle", "tm")
    b += '<path d="M380 34V340" class="grid dash"/>'
    b += box(40, 60, 200, 80, ["fifo_wr", "write pointer, full"])
    b += box(280, 60, 200, 80, ["fifo_mem", "8 bit RAM"], "bxa")
    b += box(520, 60, 200, 80, ["fifo_rd", "read pointer, empty"])
    b += box(180, 230, 150, 70, ["sync", "to write side"], "bxw")
    b += box(430, 230, 150, 70, ["sync", "to read side"], "bxw")
    b += path("M240 100H280") + path("M480 100H520")
    b += path("M200 140V190H505V230") + t(350, 182, "gray_w_ptr", 14, "middle", "tm")
    b += path("M580 265H620V140") + t(630, 210, "w2r_ptr", 14, "start", "tm")
    b += path("M680 140V325H255V300") + t(470, 318, "gray_rd_ptr", 14, "middle", "tm")
    b += path("M180 265H120V140") + t(110, 210, "r2w_ptr", 14, "end", "tm")
    return fig(svg(760, 345, b, "Asynchronous FIFO with Gray pointers crossing through synchronizers"),
               "Only the Gray coded pointers cross between clocks, each through its own synchronizer. One bit changes per step, "
               "so a pointer caught mid change reads as the old or the new value.")


def course_map():
    stages = [("Language foundations", "Lectures 1, 2 and 5"),
              ("Inputs and measurement", "Lectures 3, 4, 13 and 14"),
              ("Testbench machinery", "Lectures 6 and 7, 9 to 11, 12 (interfaces)"),
              ("Methodology", "Lecture 8, Lecture 12 (UVM adder)"),
              ("Checking over time", "Lectures 10, 14 to 16, 16 to 18"),
              ("Special topic", "Lecture 19, clock domain crossing")]
    b = ""
    for i, (name, lec) in enumerate(stages):
        y = 16 + i * 70
        b += box(20, y, 260, 52, [name], "bxa" if i == 3 else "bx", 18)
        b += t(304, y + 33, lec, 17, "start", "tm")
        if i < 5:
            b += path(f"M150 {y + 52}V{y + 70}")
    return fig(svg(760, 440, b, "How the lectures connect"),
               "Read top to bottom. Each stage builds on the one above it.")


FIGURES = {
    ("L2", "Step 2"): [f_x_hiding()],
    ("L2", "Step 6"): [f_struct_union()],
    ("L2", "Step 11"): [f_packed_unpacked()],
    ("L3", "Step 1"): [f_class_objects()],
    ("L3", "Step 9"): [f_copy_levels()],
    ("L4", "Step 1"): [f_crt_loop()],
    ("L4", "Step 9"): [f_dist()],
    ("L4", "Step 12"): [f_solve_before()],
    ("L5", "Step 4"): [f_bins()],
    ("L5", "Step 6"): [f_transition()],
    ("L5", "Step 8"): [f_cross_grid()],
    ("L6", "Step 1"): [f_layers()],
    ("L6", "Step 3"): [f_bundle()],
    ("L6", "Step 5"): [f_clocking()],
    ("L7", "Step 1"): [f_fork()],
    ("L7", "Step 3"): [f_loop_bug()],
    ("L7", "Step 7"): [f_semaphore()],
    ("L7", "Step 8"): [f_mailbox()],
    ("L8", "embed"): [f_uvm()],
    ("L8", "Step 4"): [f_phases()],
    ("L8", "Step 6"): [f_handshake()],
    ("L9", "Step 3"): [f_virtual()],
    ("L9", "Step 4"): [f_blueprint()],
    ("L9", "Step 9"): [f_callbacks()],
    ("L10", "Step 3"): [f_req_grant()],
    ("L10", "Step 7"): [f_pipeline()],
    ("L11", "Step 2"): [f_adder(False)],
    ("L11", "Step 11"): [f_adder(True)],
    ("L12", "Step 2"): [f_one_class()],
    ("L12", "Step 6"): [f_xmr()],
    ("L13", "Step 3"): [f_feedback(), f_saturation()],
    ("L13", "Step 12"): [f_cross_trim()],
    ("L14", "Step 5"): [f_regions()],
    ("L14", "Step 6"): [f_glitch()],
    ("L14", "Step 10"): [f_implication()],
    ("L15", "Step 6"): [f_delays()],
    ("L15", "Step 11"): [f_repetition()],
    ("L15", "Step 12"): [f_throughout()],
    ("L16", "Step 2"): [f_mtbf()],
    ("L16", "Step 3"): [f_sync2()],
    ("L16", "Step 4"): [f_incoherence()],
    ("L16", "Step 9"): [f_async_fifo()],
}
