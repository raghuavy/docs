// Lecture 5. Try:  ./run --wave 05-interfaces/arbiter.sv   then open wave.vcd
// An interface with modports and a clocking block, wired to a tiny arbiter.
interface arb_if (input bit clk);
  logic [1:0] grant, request;
  logic       rst;

  clocking cb @(posedge clk);
    output request;          // the testbench drives this just after the edge
    input  grant;            // and samples this just before the edge
  endclocking

  modport TEST (clocking cb, output rst);
  modport DUT  (input request, rst, clk, output grant);
endinterface

module arb (arb_if.DUT arbif);             // fixed priority, request[0] wins
  always @(posedge arbif.clk or posedge arbif.rst)
    if (arbif.rst)              arbif.grant <= '0;
    else if (arbif.request[0])  arbif.grant <= 2'b01;
    else if (arbif.request[1])  arbif.grant <= 2'b10;
    else                        arbif.grant <= '0;
endmodule

module test (arb_if.TEST arbif);
  initial begin
    arbif.rst = 1;
    repeat (2) @arbif.cb;
    arbif.rst = 0;
    arbif.cb.request <= 2'b10;
    repeat (2) @arbif.cb;
    $display("asked for 10, grant sampled as %b", arbif.cb.grant);
    arbif.cb.request <= 2'b11;
    repeat (2) @arbif.cb;
    $display("asked for 11, grant sampled as %b (request[0] has priority)", arbif.cb.grant);
    $finish;
  end
endmodule

module tb;
  bit clk;
  always #5 clk = ~clk;
  arb_if arbif (clk);
  arb    dut (arbif);
  test   t   (arbif);
`ifdef WAVE
  initial begin $dumpfile("wave.vcd"); $dumpvars(0, tb); end
`endif
endmodule
