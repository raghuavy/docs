# docs
personal documentation

## EE 8350 lecture guide website

A calm, large text study site for EE 8350 (Advanced Verification Methodologies for VLSI Systems), lectures 1 to 19.

- One lecture per page, with a short list of steps at the top.
- Every code example shows plain English pseudocode first. The SystemVerilog is behind a "Show" toggle.
- Diagrams for the main ideas, drawn as SVG so they follow light and dark mode.
- Practice answers stay hidden until you open them.
- Text size buttons in the header (small, normal, large). No animations.

Open `index.html` to start. When GitHub Pages is turned on for this repo (Settings, Pages, deploy from the `main` branch, root folder), the site lives at https://raghuavy.github.io/docs/.

### Editing and rebuilding

The words come from `EE 8350_Lecture_Guide.md`. Pseudocode lives in `_src/pseudocode.py` and the diagrams in `_src/visuals.py`.

```bash
pip install markdown latex2mathml
python3 _src/build.py
```

That rewrites `index.html` and `lectures/*.html`. The font is Atkinson Hyperlegible, included under the SIL Open Font License in `assets/fonts`.
