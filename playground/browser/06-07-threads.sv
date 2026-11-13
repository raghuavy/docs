// Lectures 6 and 7. Runs in the browser.
// The three joins, the shared loop variable bug, an event, and a mailbox.
// This simulator has no built-in mailbox or semaphore, so the mailbox here is a
// queue plus an event, which is how one works inside. The automatic k fix from the
// slides is not supported here, so try that part in the Codespace playground.
module tb;
  int j;                             // one shared variable, like the slide's bug
  int box[$];                        // the mailbox storage
  event put_e;

  task automatic demo(string kind);
    $display("[%0t] %s: start", $time, kind);
    if (kind == "join")
      fork #10 $display("[%0t]   A done", $time); #20 $display("[%0t]   B done", $time); join
    else if (kind == "join_any")
      fork #10 $display("[%0t]   A done", $time); #20 $display("[%0t]   B done", $time); join_any
    else
      fork #10 $display("[%0t]   A done", $time); #20 $display("[%0t]   B done", $time); join_none
    $display("[%0t] %s: the code after the fork runs now", $time, kind);
    wait fork;                       // tidy up before the next demo
  endtask

  task automatic put(int x);         // like mbx.put(x)
    box.push_back(x);
    -> put_e;
  endtask

  task automatic get(output int x);  // like mbx.get(x): wait while it is empty
    while (box.size() == 0) @put_e;
    x = box.pop_front();
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

    $display("producer and consumer through the mailbox:");
    fork
      for (int i = 1; i <= 3; i++) begin
        #5 put(i * 10);
        $display("[%0t]   put %0d", $time, i * 10);
      end
      repeat (3) begin
        int v;
        get(v);
        $display("[%0t]   got %0d", $time, v);
      end
    join
    $finish;
  end
endmodule
