# docs
personal documentation

## EE 8350 lecture guide website

A calm, large text study site for EE 8350 (Advanced Verification Methodologies for VLSI Systems), lectures 1 to 19.

- One lecture per page, with a short list of steps at the top.
- Split view on wide screens. The right pane is a notes box, a second page of the guide, or a Code tab, and the divider can be dragged.
- The Code tab runs Icarus Verilog inside the browser (WebAssembly, in `assets/sim/`). It has an editor with auto indent, `-D` and `+plusarg` flags, terminal style output with clickable error lines, and a waveform view for `$dumpvars`. Each lecture opens on its own example from `playground/browser/`. Code is saved per example in the browser.
- Notes auto indent. Enter keeps the indent, a line ending in a colon indents the next line, Tab and Shift+Tab indent and outdent, and lists keep going. Notes save per lecture in the browser and can be downloaded as a text file.
- Every code example shows plain English pseudocode first. The SystemVerilog is behind a "Show" toggle.
- Diagrams for the main ideas, drawn as SVG so they follow the theme.
- A LeetCode style problem set at the end of each lesson, with Easy, Medium and Hard labels. Short answers are checked in the page. Code problems have an editor with line numbers and auto indent, then you compare with the reference solution and mark it.
- Light, Dark and Auto themes, three text sizes, no animations. Settings, notes and progress stay in your browser only.

Open `index.html` to start. When GitHub Pages is turned on for this repo (Settings, Pages, deploy from the `main` branch, root folder), the site lives at https://raghuavy.github.io/docs/.

### Editing and rebuilding

The words come from `EE 8350_Lecture_Guide.md`. Pseudocode lives in `_src/pseudocode.py`, the diagrams in `_src/visuals.py`, and the problem titles and answer checks in `_src/problems.py`. The Code tab's examples are the `.sv` files in `playground/browser/`; the build bundles them into `assets/sim/starters.js`.

```bash
pip install markdown latex2mathml
python3 _src/build.py
```

That rewrites `index.html` and `lectures/*.html`. The font is Atkinson Hyperlegible, included under the SIL Open Font License in `assets/fonts`.
