// EE 8350 guide. Text size, theme, split view, notes, editors and problems.
// Everything a reader saves (notes, answers, progress, settings) stays in this browser's localStorage.
(function () {
  "use strict";
  var d = document.documentElement;
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
  };
  var embedded = d.classList.contains("embedded");
  var frame = document.getElementById("sideFrame");

  function syncFrame() {
    if (!frame) return;
    try {
      var fd = frame.contentDocument && frame.contentDocument.documentElement;
      if (!fd) return;
      fd.setAttribute("data-size", d.getAttribute("data-size") || "2");
      var th = d.getAttribute("data-theme");
      if (th) fd.setAttribute("data-theme", th); else fd.removeAttribute("data-theme");
    } catch (e) {}
  }

  // ---------- Text size ----------
  var sizeBtns = document.querySelectorAll(".sizer button");
  function applySize(size) {
    d.setAttribute("data-size", size);
    sizeBtns.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-size") === size)); });
    syncFrame();
  }
  applySize(d.getAttribute("data-size") || "2");
  sizeBtns.forEach(function (b) {
    b.addEventListener("click", function () { applySize(b.getAttribute("data-size")); store.set("ee8350-size", b.getAttribute("data-size")); });
  });

  // ---------- Theme ----------
  var themeBtns = document.querySelectorAll("[data-theme-set]");
  function applyTheme(t) {
    if (t === "light" || t === "dark") d.setAttribute("data-theme", t); else { d.removeAttribute("data-theme"); t = "auto"; }
    themeBtns.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-theme-set") === t)); });
    syncFrame();
  }
  applyTheme(store.get("ee8350-theme") || "auto");
  themeBtns.forEach(function (b) {
    b.addEventListener("click", function () { applyTheme(b.getAttribute("data-theme-set")); store.set("ee8350-theme", b.getAttribute("data-theme-set")); });
  });

  // ---------- Split view ----------
  var splitBtn = document.querySelector(".split-btn");
  var tabs = document.querySelectorAll(".seg [data-mode]");
  var panels = document.querySelectorAll("[data-panel]");
  var pick = document.getElementById("pagePick");

  function loadFrame() {
    if (!frame || !pick) return;
    if (frame.getAttribute("src") !== pick.value) frame.setAttribute("src", pick.value);
  }
  function setMode(m) {
    tabs.forEach(function (t) { t.setAttribute("aria-selected", String(t.getAttribute("data-mode") === m)); });
    panels.forEach(function (p) { p.hidden = p.getAttribute("data-panel") !== m; });
    store.set("ee8350-sidemode", m);
    if (m === "page") loadFrame();
  }
  function setSplit(on, save) {
    d.classList.toggle("split", on);
    if (splitBtn) splitBtn.setAttribute("aria-pressed", String(on));
    if (save) store.set("ee8350-split", on ? "on" : "off");
    if (on && store.get("ee8350-sidemode") === "page") loadFrame();
  }

  if (!embedded && splitBtn) {
    setSplit(d.classList.contains("split"), false);
    splitBtn.addEventListener("click", function () { setSplit(!d.classList.contains("split"), true); });
    var closeBtn = document.querySelector(".side-close");
    if (closeBtn) closeBtn.addEventListener("click", function () { setSplit(false, true); splitBtn.focus(); });

    tabs.forEach(function (t) { t.addEventListener("click", function () { setMode(t.getAttribute("data-mode")); }); });
    if (pick) {
      var savedPage = store.get("ee8350-sidepage");
      if (savedPage) {
        for (var i = 0; i < pick.options.length; i++) {
          var val = pick.options[i].value.replace(/^(\.\.\/)+/, "");
          if (val === savedPage) { pick.selectedIndex = i; break; }
        }
      }
      pick.addEventListener("change", function () {
        store.set("ee8350-sidepage", pick.value.replace(/^(\.\.\/)+/, ""));
        frame.setAttribute("src", pick.value);
      });
    }
    if (frame) frame.addEventListener("load", syncFrame);
    setMode(store.get("ee8350-sidemode") || "notes");

    // Divider: drag with the mouse, or use the arrow keys
    var divider = document.getElementById("divider");
    var layout = document.getElementById("layout");
    var setWidth = function (pct) {
      pct = Math.max(30, Math.min(75, pct));
      d.style.setProperty("--split-w", pct.toFixed(1) + "%");
      store.set("ee8350-splitw", pct.toFixed(1));
    };
    if (divider && layout) {
      divider.addEventListener("pointerdown", function (e) {
        e.preventDefault();
        divider.setPointerCapture(e.pointerId);
        if (frame) frame.style.pointerEvents = "none";
        var rect = layout.getBoundingClientRect();
        var move = function (ev) { setWidth((ev.clientX - rect.left) / rect.width * 100); };
        var up = function () {
          divider.removeEventListener("pointermove", move);
          divider.removeEventListener("pointerup", up);
          if (frame) frame.style.pointerEvents = "";
        };
        divider.addEventListener("pointermove", move);
        divider.addEventListener("pointerup", up);
      });
      divider.addEventListener("keydown", function (e) {
        var cur = parseFloat(getComputedStyle(d).getPropertyValue("--split-w")) || 56;
        if (e.key === "ArrowLeft") { setWidth(cur - 2); e.preventDefault(); }
        if (e.key === "ArrowRight") { setWidth(cur + 2); e.preventDefault(); }
      });
    }

    // Notes, saved per page
    var notes = document.querySelector("textarea.notes");
    var status = document.querySelector(".note-status");
    if (notes) {
      var nkey = "ee8350-notes-" + notes.getAttribute("data-key");
      notes.value = store.get(nkey) || "";
      var timer = null;
      notes.addEventListener("input", function () {
        clearTimeout(timer);
        timer = setTimeout(function () { store.set(nkey, notes.value); if (status) status.textContent = "Saved in this browser"; }, 400);
      });
      var dl = document.querySelector(".note-dl");
      if (dl) dl.addEventListener("click", function () {
        var blob = new Blob([notes.value], { type: "text/plain" });
        var a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "ee8350-notes-" + notes.getAttribute("data-key") + ".txt";
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
      });
      var clr = document.querySelector(".note-clear");
      var armed = null;
      if (clr) clr.addEventListener("click", function () {
        if (!armed) {
          clr.textContent = "Click again to clear";
          armed = setTimeout(function () { clr.textContent = "Clear"; armed = null; }, 4000);
          return;
        }
        clearTimeout(armed); armed = null; clr.textContent = "Clear";
        notes.value = ""; store.set(nkey, "");
        if (status) status.textContent = "Notes cleared";
        notes.focus();
      });
    }
  }

  // ---------- Editors with auto indent ----------
  var UNIT = "  ";
  var OPEN_KW = /^((virtual|static|local|protected|automatic)\s+)*(class|module|interface|program|package|function|task|covergroup|property|sequence|clocking|checker|generate)\b/;
  var OPEN_STMT = /^(initial|final|always\w*|forever|repeat|for|foreach|while|if|else|case\w*|do)\b/;

  function opensBlock(text, mode) {
    var t = text.replace(/\/\/.*$/, "").trim();
    if (!t) return false;
    if (mode === "notes") return /:$/.test(t);
    if (/\b(begin|fork)$/.test(t) || /[{(\[]$/.test(t)) return true;
    if (/^(extern|pure)\b/.test(t)) return false;
    if (OPEN_KW.test(t)) return !/\bend\w*\b/.test(t);
    if (OPEN_STMT.test(t) && !/;$/.test(t)) return true;
    return /:$/.test(t);
  }

  function insertText(ta, text) {
    ta.focus();
    var ok = false;
    try { ok = document.execCommand("insertText", false, text); } catch (e) { ok = false; }
    if (!ok) {
      ta.setRangeText(text, ta.selectionStart, ta.selectionEnd, "end");
      ta.dispatchEvent(new Event("input", { bubbles: true }));
    }
  }

  function shiftLines(ta, dir, wholeLine) {
    var v = ta.value, s = ta.selectionStart, e = ta.selectionEnd;
    var ls = v.lastIndexOf("\n", s - 1) + 1;
    if (s === e && dir > 0 && !wholeLine) { insertText(ta, UNIT); return; }
    var endAt = (e > s && v[e - 1] === "\n") ? e - 1 : e;
    var le = v.indexOf("\n", endAt); if (le < 0) le = v.length;
    var lines = v.slice(ls, le).split("\n");
    var firstDelta = 0;
    var out = lines.map(function (l, k) {
      if (dir > 0) { if (k === 0) firstDelta = UNIT.length; return UNIT + l; }
      var m = l.match(/^( {1,2}|\t)/);
      if (k === 0) firstDelta = m ? -m[0].length : 0;
      return m ? l.slice(m[0].length) : l;
    }).join("\n");
    ta.setSelectionRange(ls, le);
    insertText(ta, out);
    if (s === e) { var c = Math.max(ls, s + firstDelta); ta.setSelectionRange(c, c); }
    else ta.setSelectionRange(ls, ls + out.length);
  }

  function attachEditor(ta) {
    var mode = ta.getAttribute("data-indent");
    var gutter = ta.parentElement && ta.parentElement.querySelector(".gutter");
    var key = ta.getAttribute("data-key");
    var isNotes = ta.classList.contains("notes");

    function renumber() {
      if (!gutter) return;
      var n = ta.value.split("\n").length, out = [];
      for (var i = 1; i <= n; i++) out.push(i);
      gutter.textContent = out.join("\n");
      gutter.scrollTop = ta.scrollTop;
    }
    if (key && !isNotes) {
      var saved = store.get("ee8350-" + key);
      if (saved) ta.value = saved;
      var t2 = null;
      ta.addEventListener("input", function () { clearTimeout(t2); t2 = setTimeout(function () { store.set("ee8350-" + key, ta.value); }, 400); });
    }
    if (gutter) { ta.addEventListener("input", renumber); ta.addEventListener("scroll", function () { gutter.scrollTop = ta.scrollTop; }); renumber(); }

    ta.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { ta._esc = true; return; }
      if (e.key === "Tab" && !e.ctrlKey && !e.metaKey && !e.altKey) {
        if (ta._esc) { ta._esc = false; return; }
        e.preventDefault(); shiftLines(ta, e.shiftKey ? -1 : 1, mode === "notes"); return;
      }
      ta._esc = false;
      if (e.key !== "Enter" || e.shiftKey || e.ctrlKey || e.metaKey || e.altKey || e.isComposing) return;
      var v = ta.value, s = ta.selectionStart;
      var ls = v.lastIndexOf("\n", s - 1) + 1;
      var before = v.slice(ls, s);
      var indent = before.match(/^[ \t]*/)[0];
      var trimmed = before.trim();
      var marker = "";
      if (mode === "notes") {
        var m = trimmed.match(/^([-*•]|\d+[.)])(?:\s+(.*))?$/);
        if (m) {
          if (!m[2]) {
            e.preventDefault();
            ta.setSelectionRange(ls, s);
            insertText(ta, indent);
            return;
          }
          var mk = m[1], num = mk.match(/^\d+/);
          if (num) mk = (parseInt(num[0], 10) + 1) + mk.slice(num[0].length);
          marker = mk + " ";
        }
      }
      var add = opensBlock(trimmed, mode) ? UNIT : "";
      e.preventDefault();
      var after = v.charAt(ta.selectionEnd);
      if (mode === "code" && add && /[})\]]/.test(after) && /[{(\[]$/.test(trimmed)) {
        insertText(ta, "\n" + indent + add + "\n" + indent);
        var c = s + 1 + indent.length + add.length;
        ta.setSelectionRange(c, c);
      } else {
        insertText(ta, "\n" + indent + add + marker);
      }
    });

    if (mode === "code") {
      ta.addEventListener("input", function (e) {
        if (e.inputType && e.inputType.indexOf("insert") !== 0) return;
        var v = ta.value, s = ta.selectionStart;
        if (s !== ta.selectionEnd) return;
        var ls = v.lastIndexOf("\n", s - 1) + 1;
        var le = v.indexOf("\n", s); if (le < 0) le = v.length;
        if (s !== le) return;
        var line = v.slice(ls, le);
        var m = line.match(/^([ \t]+)(end\w*|join(_any|_none)?|[})\]])$/);
        if (!m || ta._dedented === ls) return;
        var pe = ls - 1, prev = "";
        while (pe > 0) {
          var ps = v.lastIndexOf("\n", pe - 1) + 1, l = v.slice(ps, pe);
          if (l.trim()) { prev = l; break; }
          pe = ps - 1;
        }
        var prevIndent = (prev.match(/^[ \t]*/) || [""])[0];
        var target = opensBlock(prev.trim(), "code") ? prevIndent : prevIndent.slice(0, Math.max(0, prevIndent.length - UNIT.length));
        ta._dedented = ls;
        if (m[1].length <= target.length) return;
        ta.setSelectionRange(ls, ls + m[1].length);
        insertText(ta, target);
        var c = ls + target.length + m[2].length;
        ta.setSelectionRange(c, c);
      });
    }
  }
  document.querySelectorAll("textarea[data-indent]").forEach(attachEditor);

  // ---------- Copy buttons on code ----------
  document.querySelectorAll("details.code, .tryit, .cmd, main > pre").forEach(function (box) {
    var pre = box.tagName === "PRE" ? box : box.querySelector("pre");
    if (!pre || pre.nextElementSibling && pre.nextElementSibling.classList.contains("copy-btn")) return;
    var b = document.createElement("button");
    b.type = "button"; b.className = "btn copy-btn"; b.textContent = "Copy";
    b.addEventListener("click", function () {
      var text = pre.innerText.replace(/\n$/, "");
      var done = function () { b.textContent = "Copied"; setTimeout(function () { b.textContent = "Copy"; }, 1500); };
      var fallback = function () {
        var r = document.createRange(); r.selectNodeContents(pre);
        var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r);
        b.textContent = "Selected, press Ctrl+C";
      };
      if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(done, fallback);
      else fallback();
    });
    pre.insertAdjacentElement("afterend", b);
  });

  // ---------- Problems ----------
  function loadSolved() { try { return JSON.parse(store.get("ee8350-solved") || "{}") || {}; } catch (e) { return {}; } }
  function saveSolved(o) { store.set("ee8350-solved", JSON.stringify(o)); }

  function norm(s) { return String(s).toLowerCase().replace(/\s+/g, "").replace(/\.$/, ""); }
  function normList(s) {
    return String(s).toLowerCase().replace(/[\[\]]/g, "").replace(/\band\b/g, ",")
      .replace(/[\s,;]+/g, ",").replace(/^,+|,+$/g, "");
  }
  function parseNum(raw) {
    var s = String(raw).toLowerCase().replace(/\s+/g, "").replace(/,/g, "");
    var scale = 1;
    if (/(%|percent)$/.test(s)) { scale = 0.01; s = s.replace(/(%|percent)$/, ""); }
    s = s.replace(/(\*|x|×)10\^\(?(-?\d+)\)?$/, "e$2").replace(/^10\^\(?(-?\d+)\)?$/, "1e$1");
    var num = "-?(?:\\d+\\.?\\d*|\\.\\d+)(?:e[+-]?\\d+)?";
    var frac = s.match(new RegExp("^(" + num + ")/(" + num + ")$"));
    if (frac) { var b = Number(frac[2]); return b ? Number(frac[1]) / b * scale : null; }
    if (new RegExp("^" + num + "$").test(s)) return Number(s) * scale;
    return null;
  }
  function fieldOk(val, f) {
    if (val === null || val === undefined || String(val).trim() === "") return false;
    for (var i = 0; i < f.a.length; i++) {
      var a = f.a[i];
      if (typeof a === "number") {
        var x = parseNum(val);
        if (x === null) continue;
        var tol = (f.tol !== undefined ? f.tol : 0) + 1e-9;
        if (Math.abs(x - a) <= tol) return true;
        if (f.pct && Math.abs(x - a / 100) <= tol / 100) return true;
      } else if (f.opt) {
        if (val === a) return true;
      } else if (f.list) {
        if (normList(val) === normList(a)) return true;
      } else if (norm(val) === norm(a)) return true;
    }
    return false;
  }
  function buggyAdder(a, b) {
    function fa(x, y, ci) { return [x ^ y ^ ci, (x & y) | ((x ^ y) & ci)]; }
    function bit(v, i) { return (v >> i) & 1; }
    var r0 = fa(bit(a, 0), bit(b, 0), 0);
    var r1 = fa(bit(a, 1), bit(b, 1), r0[1]);
    var r2 = fa(bit(a, 2), bit(b, 2), r0[1]);   // the planted bug, c0 instead of c1
    var r3 = fa(bit(a, 3), bit(b, 3), r2[1]);
    return r0[0] | (r1[0] << 1) | (r2[0] << 2) | (r3[0] << 3) | (r3[1] << 4);
  }

  document.querySelectorAll("section.problems").forEach(function (sec) {
    var rows = Array.prototype.slice.call(sec.querySelectorAll(".prob-row"));
    var probs = Array.prototype.slice.call(sec.querySelectorAll(".prob"));
    var prog = sec.querySelector(".prob-progress");
    var curKey = "ee8350-pcur-" + sec.getAttribute("data-lecture");

    function refresh() {
      var solved = loadSolved(), n = 0;
      probs.forEach(function (p, i) {
        var ok = !!solved[p.getAttribute("data-id")];
        rows[i].classList.toggle("solved", ok);
        rows[i].querySelector(".pstat").setAttribute("aria-label", ok ? "solved" : "not solved yet");
        if (ok) n++;
      });
      prog.textContent = n + " of " + probs.length + " solved";
    }
    function mark(p, ok) {
      var solved = loadSolved();
      if (ok) solved[p.getAttribute("data-id")] = true; else delete solved[p.getAttribute("data-id")];
      saveSolved(solved); refresh();
    }
    function show(i, focus) {
      if (i < 0 || i >= probs.length) return;
      probs.forEach(function (p, k) { p.hidden = k !== i; });
      rows.forEach(function (r, k) { r.setAttribute("aria-current", String(k === i)); });
      store.set(curKey, String(i));
      if (focus) { var h = probs[i].querySelector("h4"); h.setAttribute("tabindex", "-1"); h.focus(); }
    }
    function verdict(p, cls, title, text, selfMark) {
      var v = p.querySelector(".verdict");
      v.className = "verdict" + (cls ? " " + cls : "");
      v.innerHTML = "";
      var t = document.createElement("span"); t.className = "v-title"; t.textContent = title; v.appendChild(t);
      v.appendChild(document.createTextNode(text));
      if (selfMark) {
        var box = document.createElement("div"); box.className = "self";
        var yes = document.createElement("button"); yes.type = "button"; yes.className = "btn"; yes.textContent = "I solved it";
        var no = document.createElement("button"); no.type = "button"; no.className = "btn"; no.textContent = "Not yet";
        yes.addEventListener("click", function () { mark(p, true); verdict(p, "ok", "Marked as solved", " Nice work."); });
        no.addEventListener("click", function () { mark(p, false); verdict(p, "", "Not yet", " Read the solution, then try writing it again without looking."); });
        box.appendChild(yes); box.appendChild(no); v.appendChild(box);
      }
    }
    function showSolution(p, on) {
      var sol = p.querySelector(".solution"), btn = p.querySelector(".show-sol");
      sol.hidden = !on; btn.textContent = on ? "Hide solution" : "Show solution";
    }

    function grade(p, spec) {
      var t = spec.t;
      if (t === "code" || t === "explain") {
        var ta = p.querySelector("textarea");
        if (!ta.value.trim()) { verdict(p, "", "Nothing to submit yet", " Write your answer in the box first."); return; }
        showSolution(p, true);
        verdict(p, "", "Submitted", " Compare your answer with the reference solution below, then mark it.", true);
        return;
      }
      if (t === "choice") {
        var c = p.querySelector("input[type=radio]:checked");
        if (!c) { verdict(p, "", "Pick an option first", ""); return; }
        if (Number(c.value) === spec.a) { mark(p, true); verdict(p, "ok", "Accepted", " That is the right one. Open the solution to check the reasoning."); }
        else verdict(p, "no", "Not quite", " That option is not the right one. Try again, or open the solution.");
        return;
      }
      if (t === "multi") {
        var picked = Array.prototype.map.call(p.querySelectorAll("input[type=checkbox]:checked"), function (x) { return Number(x.value); }).sort();
        if (!picked.length) { verdict(p, "", "Select at least one option", ""); return; }
        var want = spec.a.slice().sort();
        if (picked.join(",") === want.join(",")) { mark(p, true); verdict(p, "ok", "Accepted", " Exactly the right set."); }
        else verdict(p, "no", "Not quite", " Your selection is not exactly the right set. Try again, or open the solution.");
        return;
      }
      if (t === "order") {
        var inp = p.querySelector("[data-k]");
        var words = (inp.value.toLowerCase().match(/[a-z]+/g) || []).filter(function (w) { return spec.tok.indexOf(w) >= 0; });
        if (!words.length) { verdict(p, "", "Type the names first", ""); return; }
        if (words.join(",") === spec.tok.join(",")) { mark(p, true); verdict(p, "ok", "Accepted", " Right order."); }
        else verdict(p, "no", "Not quite", " The order is off somewhere. Try again, or open the solution.");
        return;
      }
      var ins = Array.prototype.slice.call(p.querySelectorAll("[data-k]"));
      if (ins.some(function (x) { return !x.value.trim(); })) { verdict(p, "", "Fill in every box first", ""); return; }
      if (t === "custom" && spec.fn === "adder_bug") {
        var a = parseNum(ins[0].value), b = parseNum(ins[1].value);
        if (a === null || b === null || a % 1 || b % 1 || a < 0 || b < 0 || a > 15 || b > 15) {
          verdict(p, "", "Use whole numbers from 0 to 15", ""); return;
        }
        var got = buggyAdder(a, b);
        if (got === a + b) { mark(p, true); verdict(p, "ok", "Accepted", " The buggy adder gives " + got + ", the same as a + b, so this input slips past the bug."); }
        else verdict(p, "no", "Not quite", " The buggy adder gives " + got + " but a + b is " + (a + b) + ", so the scoreboard would catch this one.");
        return;
      }
      var wrong = 0;
      ins.forEach(function (x) { if (!fieldOk(x.value, spec.f[Number(x.getAttribute("data-k"))])) wrong++; });
      if (!wrong) { mark(p, true); verdict(p, "ok", "Accepted", " All answers match. Open the solution to check the reasoning."); }
      else verdict(p, "no", "Not quite", " " + wrong + " of your " + ins.length + (ins.length === 1 ? " answer" : " answers") + (wrong === 1 ? " is" : " are") + " off. Try again, or open the solution.");
    }

    probs.forEach(function (p, i) {
      var spec = JSON.parse(p.getAttribute("data-check"));
      p.querySelector(".submit").addEventListener("click", function () { grade(p, spec); });
      p.querySelector(".show-sol").addEventListener("click", function () { showSolution(p, p.querySelector(".solution").hidden); });
      var prev = p.querySelector(".prev-p"), next = p.querySelector(".next-p");
      prev.disabled = i === 0; next.disabled = i === probs.length - 1;
      prev.addEventListener("click", function () { show(i - 1, true); });
      next.addEventListener("click", function () { show(i + 1, true); });
      p.querySelectorAll("input[type=text]").forEach(function (x) {
        x.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); grade(p, spec); } });
      });
    });
    rows.forEach(function (r, i) { r.addEventListener("click", function () { show(i, true); }); });

    refresh();
    var saved = parseInt(store.get(curKey), 10);
    if (isNaN(saved)) {
      var solved = loadSolved();
      saved = probs.findIndex(function (p) { return !solved[p.getAttribute("data-id")]; });
      if (saved < 0) saved = 0;
    }
    show(Math.min(saved, probs.length - 1), false);
  });
})();
