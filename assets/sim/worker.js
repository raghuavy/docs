// Runs Icarus Verilog (ivlpp, ivl, vvp) compiled to WebAssembly, inside a Web Worker.
// The page sends {type: "run", file, code, defines, plusargs}; this posts back output
// lines as they appear, then {type: "done"} with the exit code and any VCD file.
// The three runtimes are the GPL builds from @veriflow/iverilog-wasm 0.1.4, see SOURCE.md.
import createIvlpp from "./ivlpp.js";
import createIvl from "./ivl.js";
import createVvp from "./vvp.js";

const FACTORIES = { ivlpp: createIvlpp, ivl: createIvl, vvp: createVvp };
const INTERNAL = "/.iverilog";
const PRE = INTERNAL + "/preprocessed.v";
const FLAGS = INTERNAL + "/ivlpp.flags";
const CONF = INTERNAL + "/ivl.conf";
const PROGRAM = INTERNAL + "/program.vvp";
const MAX_LINES = 5000;
const MAX_VCD = 8 * 1024 * 1024;

const compiled = {};
function wasmModule(name) {
  if (!compiled[name]) {
    const url = new URL("./" + name + ".wasm", import.meta.url);
    compiled[name] = WebAssembly.compileStreaming(fetch(url)).catch(() =>
      fetch(url).then((r) => {
        if (!r.ok) throw new Error("could not load " + name + ".wasm (" + r.status + ")");
        return r.arrayBuffer();
      }).then((b) => WebAssembly.compile(b)));
  }
  return compiled[name];
}

// Output goes out in small batches, so a chatty simulation does not flood the page.
let batch = [], lines = 0, dropped = 0, lastFlush = 0;
function flush() {
  if (batch.length) { postMessage({ type: "out", lines: batch }); batch = []; }
  lastFlush = performance.now();
}
function emit(stream, text) {
  if (lines >= MAX_LINES) { dropped++; return; }
  lines++;
  batch.push([stream, text]);
  if (batch.length >= 200 || performance.now() - lastFlush > 40) flush();
}

async function runtime(name) {
  const mod = await wasmModule(name);
  return FACTORIES[name]({
    noInitialRun: true,
    print: (t) => emit("out", t),
    printErr: (t) => emit("err", t),
    instantiateWasm(imports, done) {
      WebAssembly.instantiate(mod, imports).then((inst) => done(inst), (err) => {
        flush();
        postMessage({ type: "error", message: "could not start " + name + ": " + (err && err.message || err) });
      });
      return {};
    },
  });
}

function prepare(rt) {
  rt.FS.mkdirTree("/work");
  rt.FS.mkdirTree(INTERNAL);
  rt.FS.chdir("/work");
}

function callMain(rt, args) {
  try {
    const r = rt.callMain(args);
    return r === undefined ? 0 : r;
  } catch (e) {
    if (e && Number.isInteger(e.status)) return e.status;
    throw e;
  }
}

function config() {
  return [
    "basedir:/work",
    "module:system.vpi",
    "module:v2005_math.vpi",
    "module:v2009.vpi",
    "-t:dll",
    "flag:DLL=vvp.tgt",
    "generation:2012",
    "generation:no-specify",
    "out:" + PROGRAM,
    "iwidth:32",
    "widthcap:65536",
    "functor:cprop",
    "functor:nodangle",
    "",
  ].join("\n");
}

async function run(req) {
  lines = 0; dropped = 0; batch = []; lastFlush = performance.now();
  const t0 = performance.now();
  const file = req.file || "main.sv";

  // 1. Preprocess: `define, `ifdef and the -D flags
  const pp = await runtime("ivlpp");
  prepare(pp);
  pp.FS.writeFile("/work/" + file, req.code);
  const flags = ["D:__ICARUS__=1"];
  for (const [k, v] of Object.entries(req.defines || {})) flags.push(v === true ? "D:" + k : "D:" + k + "=" + v);
  pp.FS.writeFile(FLAGS, flags.join("\n") + "\n");
  let code = callMain(pp, ["-F", FLAGS, "-L", "-o", PRE, file]);
  if (code !== 0) return finish("compile", code, t0, null, null);
  const pre = pp.FS.readFile(PRE);

  // 2. Compile to a vvp program
  const ivl = await runtime("ivl");
  prepare(ivl);
  ivl.FS.writeFile(PRE, pre);
  ivl.FS.writeFile(CONF, config());
  code = callMain(ivl, ["-C" + CONF, "--", PRE]);
  if (code !== 0 || !ivl.FS.analyzePath(PROGRAM).exists) return finish("compile", code || 1, t0, null, null);
  const program = ivl.FS.readFile(PROGRAM);
  const t1 = performance.now();

  // 3. Simulate
  flush();
  postMessage({ type: "stage", stage: "run" });
  const vvp = await runtime("vvp");
  prepare(vvp);
  vvp.FS.writeFile(PROGRAM, program);
  code = callMain(vvp, ["-n", PROGRAM].concat(req.plusargs || []));

  let vcd = null, vcdName = null;
  for (const name of vvp.FS.readdir("/work")) {
    if (!/\.vcd$/i.test(name)) continue;
    const bytes = vvp.FS.readFile("/work/" + name);
    vcdName = name;
    vcd = bytes.length > MAX_VCD ? null : new TextDecoder().decode(bytes);
    if (!vcd) emit("err", "(" + name + " is over 8 MB, too big to draw here)");
    break;
  }
  return finish("run", code, t0, t1, vcd, vcdName);
}

function finish(stage, code, t0, t1, vcd, vcdName) {
  flush();
  const now = performance.now();
  postMessage({
    type: "done", stage, exitCode: code, dropped, vcd, vcdName: vcdName || null,
    compileMs: (t1 || now) - t0, runMs: t1 ? now - t1 : 0,
  });
}

onmessage = (e) => {
  const req = e.data || {};
  if (req.type === "warm") {
    Promise.all(Object.keys(FACTORIES).map(wasmModule)).then(
      () => postMessage({ type: "ready" }),
      (err) => postMessage({ type: "error", message: String(err && err.message || err) }));
    return;
  }
  if (req.type !== "run") return;
  run(req).catch((err) => {
    flush();
    postMessage({ type: "error", message: String(err && err.message || err) });
  });
};
