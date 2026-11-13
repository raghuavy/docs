// Lecture 3. Runs in the browser.
// This simulator has no constraint solver, so randomize() and constraint blocks
// are not available here. Instead this builds the same ideas by hand, which is
// close to what a solver does for you. The real syntax is in the comments.
// Use the Codespace playground to run real constraints.
module tb;
  int a, b, tries, total_tries;
  int hist [4];
  int pick;

  // constraint c_order { a < b; }      written as: draw again until it holds
  task automatic draw_ab();
    tries = 0;
    do begin
      a = $urandom_range(0, 15);
      b = $urandom_range(0, 15);
      tries++;
    end while (!(a < b));
    total_tries += tries;
  endtask

  // constraint c_mode { mode dist {0 := 40, 1 := 30, 2 := 20, 3 := 10}; }
  function automatic int pick_mode();
    int r = $urandom_range(0, 99);   // 0 to 99, then cut it into 40, 30, 20, 10
    if (r < 40) return 0;
    if (r < 70) return 1;
    if (r < 90) return 2;
    return 3;
  endfunction

  initial begin
    repeat (5) begin
      draw_ab();
      $display("a = %2d, b = %2d   (took %0d draws)", a, b, tries);
    end
    $display("average draws for a < b: %0.2f", total_tries / 5.0);

    repeat (1000) begin
      pick = pick_mode();
      hist[pick]++;
    end
    $display("mode weights 40 30 20 10, counts from 1000 draws:");
    foreach (hist[i]) $display("  mode %0d: %4d", i, hist[i]);
    $finish;
  end
endmodule
