// Lectures 9 to 11. Runs in the browser, with a limit you should know about:
// this simulator does not dispatch virtual methods through a parent handle, so
// polymorphism and callbacks give the wrong answer here. This file sticks to the
// parts that work: extends, super.new and super calls, and a parent handle that
// can see only the parent's fields. Run polymorphism in the Codespace playground.
class Transaction;
  int addr;
  function new(int a);
    addr = a;
  endfunction
  function void show();
    $display("  Transaction addr = %0d", addr);
  endfunction
endclass

class BadTr extends Transaction;
  bit bad_crc;
  function new(int a, bit crc);
    super.new(a);                    // the parent constructor runs first
    bad_crc = crc;
  endfunction
  function void show();
    super.show();                    // reuse the parent's code, then add to it
    $display("  BadTr bad_crc = %0d", bad_crc);
  endfunction
endclass

module tb;
  Transaction tr;
  BadTr       bt;

  initial begin
    bt = new(8, 1);
    $display("bt.show() on the child handle:");
    bt.show();

    tr = bt;                         // a parent handle may point at a child object
    $display("tr.addr through the parent handle = %0d", tr.addr);
    // tr.bad_crc would not compile: the parent handle only knows parent fields.
    // With virtual show(), tr.show() would print both lines. Try it in the Codespace.
    $finish;
  end
endmodule
