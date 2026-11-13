// Lectures 10 and 14 to 18. Try:  ./run 10-assertions/req_grant.sv
// req is high at cycles 1 and 3, grant only at cycle 7, as in the slides.
// The assertion catches the first request. Then edit the grant cycles and run again.
module tb;
  bit clk, req, grant;
  int cycle;
  always #5 clk = ~clk;
  always @(posedge clk) cycle <= cycle + 1;

  // Every req starts its own check: grant must be high 4 clocks later
  a_req_grant: assert property (@(posedge clk) req |-> ##4 grant)
    else $error("cycle %0d: grant missing 4 clocks after a req", cycle);

  // Same as |-> ##1
  a_next: assert property (@(posedge clk) req |=> !req)
    else $error("cycle %0d: req held high two cycles in a row", cycle);

  // Count how often the antecedent actually fired, so a pass is not vacuous
  c_req: cover property (@(posedge clk) req);

  initial begin
    repeat (12) begin
      @(negedge clk);
      req   = (cycle == 1 || cycle == 3);
      grant = (cycle == 7);
    end
    $finish;
  end
endmodule
