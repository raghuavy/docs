// Lectures 16 to 18. Runs in the browser.
// The repetition operators, checked by hand on one recorded trace of b.
// For each start cycle it asks: does  b[*2]  (two in a row), b[->2]  (the second b,
// ending on it) and  b[=2]  (exactly two b, may end later) match from here?
// Change the trace and run again.
module tb;
  bit trace [10] = '{0, 1, 1, 0, 1, 0, 0, 1, 0, 0};

  function automatic int consec2(int st);       // b[*2] from st: ends at st+1 or -1
    if (st + 1 < 10 && trace[st] && trace[st + 1]) return st + 1;
    return -1;
  endfunction

  function automatic int goto2(int st);         // b[->2]: ends on the 2nd b
    int seen = 0;
    for (int i = st; i < 10; i++) begin
      if (trace[i]) seen++;
      if (seen == 2) return i;
    end
    return -1;
  endfunction

  function automatic string nonconsec2(int st); // b[=2]: any end after the 2nd b, before a 3rd
    int seen = 0, first = -1, last = -1;
    for (int i = st; i < 10; i++) begin
      if (trace[i]) seen++;
      if (seen == 2 && first < 0) first = i;
      if (seen == 3) begin last = i - 1; break; end
    end
    if (first < 0) return "no match";
    if (last < 0) last = 9;
    return $sformatf("ends at %0d to %0d", first, last);
  endfunction

  function automatic string ends(int e);
    if (e < 0) return "no match";
    return $sformatf("ends at %0d", e);
  endfunction

  initial begin
    $write("trace of b, cycles 0 to 9: ");
    foreach (trace[i]) $write("%0d", trace[i]);
    $display("");
    for (int st = 0; st < 6; st++)
      $display("start %0d:  b[*2] %-12s b[->2] %-12s b[=2] %s", st, ends(consec2(st)), ends(goto2(st)), nonconsec2(st));
    $finish;
  end
endmodule
