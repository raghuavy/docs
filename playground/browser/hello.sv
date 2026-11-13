// Runs right here in your browser. Press Run, or Ctrl+Enter.
// A 4 bit counter and a testbench. After it runs, open Waves to see the signals.
module counter (input logic clk, rst, en, output logic [3:0] count);
  always_ff @(posedge clk)
    if (rst)     count <= 0;
    else if (en) count <= count + 1;
endmodule

module tb;
  logic clk = 0, rst = 1, en = 0;
  logic [3:0] count;
  counter dut (.clk(clk), .rst(rst), .en(en), .count(count));

  always #5 clk = ~clk;              // a clock with period 10

  initial begin
    $dumpfile("wave.vcd");           // record every signal for the Waves view
    $dumpvars(0, tb);
    #12 rst = 0;
    #10 en  = 1;
    repeat (5) @(posedge clk) #1 $display("[%0t] count = %0d", $time, count);
    en = 0;
    #20 $display("[%0t] stopped at %0d", $time, count);
    $finish;                         // always end with $finish, or the run is stopped for you
  end
endmodule
