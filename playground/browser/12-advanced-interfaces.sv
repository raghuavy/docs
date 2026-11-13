// Lecture 12, advanced interfaces. Runs in the browser.
// Two copies of the same interface, each wired to its own DUT, and one driver task
// that can drive either. In a class based testbench a virtual interface handle is
// what lets one driver class point at bus0 or bus1. This simulator has no virtual
// interfaces, so the driver picks the bus with an if instead.
interface mem_if (input logic clk);
  logic       we = 0;
  logic [3:0] addr = 0;
  logic [7:0] wdata = 0;

  task automatic write(input logic [3:0] a, input logic [7:0] d);   // a bus functional model
    @(negedge clk);
    we = 1; addr = a; wdata = d;
    @(negedge clk);
    we = 0;
  endtask
endinterface

module mem (input logic clk, we, input logic [3:0] addr, input logic [7:0] wdata);
  logic [7:0] store [16];
  always_ff @(posedge clk) if (we) store[addr] <= wdata;
endmodule

module tb;
  logic clk = 0;
  always #5 clk = ~clk;

  mem_if bus0 (clk), bus1 (clk);
  mem m0 (.clk(clk), .we(bus0.we), .addr(bus0.addr), .wdata(bus0.wdata));
  mem m1 (.clk(clk), .we(bus1.we), .addr(bus1.addr), .wdata(bus1.wdata));

  task automatic drive(int which, logic [3:0] a, logic [7:0] d);
    if (which == 0) bus0.write(a, d);
    else            bus1.write(a, d);
    $display("[%0t] wrote %h to address %0d through bus%0d", $time, d, a, which);
  endtask

  initial begin
    drive(0, 3, 8'hAA);
    drive(1, 3, 8'h55);
    #1 $display("m0[3] = %h, m1[3] = %h: same address, two separate memories", m0.store[3], m1.store[3]);
    $finish;
  end
endmodule
