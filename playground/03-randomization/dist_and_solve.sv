// Lecture 3. Try:  ./run 03-randomization/dist_and_solve.sv
// Counts how often each value comes up, so you can see weights and solve before at work.
class Weighted;
  rand int x;
  // := gives 200 and 201 a weight of 4 each. Change := to :/ and run again.
  constraint c { x dist { 100 := 1, [200:201] := 4 }; }
endclass

class SolveBefore;
  rand bit x;
  rand bit [1:0] y;
  constraint c_xy { (x == 0) -> y == 0; solve x before y; }
endclass

module tb;
  int hist [int];
  int y_zero;
  initial begin
    Weighted w = new();
    SolveBefore s = new();
    repeat (900) begin void'(w.randomize()); hist[w.x]++; end
    foreach (hist[k]) $display("x = %0d came up %0d times out of 900", k, hist[k]);

    repeat (800) begin void'(s.randomize()); if (s.y == 0) y_zero++; end
    $display("y was 0 in %0d of 800 tries. 5/8 of 800 is 500.", y_zero);
    $display("Delete the solve line and run again. With no solve before it drops near 2/5, which is 320.");
    $finish;
  end
endmodule
