// EE 8350 guide. The side pane's Code tab: an editor, a Run button, terminal style output
// and a waveform view. The simulation itself runs in worker.js, inside this browser.
(function () {
  "use strict";
  var EE = window.EE, store = EE.store;
  var sec = document.querySelector(".side-code");
  if (!sec || window.EECode) return;

  var ta = sec.querySelector(".code-src");
  var runBtn = sec.querySelector(".code-run"), stopBtn = sec.querySelector(".code-stop");
  var flagIn = sec.querySelector(".code-flag-in"), pickIn = sec.querySelector(".code-pick-in");
  var resetBtn = sec.querySelector(".code-reset"), dlBtn = sec.querySelector(".code-dl"), edaBtn = sec.querySelector(".code-eda");
  var con = sec.querySelector(".console"), wavesBox = sec.querySelector(".waves");
  var statusEl = sec.querySelector(".code-status");
  var outTabs = sec.querySelectorAll("[data-out]");
  var page = sec.getAttribute("data-page"), defaultId = sec.getAttribute("data-starter");

  var COMPILE_LIMIT = 60000, RUN_LIMIT = 20000;
  var starters = null, byId = {}, cur = null, opened = false, pending = null;
  var worker = null, warm = false, running = false, limitTimer = null, tick = null, t0 = 0, runStart = 0;
  var lastVcd = null, lastVcdName = null, drawnVcd = null, everWarm = false, keepStatus = false;

  function setStatus(t) { statusEl.textContent = t; }

  // ---------- Examples ----------
  function loadStarters(cb) {
    if (window.EE_STARTERS) { cb(); return; }
    var s = document.createElement("script");
    s.src = sec.getAttribute("data-starters");
    s.onload = cb;
    s.onerror = function () { opened = false; setStatus("Could not load the examples. Check the connection and open the tab again."); };
    document.head.appendChild(s);
  }

  function open() {
    if (opened) return;
    opened = true;
    setStatus("Loading the examples");
    loadStarters(function () {
      starters = window.EE_STARTERS || [];
      starters.forEach(function (st) {
        byId[st.id] = st;
        var o = document.createElement("option");
        o.value = st.id; o.textContent = st.label;
        pickIn.appendChild(o);
      });
      var id = pending || store.get("ee8350-codepick-" + page) || defaultId;
      var focus = !!pending;
      pending = null;
      load(id, focus);
      startWorker();
    });
  }

  function saveNow() {
    if (!cur) return;
    store.set("ee8350-code-" + cur.id, ta.value === cur.code ? "" : ta.value);
    store.set("ee8350-codeflags-" + cur.id, flagIn.value);
  }

  function load(id, focus) {
    if (!starters) { pending = id; open(); return; }
    if (!byId[id]) id = byId[defaultId] ? defaultId : starters[0].id;
    if (cur && cur.id === id && !focus) return;
    saveNow();
    cur = byId[id];
    pickIn.value = id;
    store.set("ee8350-codepick-" + page, id);
    ta.value = store.get("ee8350-code-" + id) || cur.code;
    flagIn.value = store.get("ee8350-codeflags-" + id) || "";
    if (ta._renumber) ta._renumber();
    ta.scrollTop = 0; ta.scrollLeft = 0;
    ta.setSelectionRange(0, 0);
    if (focus) ta.focus();
    if (!running) setStatus((warm ? "Ready. " : "") + "Press Run, or Ctrl+Enter.");
  }

  var saveTimer = null;
  function saveSoon() { clearTimeout(saveTimer); saveTimer = setTimeout(saveNow, 400); }
  ta.addEventListener("input", saveSoon);
  flagIn.addEventListener("input", saveSoon);
  pickIn.addEventListener("change", function () { load(pickIn.value, false); });

  // ---------- Buttons ----------
  var armed = null;
  resetBtn.addEventListener("click", function () {
    if (!cur) return;
    if (!armed) {
      resetBtn.textContent = "Click again to reset";
      armed = setTimeout(function () { resetBtn.textContent = "Reset"; armed = null; }, 4000);
      return;
    }
    clearTimeout(armed); armed = null; resetBtn.textContent = "Reset";
    ta.value = cur.code; flagIn.value = "";
    saveNow();
    if (ta._renumber) ta._renumber();
    setStatus("Back to the original example.");
    ta.focus();
  });

  dlBtn.addEventListener("click", function () {
    if (!cur) return;
    var a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([ta.value], { type: "text/plain" }));
    a.download = cur.file;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
  });

  edaBtn.addEventListener("click", function () {
    window.open("https://www.edaplayground.com/", "_blank", "noopener");
    var msg = "In EDA Playground, paste over the testbench box, pick a simulator such as Synopsys VCS, and press Run.";
    var done = function () { setStatus("Copied. " + msg); };
    var fail = function () { ta.focus(); ta.select(); setStatus("Press Ctrl+C to copy, then: " + msg); };
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(ta.value).then(done, fail);
    else fail();
  });

  ta.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); run(); }
  });
  flagIn.addEventListener("keydown", function (e) {
    if (e.key === "Enter") { e.preventDefault(); run(); }
  });
  runBtn.addEventListener("click", run);
  stopBtn.addEventListener("click", function () { stop("Stopped."); });

  outTabs.forEach(function (b) { b.addEventListener("click", function () { showOut(b.getAttribute("data-out")); }); });
  function showOut(which) {
    outTabs.forEach(function (b) { b.setAttribute("aria-selected", String(b.getAttribute("data-out") === which)); });
    con.hidden = which !== "console";
    wavesBox.hidden = which !== "waves";
    sec.classList.toggle("show-waves", which === "waves");
    if (which === "waves") drawWaves();
  }

  // ---------- Flags ----------
  function parseFlags(text) {
    var toks = text.trim() ? text.trim().split(/\s+/) : [];
    var defines = {}, plusargs = [], bad = [];
    function def(x) {
      var m = /^([A-Za-z_]\w*)(?:=(.*))?$/.exec(x || "");
      if (m) defines[m[1]] = m[2] === undefined ? true : m[2]; else bad.push("-D " + (x || ""));
    }
    for (var i = 0; i < toks.length; i++) {
      var t = toks[i];
      if (t === "-D") def(toks[++i]);
      else if (/^-D./.test(t)) def(t.slice(2));
      else if (t.charAt(0) === "+") plusargs.push(t);
      else bad.push(t);
    }
    return { defines: defines, plusargs: plusargs, bad: bad };
  }

  // ---------- Output ----------
  var REF = /([\w.\/-]+\.s?vh?):(\d+):/;
  function lineEl(stream, text) {
    var el = document.createElement("span");
    el.className = "ln";
    if (stream === "cmd") el.className += " cmd";
    else if (/\b(error|errors|sorry|fail(ed)?|mismatch)\b/i.test(text)) el.className += " bad";
    else if (/\bwarning\b/i.test(text)) el.className += " warn";
    else if (stream === "note") el.className += " note";
    var m = stream === "cmd" ? null : REF.exec(text);
    if (m) {
      el.appendChild(document.createTextNode(text.slice(0, m.index)));
      var b = document.createElement("button");
      b.type = "button"; b.className = "ref"; b.textContent = m[0];
      b.setAttribute("aria-label", "Go to line " + m[2]);
      b.addEventListener("click", function () { gotoLine(parseInt(m[2], 10)); });
      el.appendChild(b);
      el.appendChild(document.createTextNode(text.slice(m.index + m[0].length) + "\n"));
    } else {
      el.textContent = text + "\n";
    }
    return el;
  }
  function addLines(list) {
    var nearBottom = con.scrollHeight - con.scrollTop - con.clientHeight < 40;
    var frag = document.createDocumentFragment();
    list.forEach(function (l) { frag.appendChild(lineEl(l[0], l[1])); });
    con.appendChild(frag);
    if (nearBottom) con.scrollTop = con.scrollHeight;
  }
  function say(stream, text) { addLines([[stream, text]]); }

  function gotoLine(n) {
    var v = ta.value, pos = 0;
    for (var i = 1; i < n && pos >= 0; i++) { pos = v.indexOf("\n", pos); if (pos >= 0) pos++; }
    if (pos < 0) pos = v.length;
    var end = v.indexOf("\n", pos); if (end < 0) end = v.length;
    ta.focus();
    ta.setSelectionRange(pos, end);
    var lh = parseFloat(getComputedStyle(ta).lineHeight) || 20;
    ta.scrollTop = Math.max(0, (n - 1) * lh - ta.clientHeight / 3);
  }

  // ---------- Running ----------
  function startWorker() {
    if (worker) return worker;
    try {
      worker = new Worker(sec.getAttribute("data-worker"), { type: "module" });
    } catch (e) {
      worker = null;
      setStatus("This browser cannot run the simulator. Try a current Chrome, Edge, Firefox or Safari.");
      return null;
    }
    warm = false;
    worker.onmessage = onMessage;
    worker.onerror = function (e) {
      if (e && e.preventDefault) e.preventDefault();
      say("err", "The simulator failed to start" + (e && e.message ? ": " + e.message : "."));
      done(false);
      killWorker();
    };
    if (!running && !keepStatus) setStatus(everWarm ? "Getting the simulator ready" : "Loading the simulator, about 3 MB the first time");
    worker.postMessage({ type: "warm" });
    return worker;
  }
  function killWorker() {
    if (worker) { worker.terminate(); worker = null; }
    warm = false;
  }

  function run() {
    if (running || !cur) return;
    keepStatus = false;
    saveNow();
    var f = parseFlags(flagIn.value);
    con.textContent = "";
    lastVcd = null; lastVcdName = null; drawnVcd = null;
    wavesBox.textContent = "";
    outTabs[1].disabled = true;
    showOut("console");
    var defs = Object.keys(f.defines).map(function (k) { return " -D" + k + (f.defines[k] === true ? "" : "=" + f.defines[k]); }).join("");
    say("cmd", "$ iverilog -g2012" + defs + " -o a.out " + cur.file);
    if (f.bad.length) say("note", "(ignored, not understood here: " + f.bad.join(" ") + ")");
    var w = startWorker();
    if (!w) return;
    running = true;
    runBtn.disabled = true; stopBtn.hidden = false;
    t0 = performance.now(); runStart = 0;
    setStatus(warm ? "Compiling" : "Loading the simulator, then compiling");
    clearTimeout(limitTimer);
    limitTimer = setTimeout(function () { stop("Stopped: compiling took over a minute."); }, COMPILE_LIMIT);
    clearInterval(tick);
    tick = setInterval(function () {
      if (runStart) setStatus("Running, " + Math.round((performance.now() - runStart) / 1000) + " s");
    }, 1000);
    w.postMessage({ type: "run", file: cur.file, code: ta.value, defines: f.defines, plusargs: f.plusargs });
    run.plus = f.plusargs;
  }

  function onMessage(e) {
    var m = e.data || {};
    if (m.type === "ready") {
      warm = true; everWarm = true;
      if (!running && !keepStatus) setStatus("Ready. Press Run, or Ctrl+Enter.");
      else if (!runStart) setStatus("Compiling");
    } else if (m.type === "out") {
      addLines(m.lines);
    } else if (m.type === "stage" && m.stage === "run") {
      say("cmd", "$ vvp -n a.out" + (run.plus && run.plus.length ? " " + run.plus.join(" ") : ""));
      runStart = performance.now();
      setStatus("Running");
      clearTimeout(limitTimer);
      limitTimer = setTimeout(function () {
        stop("Stopped after " + RUN_LIMIT / 1000 + " s. A clock that runs forever needs a $finish to end the run.");
      }, RUN_LIMIT);
    } else if (m.type === "done") {
      if (m.dropped) say("note", "(" + m.dropped + " more lines were cut. Print less to see them all.)");
      var secs = function (ms) { return (ms / 1000).toFixed(ms < 10000 ? 2 : 1) + " s"; };
      if (m.stage === "compile") {
        say("note", "Compile failed. Click a file:line above to jump to it.");
        setStatus("Compile failed");
      } else {
        if (m.vcd) {
          lastVcd = m.vcd; lastVcdName = m.vcdName;
          outTabs[1].disabled = false;
          say("note", "Waves recorded in " + m.vcdName + ". Open the Waves tab to see them.");
        }
        setStatus((m.exitCode ? "Ended with exit code " + m.exitCode : "Finished") + ", compile " + secs(m.compileMs) + ", run " + secs(m.runMs));
      }
      done(true);
    } else if (m.type === "error") {
      say("err", "Simulator error: " + m.message);
      setStatus("Something went wrong inside the simulator");
      done(false);
      killWorker();
    }
  }

  function done() {
    running = false;
    clearTimeout(limitTimer); clearInterval(tick);
    runBtn.disabled = false; stopBtn.hidden = true;
  }

  function stop(msg) {
    if (!running) return;
    killWorker();
    say("note", msg);
    setStatus(msg.split(".")[0]);
    keepStatus = true;
    done(false);
    startWorker();   // get a fresh one ready for the next run
  }

  // ---------- Waves ----------
  function parseVcd(text) {
    var tok = text.split(/\s+/), i = 0, n = tok.length;
    var sigs = {}, order = [], scope = [], t = 0, tEnd = 0;
    function skipToEnd() { while (i < n && tok[i] !== "$end") i++; i++; }
    function push(id, v) {
      var s = sigs[id];
      if (!s) return;
      var last = s.ch[s.ch.length - 1];
      if (last && last[1] === v) return;
      if (last && last[0] === t) last[1] = v; else s.ch.push([t, v]);
    }
    while (i < n) {
      var k = tok[i];
      if (!k) { i++; continue; }
      if (k === "$scope") { scope.push(tok[i + 2]); i += 3; skipToEnd(); continue; }
      if (k === "$upscope") { scope.pop(); skipToEnd(); continue; }
      if (k === "$var") {
        var type = tok[i + 1], size = parseInt(tok[i + 2], 10), id = tok[i + 3], ref = tok[i + 4];
        var rng = tok[i + 5] && tok[i + 5] !== "$end" ? tok[i + 5] : "";
        var name = scope.slice(1).concat(ref + rng).join(".");
        if (!sigs[id]) { sigs[id] = { id: id, name: name, width: size, type: type, depth: scope.length, ch: [] }; order.push(id); }
        else if (scope.length < sigs[id].depth) { sigs[id].name = name; sigs[id].depth = scope.length; }
        i += 5; skipToEnd(); continue;
      }
      if (k === "$timescale" || k === "$date" || k === "$version" || k === "$comment") { i++; skipToEnd(); continue; }
      if (k.charAt(0) === "$") { i++; continue; }      // $enddefinitions, $dumpvars, $end and friends
      var c = k.charAt(0);
      if (c === "#") { t = parseInt(k.slice(1), 10); if (t > tEnd) tEnd = t; i++; continue; }
      if (c === "b" || c === "B" || c === "r" || c === "R") { push(tok[i + 1], k.slice(1).toLowerCase()); i += 2; continue; }
      if (/[01xzXZ]/.test(c)) { push(k.slice(1), c.toLowerCase()); i++; continue; }
      i++;
    }
    var list = order.map(function (id) { return sigs[id]; }).filter(function (s) { return s.ch.length; });
    list.sort(function (a, b) { return a.depth - b.depth; });
    // A port shows up once per scope, same name and same history: keep the outermost one only
    var seen = {};
    list = list.filter(function (s) {
      var key = s.name.split(".").pop() + "|" + s.width + "|" + JSON.stringify(s.ch);
      if (seen[key]) return false;
      seen[key] = true;
      return true;
    });
    return { sigs: list, tEnd: tEnd };
  }

  function fmtVal(s, v) {
    if (v === undefined) return "";
    if (s.width === 1) return v;
    if (s.type === "real") return String(parseFloat(v));
    if (/[xz]/.test(v)) return /^[x]+$/.test(v) ? "x" : (/^[z]+$/.test(v) ? "z" : "x");
    var bits = v.replace(/^0+(?=.)/, "");
    if ((s.type === "integer" || s.type === "int") && s.width <= 32) {
      var u = parseInt(v, 2);
      if (v.length === s.width && v.charAt(0) === "1" && s.width === 32) u -= 4294967296;
      return String(u);
    }
    if (bits.length <= 6) return String(parseInt(bits, 2));
    var hex = "";
    while (bits.length % 4) bits = "0" + bits;
    for (var j = 0; j < bits.length; j += 4) hex += parseInt(bits.substr(j, 4), 2).toString(16);
    return "h" + hex.replace(/^0+(?=.)/, "");
  }

  var zoom = 1, MAXROWS = 40;
  var NS = "http://www.w3.org/2000/svg";
  function svgEl(tag, attrs, parent) {
    var el = document.createElementNS(NS, tag);
    for (var a in attrs) el.setAttribute(a, attrs[a]);
    if (parent) parent.appendChild(el);
    return el;
  }

  function drawWaves() {
    if (!lastVcd) { wavesBox.textContent = "Nothing recorded. Add $dumpfile(\"wave.vcd\"); $dumpvars(0, tb); to the testbench."; return; }
    if (drawnVcd === lastVcd && wavesBox.firstChild) { layoutWaves(); return; }
    drawnVcd = lastVcd;
    wavesBox.textContent = "";
    var data = parseVcd(lastVcd);
    wavesBox._data = data;
    var bar = document.createElement("div"); bar.className = "w-bar";
    [["Zoom out", 0.5], ["Zoom in", 2], ["Fit", 0]].forEach(function (z) {
      var b = document.createElement("button"); b.type = "button"; b.className = "btn"; b.textContent = z[0];
      b.addEventListener("click", function () { zoom = z[1] ? Math.max(1, Math.min(64, zoom * z[1])) : 1; layoutWaves(); });
      bar.appendChild(b);
    });
    var read = document.createElement("span"); read.className = "w-read"; read.textContent = "Point at the waves to read values";
    bar.appendChild(read);
    wavesBox.appendChild(bar);
    var grid = document.createElement("div"); grid.className = "w-grid";
    var names = document.createElement("div"); names.className = "w-names";
    var scroll = document.createElement("div"); scroll.className = "w-scroll";
    grid.appendChild(names); grid.appendChild(scroll);
    wavesBox.appendChild(grid);
    if (data.sigs.length > MAXROWS) {
      var more = document.createElement("p"); more.className = "w-more";
      more.textContent = "Showing the first " + MAXROWS + " of " + data.sigs.length + " signals. Dump fewer with $dumpvars(1, tb).";
      wavesBox.appendChild(more);
    }
    wavesBox._parts = { names: names, scroll: scroll, read: read };
    zoom = 1;
    layoutWaves();
  }

  function valueAt(s, t) {
    var v;
    for (var j = 0; j < s.ch.length && s.ch[j][0] <= t; j++) v = s.ch[j][1];
    return v;
  }

  function layoutWaves() {
    var data = wavesBox._data, parts = wavesBox._parts;
    if (!data || !parts || wavesBox.hidden) return;
    var sigs = data.sigs.slice(0, MAXROWS);
    var fs = parseFloat(getComputedStyle(wavesBox).fontSize) || 16;
    var rowH = Math.round(fs * 1.9), axisH = Math.round(fs * 1.6), pad = 8;
    var fitW = Math.max(200, parts.scroll.clientWidth - 2);
    var W = Math.round(fitW * zoom), H = axisH + rowH * sigs.length + 4;
    var tEnd = Math.max(1, data.tEnd);
    var X = function (t) { return pad + t / tEnd * (W - 2 * pad); };

    parts.names.textContent = "";
    var head = document.createElement("div"); head.className = "w-name w-axis"; head.style.height = axisH + "px"; head.textContent = "time";
    parts.names.appendChild(head);
    var valSpans = [];
    sigs.forEach(function (s) {
      var row = document.createElement("div"); row.className = "w-name"; row.style.height = rowH + "px";
      var nm = document.createElement("span"); nm.className = "w-n"; nm.textContent = s.name + (s.width > 1 && !/\[/.test(s.name) && s.type !== "integer" && s.type !== "int" ? " [" + (s.width - 1) + ":0]" : "");
      nm.title = s.name;
      var vv = document.createElement("span"); vv.className = "w-v";
      row.appendChild(nm); row.appendChild(vv); parts.names.appendChild(row);
      valSpans.push(vv);
    });

    parts.scroll.textContent = "";
    var svg = svgEl("svg", { width: W, height: H, viewBox: "0 0 " + W + " " + H, role: "img", "aria-label": "Waveforms of " + sigs.length + " signals" }, parts.scroll);
    // time axis with round tick steps
    var raw = tEnd / Math.max(2, Math.floor(W / 90)), mag = Math.pow(10, Math.floor(Math.log10(raw)));
    var step = [1, 2, 5, 10].map(function (m) { return m * mag; }).filter(function (v) { return v >= raw; })[0] || 10 * mag;
    for (var tt = 0; tt <= tEnd + 1e-9; tt += step) {
      svgEl("line", { x1: X(tt), x2: X(tt), y1: axisH - 6, y2: H, "class": "w-grid-ln" }, svg);
      var lab = svgEl("text", { x: X(tt) + 3, y: axisH - 9, "class": "w-t" }, svg);
      lab.textContent = String(+tt.toPrecision(6));
    }
    sigs.forEach(function (s, r) {
      var top = axisH + r * rowH, hi = top + rowH * 0.22, lo = top + rowH * 0.78, mid = (hi + lo) / 2;
      svgEl("line", { x1: 0, x2: W, y1: top + rowH, y2: top + rowH, "class": "w-row-ln" }, svg);
      var ch = s.ch;
      if (s.width === 1 && s.type !== "real") {
        var d = "", prevY = null;
        for (var j = 0; j < ch.length; j++) {
          var x1 = X(ch[j][0]), x2 = X(j + 1 < ch.length ? ch[j + 1][0] : tEnd), v = ch[j][1];
          if (v === "x" || v === "z") {
            svgEl("rect", { x: x1, y: hi, width: Math.max(1, x2 - x1), height: lo - hi, "class": v === "x" ? "w-x" : "w-z" }, svg);
            prevY = null; continue;
          }
          var y = v === "1" ? hi : lo;
          d += (prevY === null ? "M" + x1 + " " + y : "L" + x1 + " " + prevY + " L" + x1 + " " + y) + " L" + x2 + " " + y + " ";
          prevY = y;
        }
        if (d) svgEl("path", { d: d, "class": "w-bit" }, svg);
      } else {
        for (var k = 0; k < ch.length; k++) {
          var a = X(ch[k][0]), b = X(k + 1 < ch.length ? ch[k + 1][0] : tEnd), e = Math.min(4, (b - a) / 2);
          var txt = fmtVal(s, ch[k][1]), bad = txt === "x" || txt === "z";
          svgEl("polygon", { points: [a, mid, a + e, hi, b - e, hi, b, mid, b - e, lo, a + e, lo].join(" "), "class": bad ? "w-x" : "w-bus" }, svg);
          if (b - a > txt.length * fs * 0.55 + 8) {
            var tx = svgEl("text", { x: (a + b) / 2, y: mid + fs * 0.32, "class": "w-bt" }, svg);
            tx.textContent = txt;
          }
        }
      }
    });
    var cursor = svgEl("line", { x1: -10, x2: -10, y1: 0, y2: H, "class": "w-cur" }, svg);
    function readAt(clientX) {
      var rect = svg.getBoundingClientRect();
      var x = Math.max(pad, Math.min(W - pad, clientX - rect.left));
      var t = Math.round((x - pad) / (W - 2 * pad) * tEnd);
      cursor.setAttribute("x1", X(t)); cursor.setAttribute("x2", X(t));
      parts.read.textContent = "time " + t;
      sigs.forEach(function (s, r) { valSpans[r].textContent = fmtVal(s, valueAt(s, t)); });
    }
    svg.addEventListener("pointermove", function (ev) { readAt(ev.clientX); });
    svg.addEventListener("pointerdown", function (ev) { readAt(ev.clientX); });
  }
  window.addEventListener("resize", function () { if (!wavesBox.hidden) layoutWaves(); });

  window.EECode = { open: open, load: load, run: run };
})();
