// Lecture 12. Runs in the browser. Then type  -D BUG  in Flags and run again.
// The adder, predictor and scoreboard from the UVM example, in plain SystemVerilog.
module full_adder (output sum, output c_out, input a, input b, input c_in);
  assign sum   = a ^ b ^ c_in;
  assign c_out = (a & b) | ((a ^ b) & c_in);
endmodule

module adder (input logic [3:0] a, b, output logic [4:0] sum);
  wire [3:0] c;
  full_adder f0 (sum[0], c[0], a[0], b[0], 1'b0);
  full_adder f1 (sum[1], c[1], a[1], b[1], c[0]);
`ifdef BUG
  full_adder f2 (sum[2], c[2], a[2], b[2], c[0]);   // the planted bug: wrong carry in
`else
  full_adder f2 (sum[2], c[2], a[2], b[2], c[1]);
`endif
  full_adder f3 (sum[3], sum[4], a[3], b[3], c[2]);
endmodule

module tb;
  logic [3:0] a, b;
  logic [4:0] sum, expected;
  int pass_n, fail_n;

  adder dut (.a(a), .b(b), .sum(sum));

  initial begin
    repeat (20) begin
      a = $urandom_range(0, 15);     // sequence and driver
      b = $urandom_range(0, 15);
      #10;                           // let the adder settle
      expected = a + b;              // predictor, 5 bits so the carry is kept
      if (sum === expected)          // scoreboard
        pass_n++;
      else begin
        fail_n++;
        $display("MISMATCH a=%0d b=%0d dut=%0d expected=%0d", a, b, sum, expected);
      end
    end
    $display("%0d matched, %0d mismatched", pass_n, fail_n);
    $finish;
  end
endmodule
