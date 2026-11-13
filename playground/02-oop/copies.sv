// Lecture 2. Try:  ./run 02-oop/copies.sv
// Handles, static members, super, and the three kinds of copy.
class Inner;
  int y;
endclass

class A;
  static int count = 0;
  int x;
  Inner b = new();
  function new(); count++; endfunction

  function A deep_copy();
    deep_copy = new();
    deep_copy.x = x;
    deep_copy.b.y = b.y;
  endfunction
endclass

class Base;
  virtual function void show(); $display("  Base.show"); endfunction
endclass
class Child extends Base;
  virtual function void show(); $display("  Child.show"); super.show(); endfunction
endclass

module tb;
  A a1, a2;
  Child c;
  initial begin
    a1 = new(); a1.x = 8; a1.b.y = 1;

    a2 = a1;                 // copy the handle
    a2.x = 6;
    $display("handle copy:  a1.x = %0d (one object, two handles)", a1.x);

    a1.x = 8;
    a2 = new a1;             // shallow copy
    a2.x = 6; a2.b.y = 9;
    $display("shallow copy: a1.x = %0d, but a1.b.y = %0d (inner object shared)", a1.x, a1.b.y);

    a1.b.y = 1;
    a2 = a1.deep_copy();     // deep copy
    a2.b.y = 9;
    $display("deep copy:    a1.b.y = %0d (nothing shared)", a1.b.y);

    $display("objects built with new(): A::count = %0d", A::count);

    c = new();
    $display("calling show() on a Child:");
    c.show();
    $finish;
  end
endmodule
