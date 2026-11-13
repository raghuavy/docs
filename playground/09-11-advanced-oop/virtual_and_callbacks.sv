// Lectures 9 to 11. Try:  ./run 09-11-advanced-oop/virtual_and_callbacks.sv
// Virtual methods, $cast, the blueprint pattern and a callback, in one small testbench.
class Transaction;
  rand bit [7:0] src, dst;
  bit [7:0] csm;
  virtual function void calc_csm(); csm = src ^ dst; endfunction
  function void plain_name(); $display("    plain method: Transaction version"); endfunction
  virtual function Transaction copy();
    copy = new();
    copy.src = src; copy.dst = dst; copy.csm = csm;
  endfunction
endclass

class BadTr extends Transaction;
  rand bit bad_csm;
  virtual function void calc_csm();
    super.calc_csm();
    if (bad_csm) csm = ~csm;
  endfunction
  function void plain_name(); $display("    plain method: BadTr version"); endfunction
  virtual function Transaction copy();
    BadTr b = new();
    b.src = src; b.dst = dst; b.csm = csm; b.bad_csm = bad_csm;
    return b;
  endfunction
endclass

virtual class Driver_cbs;
  virtual task pre_tx(ref Transaction tr, ref bit drop); endtask
endclass

class Drop_every_third extends Driver_cbs;
  int n;
  virtual task pre_tx(ref Transaction tr, ref bit drop);
    n++;
    drop = (n % 3 == 0);
  endtask
endclass

class Driver;
  Driver_cbs cbs[$];
  task send(Transaction tr);
    bit drop = 0;
    foreach (cbs[i]) cbs[i].pre_tx(tr, drop);
    if (drop) $display("    dropped by a callback");
    else      $display("    sent src=%h dst=%h csm=%h", tr.src, tr.dst, tr.csm);
  endtask
endclass

module tb;
  initial begin
    Transaction tr, blueprint;
    BadTr bad, b2;
    Driver drv = new();
    Drop_every_third cb = new();

    bad = new();
    bad.src = 8'h0F; bad.dst = 8'hF0; bad.bad_csm = 1;
    tr = bad;                                   // base handle, child object
    $display("calling through a Transaction handle that points at a BadTr:");
    tr.calc_csm();
    $display("    virtual method gave csm = %h (BadTr flipped it)", tr.csm);
    tr.plain_name();

    if ($cast(b2, tr)) $display("$cast worked, b2.bad_csm = %0d", b2.bad_csm);

    $display("blueprint pattern with a BadTr blueprint and a drop callback:");
    drv.cbs.push_back(cb);
    blueprint = bad;
    repeat (4) begin
      void'(blueprint.randomize());
      blueprint.calc_csm();
      drv.send(blueprint.copy());
    end
    $finish;
  end
endmodule
