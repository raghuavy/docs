// Lecture 10. Runs in the browser. Open Waves after it runs.
// Immediate assertions work here. Concurrent ones (assert property) do not, so the
// property  req |-> ##4 grant  is checked by hand: every req starts its own attempt,
// and each attempt looks for grant exactly 4 clocks later. Edit the grant cycle
// below and run again.
module tb;
  logic clk = 0, req = 0, grant = 0;
  int cycle = 0;
  logic [4:0] pending = 0;           // bit i: an attempt that started i clocks ago
  int passes, fails;

  always #5 clk = ~clk;
  always @(posedge clk) cycle <= cycle + 1;

  always @(posedge clk) begin
    if (pending[3]) begin            // this attempt started 4 clocks ago
      if (grant) begin passes++; $display("[cycle %0d] pass: grant came 4 clocks after req", cycle); end
      else       begin fails++;  $display("[cycle %0d] FAIL: no grant 4 clocks after the req at cycle %0d", cycle, cycle - 4); end
    end
    pending <= {pending[3:0], req};  // start a new attempt when req is high
  end

  initial begin
    $dumpfile("wave.vcd");
    $dumpvars(0, tb);
    repeat (12) begin
      @(negedge clk);
      req   = (cycle == 1 || cycle == 3);
      grant = (cycle == 7);
      assert (!(req && grant)) else $error("req and grant high together");  // immediate
    end
    $display("%0d passed, %0d failed", passes, fails);
    $finish;
  end
endmodule
