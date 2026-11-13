// Lectures 13 and 14. Runs in the browser.
// Cross coverage, a transition bin and an illegal bin, counted by hand because this
// simulator has no covergroup. The grid printed at the end is the cross of
// kind (read, write) with size (1, 2, 4 bytes). Raise the sample count and run again.
module tb;
  string kinds [2] = '{"read ", "write"};
  int    sizes [3] = '{1, 2, 4};
  int    cross_hit [2][3];
  int    trans_hit;                   // transition bin: a read straight after a write
  int    illegal;                     // illegal bin: a 4 byte write
  int    k, s, prev_k = -1, covered;

  initial begin
    repeat (8) begin
      k = $urandom_range(0, 1);
      s = $urandom_range(0, 2);
      cross_hit[k][s]++;
      if (prev_k == 1 && k == 0) trans_hit++;
      if (k == 1 && s == 2) begin
        illegal++;
        $display("illegal bin hit: a 4 byte write");
      end
      prev_k = k;
    end

    $display("cross of kind x size, hits per cell:");
    $display("          1B   2B   4B");
    for (int i = 0; i < 2; i++) begin
      $display("  %s %4d %4d %4d", kinds[i], cross_hit[i][0], cross_hit[i][1], cross_hit[i][2]);
      for (int j = 0; j < 3; j++) if (cross_hit[i][j] > 0 && !(i == 1 && j == 2)) covered++;
    end
    // the illegal cell does not count toward coverage, so there are 5 legal cells
    $display("cross coverage: %0d of 5 legal cells = %0.2f%%", covered, 100.0 * covered / 5);
    $display("write then read transition hit %0d times", trans_hit);
    $finish;
  end
endmodule
