// Lecture 1. Runs in the browser. Change the numbers and run again.
// This simulator keeps X values, so you can see four state versus two state.
module tb;
  logic [3:0] four_state;            // can hold 0, 1, X and Z
  bit   [3:0] two_state;             // only 0 and 1

  typedef struct packed {            // one vector, first field in the top bits
    logic [3:0] a;
    logic [7:0] b;
    logic       c;
  } rec_t;
  rec_t r;

  union packed {                     // one set of bits, read two ways
    logic [3:0]        u;
    logic signed [3:0] s;
  } info;

  typedef enum {IDLE, BUSY, DONE} state_t;
  state_t st;

  int k, n;
  int m [2][3];
  bit [3:0][7:0] word;

  initial begin
    four_state = 'x;
    two_state  = four_state;         // X cannot live in a two state type, it becomes 0
    $display("four state holds %b, two state holds %b", four_state, two_state);

    r.a = 4'hF; r.b = 8'h00; r.c = 1'b1;
    $display("struct as one vector: %b  (width %0d)", r, $bits(r));

    info.u = 4'b1110;
    $display("union bits 1110 read as u = %0d and s = %0d", info.u, info.s);

    k = 5; n = k++;  $display("n = k++  gives n = %0d, k = %0d", n, k);
    k = 5; n = ++k;  $display("n = ++k  gives n = %0d, k = %0d", n, k);

    foreach (m[i, j]) m[i][j] = i * 3 + j;
    foreach (m[i, j]) $display("m[%0d][%0d] = %0d", i, j, m[i][j]);

    st = BUSY;
    $display("enum %s has value %0d", st.name(), st);
    st = st.next();
    $display("st.next() moves it to %s", st.name());

    word = 32'hDEAD_BEEF;
    word[2:1] = 16'h1234;            // a packed array can be sliced by byte
    $display("packed array after a slice write: %h", word);
    $finish;
  end
endmodule
