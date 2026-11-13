# In-browser simulator

`worker.js` runs Icarus Verilog in a Web Worker for the side pane's Code tab.

`ivlpp`, `ivl` and `vvp` (`.js` loaders and `.wasm` binaries) come from the npm package
`@veriflow/iverilog-wasm` 0.1.4, which is Icarus Verilog compiled with Emscripten. They are
under the GPL, version 2 or later: see `COPYING`, and `SOURCE.md` for the exact source
revision and the command that rebuilds them.

One change was made to each loader: the package is built for Node.js, so the line
`var ENVIRONMENT_IS_WORKER=false;var ENVIRONMENT_IS_NODE=true;` was changed to
`var ENVIRONMENT_IS_WORKER=true;var ENVIRONMENT_IS_NODE=false;`, which turns on Emscripten's
own browser code paths. The `.mjs` files were renamed `.js`. The `.wasm` files are unchanged.
