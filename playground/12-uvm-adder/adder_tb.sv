// Lecture 12. Try:  ./run 12-uvm-adder/adder_tb.sv
//      then:        ./run -D BUG 12-uvm-adder/adder_tb.sv
// The same adder, predictor and scoreboard idea as the UVM example, in plain SystemVerilog,
// so it runs on the free simulators. Full UVM needs a commercial simulator, see the README.
interface adder_if;
  logic [3:0] a, b;
  logic [4:0] sum;
endinterface

module full_adder (output sum, output c_out, input a, input b, input c_in);
  assign sum   = a ^ b ^ c_in;
  assign c_out = (a & b) | ((a ^ b) & c_in);
endmodule

module adder (adder_if vif);
  wire [3:0] c_out;
  full_adder f0 (vif.sum[0], c_out[0], vif.a[0], vif.b[0], 1'b0);
  full_adder f1 (vif.sum[1], c_out[1], vif.a[1], vif.b[1], c_out[0]);
`ifdef BUG
  full_adder f2 (vif.sum[2], c_out[2], vif.a[2], vif.b[2], c_out[0]);   // the planted bug
`else
  full_adder f2 (vif.sum[2], c_out[2], vif.a[2], vif.b[2], c_out[1]);
`endif
  full_adder f3 (vif.sum[3], vif.sum[4], vif.a[3], vif.b[3], c_out[2]);
endmodule

class adder_item;
  rand logic [3:0] a, b;
  logic [4:0] sum;
endclass

module tb;
  adder_if inf ();
  adder    dut (inf);
  int pass_n, fail_n;
  logic [4:0] expected;

  initial begin
    adder_item item = new();
    repeat (20) begin
      void'(item.randomize());           // sequence and driver
      inf.a = item.a;
      inf.b = item.b;
      #10;                               // let the adder settle
      item.sum = inf.sum;                // monitor
      expected = item.a + item.b;        // predictor, 5 bits wide so the carry is kept
      if (item.sum === expected)         // scoreboard
        pass_n++;
      else begin
        fail_n++;
        $display("MISMATCH a=%0d b=%0d dut=%0d expected=%0d", item.a, item.b, item.sum, expected);
      end
    end
    $display("%0d matched, %0d mismatched", pass_n, fail_n);
    $finish;
  end
endmodule
