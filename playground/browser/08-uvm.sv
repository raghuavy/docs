// Lecture 8. Runs in the browser.
// UVM itself needs a commercial simulator. This shows the two ideas that make a
// UVM test end: phases run in a fixed order, and the run phase only stops when
// every component has dropped its objection.
module tb;
  int objections = 0;

  task automatic raise(string who); objections++; $display("[%0t] %-10s raises an objection  (count %0d)", $time, who, objections); endtask
  task automatic drop(string who);  objections--; $display("[%0t] %-10s drops its objection   (count %0d)", $time, who, objections); endtask

  // Each "component" runs its own run phase as a thread
  task automatic sequence_run();  raise("sequence"); #40 drop("sequence");  endtask
  task automatic driver_run();    forever #10 $display("[%0t] driver     drives an item", $time); endtask
  task automatic scoreboard_run(); raise("scoreboard"); #55 drop("scoreboard"); endtask

  initial begin
    $display("build_phase    top down: test, env, agent, driver");
    $display("connect_phase  bottom up: ports joined to exports");
    $display("run_phase      every component starts at time 0");
    fork
      sequence_run();
      driver_run();                  // never ends on its own, like a real driver
      scoreboard_run();
    join_none
    #1 wait (objections == 0);       // the run phase ends when nobody objects
    disable fork;                    // UVM kills the threads that are still running
    $display("[%0t] all objections dropped, run_phase ends", $time);
    $display("report_phase   print the scoreboard results");
    $finish;
  end
endmodule
