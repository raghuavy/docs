// Lecture 4. Runs in the browser.
// This simulator has no covergroup, so this counts the bins by hand.
// It is what  coverpoint op { bins add = {0}; bins sub = {1}; bins logic_ops = {[2:3]}; }
// does for you. Change how many times you sample and watch the percent move.
module tb;
  int bins_hit [3];                  // add, sub, logic_ops
  string names [3] = '{"add", "sub", "logic_ops"};
  int auto_hit [16];                 // auto bins for a 4 bit value: one per value
  int op, val, covered, auto_covered;

  task automatic sample(int op, int val);
    if (op == 0)      bins_hit[0]++;
    else if (op == 1) bins_hit[1]++;
    else              bins_hit[2]++;
    auto_hit[val]++;
  endtask

  initial begin
    repeat (6) begin
      op  = $urandom_range(0, 3);
      val = $urandom_range(0, 15);
      sample(op, val);
    end

    foreach (bins_hit[i]) begin
      $display("bin %-10s hit %0d times", names[i], bins_hit[i]);
      if (bins_hit[i] > 0) covered++;
    end
    $display("op coverage: %0d of 3 bins = %0.2f%%", covered, 100.0 * covered / 3);

    foreach (auto_hit[i]) if (auto_hit[i] > 0) auto_covered++;
    $display("val coverage with 16 auto bins: %0d of 16 = %0.2f%%", auto_covered, 100.0 * auto_covered / 16);
    $finish;
  end
endmodule
