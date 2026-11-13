// Lectures 4, 13 and 14. Try:  ./run 04-coverage/bins.sv
// The same samples as the slides, with the coverage printed for each covergroup.
module tb;
  bit [3:0] x, y;

  covergroup auto8;                          // 8 automatic bins, 2 values each
    cpx : coverpoint x { option.auto_bin_max = 8; }
  endgroup

  covergroup named;
    cpx : coverpoint x {
      bins low  = {[0:3]};
      bins mid  = {4, 5, 6, 7};
      bins high = {[8:15]};
    }
  endgroup

  covergroup ignored;
    cpx : coverpoint x { ignore_bins skip = {12, 13, 14, 15}; }
  endgroup

  covergroup crossed;
    cpx  : coverpoint x;
    cpy  : coverpoint y;
    cpxy : cross cpx, cpy;
  endgroup

  auto8   g1 = new();
  named   g2 = new();
  ignored g3 = new();
  crossed g4 = new();

  bit [3:0] xs1 [4] = '{10, 11, 12, 14};
  bit [3:0] xs3 [4] = '{4, 8, 10, 12};
  bit [3:0] xs4 [4] = '{1, 3, 5, 7};
  bit [3:0] ys4 [4] = '{8, 10, 12, 14};

  initial begin
    foreach (xs1[i]) begin x = xs1[i]; g1.sample(); g2.sample(); end
    foreach (xs3[i]) begin x = xs3[i]; g3.sample(); end
    foreach (xs4[i]) begin x = xs4[i]; y = ys4[i]; g4.sample(); end
    $display("auto bins, values 10 11 12 14:   %0.2f percent (slides say 37.5)", g1.get_coverage());
    $display("named bins, same values:         %0.2f percent", g2.get_coverage());
    $display("ignore_bins, values 4 8 10 12:   %0.2f percent (slides say 25)", g3.get_coverage());
    $display("x, y and their cross together:   %0.2f percent", g4.get_coverage());
    $display("  that is the average of 25 (cpx), 25 (cpy) and 1.56 (cross), the three numbers in the slides");
    $finish;
  end
endmodule
