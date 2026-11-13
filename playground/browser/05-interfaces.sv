// Lecture 5. Runs in the browser. Open Waves after it runs.
// An interface bundles the signals, and a task inside it drives them.
// This simulator cannot pass an interface through a port, and has no modport or
// clocking block, so the DUT is wired to the interface signals by name, and the
// task drives on the falling edge, which is the race-free timing a clocking block gives you.
interface arb_if (input logic clk);
  logic [1:0] request = 0;
  logic [1:0] grant;
  logic       rst = 1;

  task automatic ask(input logic [1:0] r);
    @(negedge clk) request = r;      // drive away from the edge the DUT samples on
  endtask
endinterface

module arb (input logic clk, rst, input logic [1:0] request, output logic [1:0] grant);
  always_ff @(posedge clk)
    if (rst)             grant <= 2'b00;
    else if (request[0]) grant <= 2'b01;   // requester 0 has priority
    else if (request[1]) grant <= 2'b10;
    else                 grant <= 2'b00;
endmodule

module tb;
  logic clk = 0;
  always #5 clk = ~clk;

  arb_if bus (clk);
  arb    dut (.clk(clk), .rst(bus.rst), .request(bus.request), .grant(bus.grant));

  initial begin
    $dumpfile("wave.vcd");
    $dumpvars(0, tb);
    @(negedge clk) bus.rst = 0;
    bus.ask(2'b10); @(posedge clk) #1 $display("[%0t] request 10 -> grant %b", $time, bus.grant);
    bus.ask(2'b11); @(posedge clk) #1 $display("[%0t] request 11 -> grant %b", $time, bus.grant);
    bus.ask(2'b00); @(posedge clk) #1 $display("[%0t] request 00 -> grant %b", $time, bus.grant);
    $finish;
  end
endmodule
