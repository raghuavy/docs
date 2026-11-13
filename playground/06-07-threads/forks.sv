// Lectures 6 and 7. Try:  ./run 06-07-threads/forks.sv
// The three joins, the loop variable bug and its fix.
module tb;
  int j;   // one shared variable, like the slide's bug

  task automatic demo(string kind);
    $display("[%0t] %s: start", $time, kind);
    case (kind)
      "join":      fork #10 $display("[%0t]   A done", $time); #20 $display("[%0t]   B done", $time); join
      "join_any":  fork #10 $display("[%0t]   A done", $time); #20 $display("[%0t]   B done", $time); join_any
      "join_none": fork #10 $display("[%0t]   A done", $time); #20 $display("[%0t]   B done", $time); join_none
    endcase
    $display("[%0t] %s: code after the fork runs now", $time, kind);
    wait fork;                      // tidy up before the next demo
  endtask

  initial begin
    demo("join");
    demo("join_any");
    demo("join_none");

    $display("loop where every thread reads the one shared j:");
    for (j = 0; j < 3; j++)
      fork
        $display("  j = %0d", j);
      join_none
    #1;
    $display("loop with automatic k = j:");
    for (j = 0; j < 3; j++)
      fork
        automatic int k = j;
        $display("  k = %0d", k);
      join_none
    #1 $finish;
  end
endmodule
