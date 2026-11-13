// Lectures 6 and 7. Try:  ./run 06-07-threads/mailbox.sv
// A producer and a consumer kept in step by a mailbox and an event, plus a one key semaphore.
module tb;
  mailbox #(int) mbx = new();
  event handshake;
  semaphore room = new(1);

  task automatic use_room(int id);
    room.get(1);
    $display("[%0t] thread %0d has the key", $time, id);
    #15;
    room.put(1);
    $display("[%0t] thread %0d gave the key back", $time, id);
  endtask

  initial begin
    fork
      begin : producer
        for (int i = 1; i <= 3; i++) begin
          $display("[%0t] put %0d", $time, i);
          mbx.put(i);
          @handshake;
        end
      end
      begin : consumer
        int v;
        repeat (3) begin
          mbx.get(v);
          #5 $display("[%0t]   got %0d", $time, v);
          ->handshake;
        end
      end
    join
    fork
      use_room(1);
      #5 use_room(2);
    join
    $finish;
  end
endmodule
