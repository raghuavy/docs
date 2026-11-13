// Lecture 19. Try:  ./run --wave 19-cdc/sync.sv   then open wave.vcd
// A fast clock and a slow clock, a two flop synchronizer, and a Gray code counter with an assertion.
module sync2 (input logic dst_clk, rst_n, d_async, output logic q_sync);
  logic meta;
  always_ff @(posedge dst_clk or negedge rst_n)
    if (!rst_n) {q_sync, meta} <= '0;
    else        {q_sync, meta} <= {meta, d_async};
endmodule

module tb;
  bit fast_clk, slow_clk, rst_n;
  always #3 fast_clk = ~fast_clk;          // period 6
  always #7 slow_clk = ~slow_clk;          // period 14, unrelated to 6

  logic flag, flag_sync;
  sync2 u_sync (.dst_clk(slow_clk), .rst_n(rst_n), .d_async(flag), .q_sync(flag_sync));

  // A 3 bit counter in the fast domain, and its Gray code version
  logic [2:0] bin, gray;
  always_ff @(posedge fast_clk or negedge rst_n)
    if (!rst_n) bin <= '0; else bin <= bin + 1;
  assign gray = bin ^ (bin >> 1);

  // Gray code: at most one bit changes per clock, which is why it is safe to cross
  a_gray: assert property (@(posedge fast_clk) disable iff (!rst_n) $onehot0(gray ^ $past(gray)))
    else $error("more than one Gray bit changed");

  initial begin
`ifdef WAVE
    $dumpfile("wave.vcd"); $dumpvars(0, tb);
`endif
    flag = 0;
    #20 rst_n = 1;
    @(posedge fast_clk) flag <= 1;
    $display("[%0t] flag rises in the fast domain", $time);
    @(posedge slow_clk); #1 $display("[%0t] after slow edge 1: meta = %b, flag_sync = %b", $time, u_sync.meta, flag_sync);
    @(posedge slow_clk); #1 $display("[%0t] after slow edge 2: meta = %b, flag_sync = %b", $time, u_sync.meta, flag_sync);
    repeat (8) @(posedge fast_clk) $display("[%0t] bin %b  gray %b", $time, bin, gray);
    $finish;
  end
endmodule
