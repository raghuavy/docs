// Lecture 19. Runs in the browser. Open Waves after it runs.
// A fast clock and a slow clock, a two flop synchronizer, and a Gray code counter.
// The Gray check here is a plain if, because this simulator has no assert property.
// It uses  d & (d - 1), which clears the lowest 1 bit, so it is zero when at most
// one bit of d is set. That is what $onehot0(d) means.
module sync2 (input logic dst_clk, rst_n, d_async, output logic q_sync);
  logic meta;
  always_ff @(posedge dst_clk or negedge rst_n)
    if (!rst_n) {q_sync, meta} <= '0;
    else        {q_sync, meta} <= {meta, d_async};
endmodule

module tb;
  logic fast_clk = 0, slow_clk = 0, rst_n = 0;
  always #3 fast_clk = ~fast_clk;    // period 6
  always #7 slow_clk = ~slow_clk;    // period 14, unrelated to 6

  logic flag = 0, flag_sync;
  sync2 u_sync (.dst_clk(slow_clk), .rst_n(rst_n), .d_async(flag), .q_sync(flag_sync));

  logic [2:0] bin, gray, gray_past, diff;
  always_ff @(posedge fast_clk or negedge rst_n)
    if (!rst_n) bin <= '0; else bin <= bin + 1;
  assign gray = bin ^ (bin >> 1);

  // Gray code: at most one bit changes per clock, which is why it is safe to cross
  always @(posedge fast_clk) begin
    diff = gray ^ gray_past;          // the bits that changed since the last edge
    if (rst_n && (diff & (diff - 3'd1)) != 0) $display("[%0t] ERROR: more than one Gray bit changed", $time);
    gray_past <= gray;
  end

  initial begin
    $dumpfile("wave.vcd");
    $dumpvars(0, tb);
    #20 rst_n = 1;
    @(posedge fast_clk) flag <= 1;
    $display("[%0t] flag rises in the fast domain", $time);
    @(posedge slow_clk); #1 $display("[%0t] after slow edge 1: meta = %b, flag_sync = %b", $time, u_sync.meta, flag_sync);
    @(posedge slow_clk); #1 $display("[%0t] after slow edge 2: meta = %b, flag_sync = %b", $time, u_sync.meta, flag_sync);
    repeat (8) @(posedge fast_clk) #1 $display("[%0t] bin %b  gray %b", $time, bin, gray);
    $finish;
  end
endmodule
