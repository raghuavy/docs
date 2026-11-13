// Lectures 14 to 16. Runs in the browser. Open Waves after it runs.
// What the sampled value functions mean, built from a flop that remembers last
// cycle's value. This simulator has no assert property, so the sequence
//   start ##1 busy ##1 done
// is checked by a small state machine, one attempt at a time.
module tb;
  logic clk = 0, a = 0, start = 0, busy = 0, done = 0;
  logic a_past = 0;                  // $past(a): the value at the last clock edge
  int cycle = 0, state = 0;

  always #5 clk = ~clk;

  always @(posedge clk) begin
    cycle <= cycle + 1;
    a_past <= a;
    if ( a && !a_past) $display("[cycle %0d] $rose(a)",   cycle);
    if (!a &&  a_past) $display("[cycle %0d] $fell(a)",   cycle);
    if ( a &&  a_past) $display("[cycle %0d] $stable(a), still 1", cycle);

    case (state)                     // start ##1 busy ##1 done
      0: if (start) state <= 1;
      1: if (busy) state <= 2; else begin state <= 0; $display("[cycle %0d] sequence FAIL: busy missing", cycle); end
      2: begin
           state <= 0;
           if (done) $display("[cycle %0d] sequence matched: start, busy, done", cycle);
           else      $display("[cycle %0d] sequence FAIL: done missing", cycle);
         end
    endcase
  end

  initial begin
    $dumpfile("wave.vcd");
    $dumpvars(0, tb);
    @(negedge clk) a = 1;
    @(negedge clk); @(negedge clk) a = 0;
    @(negedge clk) start = 1;
    @(negedge clk) begin start = 0; busy = 1; end
    @(negedge clk) begin busy = 0; done = 1; end
    @(negedge clk) begin done = 0; start = 1; end
    @(negedge clk) start = 0;          // busy never comes this time
    repeat (2) @(negedge clk);
    $finish;
  end
endmodule
