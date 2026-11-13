// Lecture 3. Try:  ./run 03-randomization/constraints.sv
// Run it a few times with different seeds by editing SEED below.
class Packet;
  rand bit [15:0] b, c, d;
  constraint c_bidir { b < d; c == b; d < 30; c > 25; }
endclass

class Small;
  rand int x;
  constraint allowed_x { x > 0; x < 10; }
endclass

class Large extends Small;
  constraint allowed_x { x > 10; x < 20; }   // same name, so it replaces the parent rule
endclass

module tb;
  localparam int SEED = 1;
  int hist [3];
  int seed = SEED;
  initial begin
    Packet p = new();
    Small  s = new();
    Large  l = new();
    void'($urandom(seed));

    repeat (3) begin
      if (!p.randomize()) $display("randomize failed");
      $display("bidirectional: b = %0d, c = %0d, d = %0d", p.b, p.c, p.d);
    end
    repeat (3) begin
      void'(s.randomize());
      void'(l.randomize());
      $display("small x = %0d, large x = %0d", s.x, l.x);
    end

    repeat (3) begin
      void'(s.randomize() with { x > 5; });
      $display("inline with x > 5: x = %0d", s.x);
    end

    // randcase with weights 1, 4, 5. Expect about 10, 40 and 50 percent.
    repeat (1000) randcase
      1: hist[0]++;
      4: hist[1]++;
      5: hist[2]++;
    endcase
    $display("randcase over 1000 tries: %0d, %0d, %0d", hist[0], hist[1], hist[2]);
    $display("$urandom_range(10, 1) = %0d", $urandom_range(10, 1));
    $finish;
  end
endmodule
