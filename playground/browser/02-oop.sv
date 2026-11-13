// Lecture 2. Runs in the browser.
// Handles, new(), a static counter and a shallow copy.
// This simulator has limited class support: virtual methods called through a
// parent handle run the parent version, and a.b.c paths are not allowed.
// For Lecture 9 style polymorphism, use the Codespace playground.
class Inner;
  int y;
endclass

class Packet;
  static int count = 0;              // one copy shared by every Packet
  int    id;
  Inner  in;                         // a handle to another object
  function new();
    count++;
    id = count;
    in = new();
  endfunction
endclass

module tb;
  Packet p1, p2, p3;
  Inner  t;

  initial begin
    p1 = new();
    p2 = p1;                         // copies the handle, not the object
    p2.id = 42;
    $display("p1.id = %0d after writing p2.id: two handles, one object", p1.id);

    p3 = new();
    $display("built %0d packets with new()", p3.count);

    if (p2 != null) $display("p2 points at an object");
    p2 = null;                       // drop the handle, the object lives on through p1
    $display("p1.id is still %0d", p1.id);

    t = p1.in; t.y = 7;
    p3 = new p1;                     // shallow copy: fields copied, inner handle shared
    t = p3.in; t.y = 9;
    t = p1.in;
    $display("after the shallow copy, p1.in.y = %0d (the inner object is shared)", t.y);
    $display("p3.id = %0d, copied from p1, and count = %0d (new p1 does not call new())", p3.id, p3.count);
    $finish;
  end
endmodule
