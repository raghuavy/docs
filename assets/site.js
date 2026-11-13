// Text size buttons. The chosen size is remembered in this browser only.
(function () {
  var root = document.documentElement;
  var buttons = document.querySelectorAll(".sizer button");
  function apply(size) {
    root.setAttribute("data-size", size);
    buttons.forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-size") === size ? "true" : "false");
    });
  }
  apply(root.getAttribute("data-size") || "2");
  buttons.forEach(function (b) {
    b.addEventListener("click", function () {
      var size = b.getAttribute("data-size");
      apply(size);
      try { localStorage.setItem("ee8350-size", size); } catch (e) {}
    });
  });
})();
