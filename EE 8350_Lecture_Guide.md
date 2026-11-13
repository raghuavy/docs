# EE 8350 Lecture Guide, Chapters 1 to 19

Nov 13, 2026 · @Avi

## How to use this guide

Every lecture in this course builds toward one skill. You learn to write a testbench that drives a design with random inputs, checks the answers by itself, and tells you how much of the design you actually exercised.

A few words show up in every lecture, so here they are once.

- DUT means design under test. It is the RTL block you are verifying, like an adder or a FIFO.
- Testbench means all the code around the DUT that creates inputs, watches outputs, and decides pass or fail.
- Stimulus means the input values you drive into the DUT.
- Checker or scoreboard means the code that compares what the DUT did against what it should have done.
- Coverage means a measurement of which situations your tests actually hit.

### How the lectures connect

1. Language foundations. Lecture 1 reviews SystemVerilog data types, Lecture 2 adds classes, and Lecture 5 adds interfaces for connecting the testbench to the DUT.
2. Making inputs and measuring progress. Lecture 3 makes random stimulus, and Lectures 4 and 13 to 14 measure what that stimulus covered.
3. Testbench machinery. Lectures 6 and 7 cover parallel threads and how they talk, Lectures 9 to 11 cover advanced class features, and the Advanced Interfaces lecture connects classes to signals.
4. Methodology. Lecture 8 and the UVM Adder Example show UVM, which is an industry standard way to organize all of the above.
5. Checking behavior over time. Lecture 10, Lectures 14 to 16, and Lectures 16 to 18 cover assertions, which watch signals cycle by cycle.
6. A special topic. Lecture 19 covers clock domain crossing, where signals move between unrelated clocks.

### How each section is laid out

Each lecture section follows the slide order. It starts with the one sentence idea, then walks through the slides in small steps with short code examples. It ends with traps people fall into and practice problems that get harder as you go, with answers right after.

Some slides are pictures of code from the textbook (Spear and Tumbush, SystemVerilog for Verification), so for those the guide writes its own example that shows the same idea.

## Lecture 1. SystemVerilog Review

SystemVerilog is Verilog 2001 plus a large set of features for modeling and verification. It is the third generation of the language, after Verilog 1995 and Verilog 2001. This lecture covers the parts that matter before classes show up.

### Step 1. Running SystemVerilog in VCS

Files use the .sv extension. You compile with the -sverilog flag, then run the simulator executable.

```bash
vcs -sverilog design1.sv tbdesign1.sv
./simv
```

### Step 2. Four state versus two state types

A four state type can hold 0, 1, X (unknown) or Z (high impedance, nothing driving it). A two state type can hold only 0 or 1.

- Four state types are reg, logic, integer, wire, wor and wand. The type logic is identical to reg.
- Two state types are bit, byte, shortint, int and longint.

Two state types simulate faster and use less memory. The catch is that an X from the DUT silently turns into 0 when stored in a two state variable, which can hide a real bug. Use logic for anything connected to the DUT.

### Step 3. The word reg does not mean register

The slide declares two variables as reg. Only one becomes a flip flop, because the hardware depends on the block, not the keyword.

```systemverilog
reg [3:0] sum, q_out;

always_comb sum = a + b;            // combinational adder, no flip flops

always_ff @(posedge clk) q_out <= d;  // real D flip flops
```

### Step 4. Signed and unsigned

The type logic is unsigned by default. The type int is 32 bit signed by default. You can override either one.

```systemverilog
logic signed [7:0] b;   // signed now
int unsigned d;         // 32 bit unsigned
```

### Step 5. Small conveniences

1. Fill every bit of a vector without knowing its width with '0, '1, 'x or 'z, as in `data = '1;`.
2. Put direction and type right in the module header, as in `module simple (output logic a, b, input logic c, d);`.
3. Increment and decrement work like C. With k equal to 5, `n = k++;` gives n equal to 5 and then k becomes 6. With `n = ++k;` k goes up first, so n gets the new value.
4. Compound operators += , -= , \*= and /= are shorthand, so `x += 2;` means `x = x + 2;`.
5. A loop variable can live inside the loop, as in `for (int i = 0; i < 8; i++)`. In Verilog it had to be declared outside.

### Step 6. typedef, struct and union

A typedef gives a type a new name. Declared inside a module, it is visible only there. Declared outside any module, many modules can use it.

A struct groups signals of different types, like a C struct. You read a field with dot notation.

```systemverilog
typedef struct {
  logic a, b, c;
  int d, e, f;
  bit [3:0] g, h;
} my_new_type;

my_new_type v = '{1'b0, 1'b1, 1'b0, 5, 6, 7, 4'hA, 4'hB};
initial $display(v.g);   // prints a
```

To pass a struct through a module port, put the typedef outside the module so both sides know the type.

A packed struct stores all fields as one contiguous vector. The first field sits at the left, the most significant end, and the width is the sum of the field widths.

A union is one piece of storage with more than one way to read it. Packed unions are synthesizable and unpacked ones are not. The slide example reads the same 4 bits as signed or unsigned.

```systemverilog
union packed {
  logic [3:0] u;
  logic signed [3:0] s;
} info;

initial begin
  info.u = 4'b1101;
  $display("signed %0d unsigned %0d", info.s, info.u);  // -3 and 13
end
```

The bit pattern 1101 is 8 + 4 + 1 = 13 read as unsigned. Read as two's complement it is -8 + 4 + 1 = -3.

### Step 7. Unpacked arrays

An unpacked array is a normal array of elements, written with the size after the name. Both declarations below make the same 16 by 8 by 4 array.

```systemverilog
int arr [16][8][4];
int arr2 [0:15][0:7][0:3];

int b [2][4] = '{'{0,0,0,0}, '{1,1,1,1}};  // array literal
int c [8]    = '{8{5}};                    // replication
int d [8]    = '{default: 0};              // every element 0
```

The '{ ... } form is called an array literal. Note the apostrophe in front of the brace.

Loops get easier. $size returns the number of elements, and foreach walks every index for you. For more than one dimension, foreach puts all the indices in one bracket.

```systemverilog
int m [2][3];
foreach (m[i, j]) m[i][j] = i * 3 + j;
```

You can also build arrays of structs, and structs that contain arrays.

### Step 8. Enumerated types

An enum lists the legal names for a variable. By default the names are stored as int values starting at 0, so the first name is 0, the second is 1, and so on. You can override the values.

```systemverilog
typedef enum {IDLE, BUSY, DONE} state_t;        // 0, 1, 2
typedef enum logic [1:0] {RED = 2'b01, GREEN = 2'b10} color_t;
```

### Step 9. always\_comb, always\_ff and always\_latch

In Verilog, one always block could make combinational logic, latches or flops, depending on easy to break rules. SystemVerilog splits it into three keywords that state your intent, so the tools can warn you when the code does not match.

1. always\_comb is for combinational logic. You give no sensitivity list, because the tool infers every input. It also runs once at time 0 so outputs start correct.
2. always\_ff is for edge triggered flops. You do give a sensitivity list, and every signal in it needs posedge or negedge.
3. always\_latch is for level sensitive latches. No sensitivity list, and an if with no else is expected here.

```systemverilog
always_comb
  if (select) mux_out = in1;
  else        mux_out = in0;

always_ff @(posedge clk or negedge rst)
  if (!rst) q <= 0;
  else      q <= d;

always_latch
  if (clk) q_lat <= d;   // transparent while clk is high
```

### Step 10. Functions

A function with several statements no longer needs begin and end, and it uses blocking assignments. You can return a value with a return statement instead of assigning to the function name. A function may have several return statements, and it stops at the first one it reaches.

A void function returns nothing and is called like a task. It still cannot wait on time or events, but it is synthesizable.

```systemverilog
function int max2 (int a, int b);
  if (a > b) return a;
  return b;
endfunction
```

### Step 11. Packed arrays

A packed array has its dimensions before the name. It is stored as one contiguous vector, so `bit [3:0][7:0] word;` is 32 bits holding four bytes. Each range must be written out, like \[3:0\], not just a count.

Only bit level types can be packed, meaning bit, logic, reg, wire, packed structs, packed unions and other packed arrays. You can set the whole thing, one bit, a part select (part of one dimension) or a slice (several whole sub fields).

```systemverilog
bit [3:0][7:0] word;
word = 32'hDEAD_BEEF;   // whole array
word[0] = 8'h00;        // lowest byte
word[3][7] = 1'b0;      // one bit
word[2:1] = 16'h1234;   // a slice of two bytes
```

Copying one packed array to another works like a plain vector copy. Sizes do not have to match, and the usual Verilog rules truncate or zero pad the extra bits.

### Traps to watch for

- Storing a DUT output in int or bit hides X values.
- Packed means dimensions before the name and one vector. Unpacked means dimensions after the name and separate elements.
- foreach over two dimensions is written m\[i, j\], not m\[i\]\[j\].
- An if without else inside always\_comb builds a latch by accident.

### Practice

1. Which of these can hold X, bit, logic, int or integer?
2. With k equal to 5, what are n and k after `n = k++;`? What are they if the line were `n = ++k;` instead?
3. A variable is declared `int unsigned d;`. How many bits wide is it, and can it ever be negative?
4. Write a foreach loop that prints every element of `int m [2][3];`.
5. A union has `logic [3:0] u` and `logic signed [3:0] s`. If u is 4'b1110, what value does s read?
6. A packed struct holds `logic [3:0] a; logic [7:0] b; logic c;` in that order. How wide is it, and which bit range holds a?
7. Someone writes `always_comb if (en) y = x;` with no else. What does synthesis build and why will the tool complain?

### Answers

1. logic and integer. bit and int are two state.
2. With k++, n is 5 and k is 6. With ++k, k becomes 6 first, so n is 6 and k is 6.
3. It is 32 bits and never negative.
4. `foreach (m[i, j]) $display("m[%0d][%0d] = %0d", i, j, m[i][j]);`
5. 1110 is -8 + 4 + 2, so s reads -2.
6. It is 4 + 8 + 1 = 13 bits. The first field sits at the top, so a is bits \[12:9\].
7. It builds a latch, because y must hold its old value when en is 0. always\_comb promised no storage, so the tool warns.

## Lecture 2. OOP in SystemVerilog

A class bundles data together with the code that works on that data. Testbenches use classes because a transaction (one packet, one bus read) is naturally a bundle of fields plus helper methods.

### Step 1. The vocabulary

- A class is the blueprint. Think of it as the plans for a building.
- An object is one thing built from the blueprint. You can build many objects from one class.
- A property (also called an attribute) is a variable inside the class.
- A method is a function or task inside the class.
- A constructor is the method that builds an object. In SystemVerilog it is always called new.
- A handle is a pointer to an object. A variable of class type holds a handle, not the object itself.

### Step 2. Why bother with OOP

1. Encapsulation means hiding data. Members can be public (the default), local (only this class) or protected (this class and its children).
2. Abstraction means hiding complexity behind a simple interface.
3. Inheritance means a child class reuses and extends a parent class.
4. Polymorphism means a parent handle can point to a child object and call the child's version of a method. Lecture 9 to 11 goes deep on this.

### Step 3. Declare, construct and use

The slide class has three properties and two methods.

```systemverilog
class simple;
  bit [15:0] address, data, check;

  function void set_check();
    check = address ^ data;
  endfunction

  function void print();
    $display("address is %h, data is %h, check is %h", address, data, check);
  endfunction
endclass
```

Declaring a handle does not build anything. The handle starts as null, and new() builds the object.

```systemverilog
simple s;          // handle only, s is null
s = new();         // now an object exists
s.address = 16'habcd;
s.data    = 16'h1234;
s.set_check();
s.print();         // address is abcd, data is 1234, check is b9f9

simple t = new();  // declare and construct in one line
```

The dot works like it does for a struct, but it reaches methods too.

### Step 4. Inheritance with extends and super

A child class is made with extends. It automatically has every property and method of its parent. The parent is also called the superclass or base class, and the child is the subclass or derived class.

When the child defines a method with the same name as the parent's, the child's version wins. The keyword super reaches back to the parent's version.

```systemverilog
class base;
  task show();
    $display("BASE task at %0t", $time);
  endtask
endclass

class extd extends base;
  task show();
    $display("EXTD task at %0t", $time);
    super.show();   // also run the parent's version
  endtask
endclass
```

Calling show() on an extd object at time 10 prints the EXTD line, then the BASE line, both at time 10. That matches the slide output.

### Step 5. Static variables

A normal property belongs to one object. A static property belongs to the class, so all objects share one copy. If any object changes it, every object sees the new value.

You can reach a static property through any handle, or through the class name with ::.

```systemverilog
class counter;
  static int count = 0;
  function new(); count++; endfunction
endclass

counter c1 = new(), c2 = new();
initial $display(counter::count);   // 2
```

### Step 6. The keyword this

When a function argument has the same name as a property, the plain name means the argument. Writing this.x means the property instead.

```systemverilog
class demo;
  int x;
  function void set(int x);
    this.x = x;   // property gets the argument
  endfunction
endclass
```

### Step 7. Nested classes and extern methods

A class declared inside another class is a nested class. Only the outer class uses it, which keeps its name from colliding with other code.

The extern keyword lets you declare a method in the class and write its body outside. The class body then fits on one screen, which makes big classes easier to read.

```systemverilog
class ext_demo;
  extern task report();
endclass

task ext_demo::report();
  $display("The externally declared task has been called at time %0t", $time);
endtask
```

### Step 8. Arrays of handles

An array of class type holds handles, not objects. You must call new for each element, usually in a loop. Two elements may point to the same object, and an element you never constructed is null.

```systemverilog
ext_demo arr [5];
initial foreach (arr[i]) arr[i] = new();
```

### Step 9. Three levels of copying

1. Copy the handle. `a2 = a1;` makes two handles to one object. Changing a2.x changes what a1.x reads.
2. Shallow copy. `a2 = new a1;` builds a second object with copies of every property. Any handle inside, though, is copied as a handle, so both objects still share the inner object.
3. Deep copy. You write your own copy method that also builds new inner objects. Nothing is shared afterward.

```systemverilog
class inner; int x; endclass

class outer;
  inner org = new();
  function outer copy();
    copy = new();
    copy.org.x = this.org.x;   // fresh inner object, same value
  endfunction
endclass

outer dup1 = new(), dup2;
initial begin
  dup1.org.x = 8;
  dup2 = dup1.copy();
  dup1.org.x = 6;
  $display(dup1.org.x, dup2.org.x);   // 6 and 8
end
```

The slide output matches this. Both print 8 after the copy, then dup1 changes to 6 while dup2 stays 8.

### Traps to watch for

- Using a handle before new() crashes the simulation with a null handle error.
- `a2 = a1;` does not copy an object. It copies the pointer.
- A shallow copy shares every object nested inside.
- A child method with the same name hides the parent's method unless you call super.

### Practice

1. In one sentence each, what is the difference between a class, an object and a handle?
2. What happens when this runs? `simple s; s.data = 5;`
3. A class has `static int count;` and its new() does count++. After three objects are built, what does count read through the first object?
4. Class A has `int x;`. You run `a1.x = 8; a2 = a1; a2.x = 6;`. What does a1.x read?
5. Same class, but now `a2 = new a1;` before `a2.x = 6;`. What does a1.x read?
6. Class A also holds a handle b to class B, which has `int y;`. After `a2 = new a1; a2.b.y = 9;`, what does a1.b.y read and why?
7. Write a deep copy method for class A from problem 6.

### Answers

1. A class is the type, an object is one built instance of it, and a handle is the variable that points at an object.
2. A runtime null handle error, because no object was built.
3. 3. Every object shares the one static count.
4. 6. Both handles point at one object.
5. 8. new a1 built a separate object.
6. 9. The shallow copy copied the handle b, so both objects share the same B.
7. One version is below.

```systemverilog
function A copy();
  copy = new();
  copy.x = x;
  copy.b = new();
  copy.b.y = b.y;
endfunction
```

## Lecture 3. Randomization

You cannot try every input on a big design, so you let the simulator pick random inputs inside rules you write. Those rules are called constraints, and the approach is called constrained random testing (CRT).

### Step 1. Directed versus constrained random

A directed test applies one input you think will cause trouble. It only finds bugs you already imagined.

A constrained random test applies many random inputs that still obey the protocol. It reaches corners nobody thought of.

A typical CRT setup has three parts.

1. A generator creates a stream of pseudo random inputs and drives the DUT.
2. A reference model predicts the correct output for each input.
3. A comparison checks the DUT output against the prediction.

Pseudo random means the numbers look random but come from a formula, so the same seed repeats the same sequence. That is what lets you rerun a failing test.

### Step 2. What you can randomize

- Input data, alone or bundled into a transaction with constraints.
- Environment configuration. The slide example is a switch chip where you randomize 1 to 4 PCI buses, 1 to 8 devices per bus, and each device's settings.
- Protocol exceptions, meaning deliberately bad stimulus to check the DUT detects errors.
- Delays between transactions.

### Step 3. System functions

1. `$random` returns a 32 bit signed value. Without a seed it produces the same sequence every run. Pass a seed variable to get a different sequence.
2. Because `$random` is signed, `$random % 100` gives values from -99 to 99. That is why the slide output has negative numbers.
3. `$urandom` returns an unsigned 32 bit value from a better generator.
4. `$urandom_range(max, min)` returns an unsigned value from min to max. If you leave out min it defaults to 0.

```systemverilog
int q;
initial repeat (3) begin
  q = $urandom_range(10, 1);   // 1 through 10
  $display("%0d", q);
end
```

### Step 4. randcase

randcase picks one branch at random using weights. Each branch's chance is its weight divided by the total.

```systemverilog
randcase
  1: statement1;   // 1 out of 10
  4: statement2;   // 4 out of 10
  5: statement3;   // 5 out of 10
endcase
```

### Step 5. rand, randc and randomize()

Inside a class you mark a variable rand or randc, then call randomize() on the object.

- rand gives a uniform random value each call. Repeats are allowed.
- randc is cyclic. It walks through every possible value in random order before any value repeats.
- randomize() returns 1 when it found values that satisfy every constraint, and 0 when it could not.

```systemverilog
class example;
  rand integer variable;
endclass

example thing = new();
initial repeat (10)
  if (thing.randomize()) $display("random value is %0d", thing.variable);
  else                   $display("randomize failure");
```

Always check the return value. A failed randomize leaves the old values in place and your test keeps going with stale data.

### Step 6. Constraint blocks

A constraint block is a named set of rules. The solver only returns values that make every rule true.

```systemverilog
class small_class;
  rand integer x;
  constraint allowed_x { x > 0; x < 10; }
endclass
```

### Step 7. Three ways to change constraints

1. Replace by inheritance. A child class that declares a constraint with the same name replaces the parent's version.
2. Add more with an inline constraint. randomize() with { ... } adds rules for just that one call.
3. Turn one off. obj.constraint\_name.constraint\_mode(0) disables that block.

```systemverilog
class large_class extends small_class;
  constraint allowed_x { x > 10; x < 20; }   // replaces the parent rule
endclass

initial begin
  small_class s = new();
  void'(s.randomize() with { x > 5; });     // now x is 6 to 9
end
```

In the slide run, small\_obj gave values like 2 and 5 while large\_obj gave 15 and 13.

### Step 8. inside and enum

The inside operator means the value must be a member of a set. The set can mix single values and ranges.

```systemverilog
rand bit [7:0] len;
constraint c_len { len inside {1, 2, 4, [64:127]}; }
```

A rand variable of enum type only ever takes one of the listed names.

### Step 9. Weighted distributions with dist

dist keeps values random but makes some more likely. The difference between := and :/ only matters for ranges.

- := gives every value in the range that full weight.
- :/ splits the weight evenly across the range.

```systemverilog
x dist { 100 := 1, 200 := 2, 400 := 4 };   // 200 twice as likely as 100
x dist { 100 := 1, [200:201] := 4 };       // 100 gets 1, 200 gets 4, 201 gets 4
x dist { 100 := 1, [200:201] :/ 4 };       // 100 gets 1, 200 gets 2, 201 gets 2
```

### Step 10. Constraints are solved together

Constraints are not executed top to bottom. The solver treats them as one system of equations, so a rule about one variable can limit another.

```systemverilog
rand logic [15:0] b, c, d;
constraint c_bidir {
  b < d;
  c == b;
  d < 30;
  c > 25;
}
```

Since c equals b and c is above 25, b is at least 26. Since b is below d and d is below 30, d lands between 27 and 29. The slide runs show results like b = 26, c = 26, d = 27.

### Step 11. Keep the solver fast

Multiply, divide and modulo are expensive for the solver. Pick bits instead when you can.

```systemverilog
// slow
constraint slow_near_page { addr % 4096 inside {[0:20], [4075:4095]}; }
// fast, same meaning, because 4096 is 2 to the 12th
constraint near_page      { addr[11:0] inside {[0:20], [4075:4095]}; }
```

### Step 12. solve before

solve before changes the probability of each answer, never which answers are legal. Here is the slide example.

```systemverilog
class SolveBefore;
  rand bit x;          // 0 or 1
  rand bit [1:0] y;    // 0 to 3
  constraint c_xy {
    (x == 0) -> y == 0;
    solve x before y;
  }
endclass
```

1. The arrow means implies. If x is 0, y must be 0.
2. With solve x before y, x is picked first with a 1/2 chance each way. When x is 0, y is 0. When x is 1, y is any of 4 values. So y is 0 with probability 1/2 + 1/8 = 5/8.
3. With solve y before x instead, y is picked first, each value 1/4. If y is not 0, x must be 1. If y is 0, x is a coin flip. So x is 0 only 1/4 × 1/2 = 1/8 of the time.
4. With no solve before at all, the solver picks evenly among the 5 legal pairs, so x is 0 with probability 1/5.

### Step 13. Custom distributions

You can shape any distribution in pre\_randomize(), a method that runs automatically just before randomize(). The slide builds a bathtub shape, high at both ends and low in the middle, using `$dist_exponential` and then flipping half the values to the other side. Other built ins include `$dist_normal` and `$dist_poisson`.

### Traps to watch for

- Ignoring the return value of randomize().
- Expecting `$random % N` to be non negative.
- Thinking constraints run in order. They are solved all at once.
- Writing a child constraint with the same name and expecting it to add to the parent. It replaces it.

### Practice

1. What range can `$urandom_range(10)` return?
2. A randcase has weights 2, 3 and 5. What is the chance of each branch?
3. A 2 bit variable is declared randc. You randomize it 4 times. How many distinct values do you see?
4. Find the probabilities for `x dist { 0 := 1, [1:3] := 2 };`.
5. Same as problem 4 but with :/ instead of := on the range.
6. Variables are `rand bit [3:0] a, b;` with `constraint c { a > 1; a < b; b < 4; }`. What are the only legal values?
7. Write one efficient constraint block that makes a 32 bit addr word aligned (a multiple of 4) and between 'h1000 and 'h1FFF.
8. Variables are `rand bit x; rand bit [2:0] y;` with `(x == 1) -> y == 0`. Find P(x = 1) with no solve before, then with solve x before y.

### Answers

1. 0 through 10.
2. 2/10, 3/10 and 5/10.
3. All 4 values, each once, because randc cycles before repeating.
4. The total weight is 1 + 2 + 2 + 2 = 7. So 0 has 1/7, and 1, 2 and 3 each have 2/7.
5. The range shares 2, so each of 1, 2, 3 gets 2/3. The total is 3. So 0 has 1/3 and each other value has 2/9.
6. a must be 2 and b must be 3.
7. `constraint c_addr { addr[1:0] == 0; addr inside {['h1000:'h1FFF]}; }`
8. Legal pairs are x = 0 with 8 y values, plus x = 1 with y = 0, so 9 pairs and P(x = 1) is 1/9. With solve x before y, x is picked first, so P(x = 1) is 1/2.

## Lecture 4. Functional Coverage Basics

Random stimulus raises an obvious question, which is what did it actually test. Functional coverage answers it by recording which values your signals took and reporting the ones never seen.

### Step 1. Cover points and bins

A cover point is one value you watch, such as a 4 bit variable x. A 4 bit value has 16 possible values, and you want to see all of them during simulation.

The possible values are split into bins. A bin holds one value or a range of values. Each time the sampled value falls in a bin, that bin gets a hit.

Coverage is the percent of bins with at least one hit. The goal is 100 percent.

### Step 2. Cover groups

A covergroup collects cover points that are sampled at the same moment. It behaves a lot like a class.

- You define it once and create instances with new. No instance means no data.
- Every cover point inside is sampled together.
- You can define it in a program, a module or a class.

```systemverilog
covergroup grp;
  cpx : coverpoint x;     // cpx is a label for the report
endgroup

grp grp1 = new();
```

If you skip the label, the tool invents a generic name such as coverpoint\_0.

### Step 3. When does sampling happen

There are two ways to trigger a covergroup.

1. Call sample() yourself, as in grp1.sample(), right after new values are ready.
2. Put an event in the definition, as in `covergroup cg @(posedge clk);`, and it samples on every clock edge.

### Step 4. Automatic bins

With no bins written, the tool makes one bin per value, up to a limit called auto\_bin\_max. The default is 64. If the variable has more values than that, each bin covers an equal range.

For a 10 bit value, 1024 values over 64 bins gives 16 values per bin, \[0:15\], \[16:31\] and so on. A bin counts as hit if any one of its values is seen.

The slide example sets auto\_bin\_max to 8 for a 4 bit x, so each bin holds 2 values.

```systemverilog
bit [3:0] x;
bit [3:0] xvals[4] = '{10, 11, 12, 14};

covergroup grp;
  cpx : coverpoint x { option.auto_bin_max = 8; }
endgroup

grp grp1 = new();
initial foreach (xvals[i]) begin
  x = xvals[i];
  grp1.sample();
end
```

1. Bin \[10:11\] is hit twice, by 10 and 11.
2. Bin \[12:13\] is hit once, by 12.
3. Bin \[14:15\] is hit once, by 14.
4. So 3 of 8 bins are covered, which is 37.5 percent.

### Step 5. Explicit bins

You can name bins and list their values yourself with the bins keyword. A default bin catches every value you did not list.

```systemverilog
cpx : coverpoint x {
  bins low  = {[0:3]};
  bins mid  = {4, 5, 6, 7};
  bins high = {[8:15]};
}
```

The slide example has 3 named bins and all 3 get hit, so coverage is 100 percent even though most of the 16 values never appeared. Coverage only judges the bins you defined.

### Step 6. Transition bins

A transition bin checks that a value is followed directly by another value on the next sample. The syntax uses =>.

```systemverilog
bit [3:0] xvals[4] = '{7, 8, 9, 7};

cpx : coverpoint x {
  bins from_7_to_9 = (7 => 9);
  bins from_9_to_7 = (9 => 7);
}
```

The sequence is 7, 8, 9, 7. The bin 7 => 9 is not hit, because 8 came in between. The bin 9 => 7 is hit once. So 1 of 2 bins is covered.

### Step 7. ignore\_bins and illegal\_bins

ignore\_bins removes values you do not care about, such as impossible ones. They get no bins and do not count toward the percentage.

```systemverilog
bit [3:0] xvals[4] = '{4, 8, 10, 12};
cpx : coverpoint x { ignore_bins skip = {12, 13, 14, 15}; }
```

That leaves 12 automatic bins. Values 4, 8 and 10 hit their bins, and 12 is ignored. So 3 of 12 bins are covered, 25 percent.

illegal\_bins marks values that should never happen. Seeing one is reported as a run time error, and on the slide the simulation stops there. Illegal values are also left out of the percentage.

The slide example has values 11, 12, 13, 14 sampled. With 15 marked illegal, 15 values remain and 4 are hit, giving 4/15 = 26.67 percent. If 14 were also illegal, sampling 14 would end the run with an error.

### Step 8. Cross coverage

Cross coverage checks combinations of two cover points sampled at the same time. Give each cover point a label, then cross the labels.

```systemverilog
covergroup grp;
  cpx  : coverpoint x;
  cpy  : coverpoint y;
  cpxy : cross cpx, cpy;
endgroup
```

The slide drives four (x, y) pairs, (1, 8), (3, 10), (5, 12) and (7, 14).

1. cpx has 16 bins and 4 hit, so 25 percent.
2. cpy has 16 bins and 4 hit, so 25 percent.
3. cpxy has 16 × 16 = 256 combination bins and 4 hit, so 1.56 percent.

Crosses grow fast, which is why later lectures teach you to trim them.

### Step 9. Cover group methods

- sample() takes one snapshot. Think of it as taking a photo.
- start() and stop() turn collection on and off. Think of them as turning the camera on and off.

All three act on the whole covergroup, never on one cover point. A common use is calling stop() during reset, when values are meaningless, and start() afterward.

```systemverilog
covergroup DrivingGroup @(posedge clk);
  coverpoint speed;
endgroup

DrivingGroup dg = new();   // active by default
initial begin
  dg.stop();               // ignore the reset phase
  @(negedge rst);
  dg.start();
end
```

### Step 10. What can be covered, and filters

A cover point can be a variable, an expression or a function's return value. The keyword iff adds a filter, and the point is only sampled when the condition is true.

```systemverilog
cpt : coverpoint data iff (OK);
```

### Traps to watch for

- Forgetting new on the covergroup, so no data is ever collected.
- Calling sample() before the variables hold their new values.
- Reading 100 percent as all values seen. It only means all defined bins were hit.
- A transition bin needs back to back samples, not just an eventual arrival.

### Practice

1. A coverpoint is on a 3 bit variable with default settings. How many automatic bins are there?
2. A coverpoint is on an 8 bit variable with auto\_bin\_max set to 16. How many values are in each bin?
3. For problem 2, the samples are 0, 5, 17 and 255. What is the coverage percentage?
4. A transition bin is (3 => 4). The samples are 3, 3, 4, 5. Is it hit?
5. A 4 bit coverpoint uses ignore\_bins for {0, 1} and the samples are 0, 2, 3, 3. What is the coverage?
6. Two 2 bit cover points are crossed. How many cross bins exist, and what is the cross coverage after samples (0,1), (0,1), (2,3)?
7. Write a covergroup that samples on posedge clk only when valid is 1, covering a 4 bit opcode with bins for {0}, {\[1:7\]} and {\[8:15\]}.

### Answers

1. 8, one per value.
2. 256 values over 16 bins is 16 per bin.
3. 0 and 5 are in bin \[0:15\], 17 is in \[16:31\], and 255 is in \[240:255\]. That is 3 of 16 bins, 18.75 percent.
4. Yes. The second 3 is followed directly by 4.
5. 14 bins remain, and 2 and 3 are hit, so 2/14, about 14.3 percent.
6. 4 × 4 = 16 bins. Two distinct pairs were seen, so 2/16 = 12.5 percent.
7. One version is below.

```systemverilog
covergroup op_cg @(posedge clk);
  cp_op : coverpoint opcode iff (valid) {
    bins zero = {0};
    bins low  = {[1:7]};
    bins high = {[8:15]};
  }
endgroup
```

## Lecture 5. The Interface Construct

An interface bundles the wires between the testbench and the DUT into one named object. You change a signal in one place instead of three, and you can attach directions and timing to the bundle. The lecture follows chapters 1 and 4 of Spear and Tumbush.

### Step 1. The layered testbench

The first slides show how a testbench is organized as layers, from raw wires up to the test itself. Each layer only talks to the layers next to it.

1. Signal layer. The DUT and the wires connected to it.
2. Command layer. A driver turns a command like write 5 to address 3 into pin wiggles. A monitor does the reverse, watching pins and rebuilding transactions. Assertions also live here.
3. Functional layer. An agent breaks big transactions into commands. A scoreboard predicts the expected results, and a checker compares them with what the monitor saw.
4. Scenario layer. A generator creates sequences of transactions that mimic real use.
5. Test layer. The test configures everything below it, and functional coverage measures progress.

You can also replace parts of the system with behavioral models, meaning simple code that acts like a block without being the real RTL.

### Step 2. The problem with plain ports

The running example is an arbiter with clk, rst, a 2 bit request and a 2 bit grant. With plain ports, the same signal list appears in the DUT, the testbench and the top module. Adding one signal means editing all three, and a typo in one place breaks the connection.

### Step 3. An interface is a bundle of wires

```systemverilog
interface arb_if (input bit clk);
  logic [1:0] grant, request;
  logic       rst;
endinterface

module arb (arb_if arbif);           // simple fixed priority arbiter
  always @(posedge arbif.clk or posedge arbif.rst)
    if (arbif.rst)                arbif.grant <= '0;
    else if (arbif.request[0])    arbif.grant <= 2'b01;
    else if (arbif.request[1])    arbif.grant <= 2'b10;
    else                          arbif.grant <= '0;
endmodule

module top;
  bit clk;
  always #5 clk = ~clk;
  arb_if arbif (clk);   // one instance of the bundle
  arb    a1 (arbif);    // DUT
  test   t1 (arbif);    // testbench
endmodule
```

Everyone reaches a signal as arbif.name. The clock comes in as an interface port so every user shares it.

If the DUT is an older design with ordinary ports, you can still connect it by pulling the signals out of the interface.

```systemverilog
arb_port a1 (.grant(arbif.grant), .request(arbif.request),
             .rst(arbif.rst), .clk(arbif.clk));
```

### Step 4. Modports give directions

A modport is a named view of the interface that lists which signals are inputs and outputs for one user. It stops the testbench from accidentally driving a DUT output.

```systemverilog
interface arb_if (input bit clk);
  logic [1:0] grant, request;
  logic rst;
  modport TEST    (output request, rst, input grant, clk);
  modport DUT     (input request, rst, clk, output grant);
  modport MONITOR (input request, grant, rst, clk);
endinterface

module arb (arb_if.DUT arbif);   // the DUT uses the DUT view
```

A monitor only watches, so its modport is all inputs.

When every port name matches the signal name in the parent, .\* connects them all at once, as in `arb a1 (.*);`.

### Step 5. Clocking blocks

A clocking block states when synchronous signals are sampled and driven relative to a clock. It is for testbenches and is not synthesizable.

- An interface can hold more than one, one per clock domain.
- It can trigger on one edge, as in @(posedge clk), or both edges, as in @(clk).

```systemverilog
interface arb_if (input bit clk);
  logic [1:0] grant, request;
  logic rst;

  clocking cb @(posedge clk);
    output request;   // driven on the clock edge
    input  grant;     // sampled on the clock edge
  endclocking

  modport TEST (clocking cb, output rst);  // rst stays asynchronous
  modport DUT  (input request, rst, clk, output grant);
endinterface
```

The testbench then talks through cb.

```systemverilog
program automatic test (arb_if.TEST arbif);
  initial begin
    arbif.cb.request <= 2'b01;   // drive at the next posedge
    @arbif.cb;                   // wait for the clocking event
    $display("grant = %b", arbif.cb.grant);
  end
endprogram
```

Why this matters. Without a clocking block, the testbench and the DUT can both act at the exact same clock edge, and the result depends on which runs first. That is a race condition. The clocking block samples inputs just before the edge and drives outputs just after, so the order no longer matters.

### Step 6. The progression in the summary slides

1. Arbiter with plain ports.
2. Arbiter with an interface.
3. Interface plus modports.
4. Interface plus modports plus a clocking block. This is the version the slides call the better one.

### Step 7. The ATM router example

ATM sends data in fixed size cells in time slots. Any user can take any empty slot, so no slot belongs to a particular user.

The example is a router with 4 receive ports and 4 transmit ports that follow the UTOPIA interface standard. In Verilog 1995 style, every port of every channel is listed by hand, which takes several slides of code.

With interfaces, one receive interface and one transmit interface are written once, each with its own clocking block and modports. The DUT then takes eight interface ports instead of dozens of wires.

The testbench slides show only channel 0, and the same code would be copied for channels 1 to 3. The slides point out that virtual interfaces, covered later, remove that copying.

### Traps to watch for

- Driving a signal through the wrong modport. The compiler catches it, which is the point.
- Reading a DUT output directly instead of through cb, which brings the race back.
- Putting an asynchronous signal like rst inside the clocking block.

### Practice

1. Which testbench layer does a driver belong to, and which does a scoreboard belong to?
2. In the TEST modport above, why is rst listed outside the clocking block?
3. Write an interface named bus\_if with a clock port and signals valid, ready and data\[7:0\], plus a master modport and a slave modport.
4. Using the clocking block above, write code that drives request to 2'b10, then waits until grant equals 2'b10.
5. A DUT is declared `module arb (arb_if.TEST arbif);` and assigns arbif.grant. What goes wrong and how do you fix it?
6. Add a clocking block named cb to your bus\_if from problem 3 for the master side, driving valid and data and sampling ready.

### Answers

1. A driver is in the command layer. A scoreboard is in the functional layer.
2. rst is asynchronous, so it should not be tied to the clock edge.
3. One version is below.
4. `arbif.cb.request <= 2'b10; wait (arbif.cb.grant == 2'b10);` or loop on `@arbif.cb` until it matches.
5. TEST gives the DUT the testbench's view, where grant can only be read. Compile fails. Use arb\_if.DUT.
6. Shown in the same block below.

```systemverilog
interface bus_if (input bit clk);
  logic       valid, ready;
  logic [7:0] data;

  clocking cb @(posedge clk);
    output valid, data;
    input  ready;
  endclocking

  modport master (clocking cb);
  modport slave  (input valid, data, clk, output ready);
endinterface
```

## Lectures 6 and 7. Threads and Interprocess Communication

A testbench is many blocks running at the same time, such as a generator, a driver and a monitor. This lecture covers how to start those parallel threads and how they pass data and signals to each other. It follows chapter 7 of Spear and Tumbush.

A thread is one independent flow of execution. Interprocess communication (IPC) is how threads exchange data and wait for each other. Every IPC setup has a producer thread that creates information, a consumer thread that uses it, and a channel between them.

### Step 1. The three kinds of fork

Everything between fork and the join keyword runs in parallel. The join keyword decides when the parent continues.

1. fork ... join waits for all the child threads to finish.
2. fork ... join\_any waits for the first child to finish. The others keep running.
3. fork ... join\_none does not wait at all. The children start when the parent next blocks or ends its time step.

```systemverilog
initial begin
  $display("@%0t start", $time);
  fork
    #10 $display("@%0t A", $time);
    #20 $display("@%0t B", $time);
  join_any
  $display("@%0t after fork", $time);
end
```

With join\_any this prints start at 0, A at 10, after fork at 10, then B at 20. With join, after fork would print at 20. With join\_none, after fork prints at 0.

### Step 2. Testbench blocks are transactors

The generator, agent, driver, monitor, checker and scoreboard are all transactors. A transactor is a loop that takes an object from the block before it, transforms it, and sends it to the block after it. Each one runs in its own thread.

```systemverilog
class driver;
  task run();
    forever begin
      // get a transaction, drive it on the pins
    end
  endtask
endclass

class environment;
  generator gen; driver drv;
  task run();
    fork
      gen.run();
      drv.run();
    join_none
  endtask
endclass
```

Constructing the objects does not start any threads. Calling run() is what spawns them.

Dynamic threads are threads created on the fly, for example one per transaction. How many are running at once depends on how fast each one finishes.

### Step 3. The classic loop bug and automatic

```systemverilog
initial begin
  for (int j = 0; j < 3; j++)
    fork
      $write("%0d ", j);
    join_none
  #0 $display;
end
```

This prints 3 3 3, not 0 1 2. The join\_none threads do not start until the loop has finished, and by then j is 3. All three threads read the same variable.

The fix is an automatic copy made inside the fork. Automatic means the variable gets fresh storage for each thread instead of one shared copy.

```systemverilog
for (int j = 0; j < 3; j++)
  fork
    automatic int k = j;
    $write("%0d ", k);
  join_none
```

The same idea explains why testbench tasks are declared automatic. If a task is called twice at once, static storage would let the second call overwrite the first call's local variables.

### Step 4. Waiting for and stopping threads

- wait fork waits until every child spawned by the current thread is done.
- disable label stops one named block or thread.
- disable fork stops every child spawned by the current thread.

A common pattern is a timeout. Start the real work and a timer with join\_any, then kill whichever is still running.

```systemverilog
fork : timeout_block
  wait (bus.done);
  #1000 $error("timeout");
join_any
disable fork;
```

One caution from the slides. If a task is spawned three times and one copy runs disable on the task name, all three copies die. Tasks inside separately constructed class objects do not have this problem.

### Step 5. Events

An event is a handle to a synchronization object. One thread triggers it and another waits for it.

- ->e triggers the event.
- @e waits for the trigger edge. It only catches triggers that happen after it starts waiting.
- wait (e.triggered) is level sensitive. It also catches a trigger that already happened in the current time step.

In SystemVerilog you can pass an event into a task or a constructor, so objects can share events without global variables.

The slides ask what happens here.

```systemverilog
event eventA;
initial fork
  #5 waitForTrigger(eventA);
  ->eventA;
join

task waitForTrigger (event eventA);
  $display("[%0t] Waiting for EventA", $time);
  wait (eventA.triggered);
  $display("[%0t] EventA has triggered", $time);
endtask
```

The trigger happens at time 0 and the wait starts at time 5. The triggered flag only lasts for the time step of the trigger, so the second message never prints. If the trigger came at time 5 and the wait started at time 0, both lines would print.

A level sensitive wait inside a forever loop with no delay is a trap. The flag stays true for the rest of that time step, so the loop spins forever at zero time. Use @ instead, or add a delay.

### Step 6. Waiting for several things

To wait for all generators to finish, the slides give three options.

1. Spawn them all, then wait fork.
2. Count how many done events have triggered.
3. Count running threads, adding one when a thread starts and subtracting one when it ends.

To continue after only m of n threads, give each thread a count = count + 1 at its end, then wait (count == m) and disable fork.

### Step 7. Semaphores

A semaphore is a bucket of keys that guards a shared resource, such as a bus. A thread must get a key before using the resource and put it back afterward. With one key you get mutual exclusion, or mutex, meaning only one thread at a time.

- `semaphore sem = new(1);` creates it with 1 key.
- get(n) takes n keys and blocks until they are available.
- put(n) returns n keys.
- try\_get(n) takes the keys if available and returns 1, or returns 0 right away without blocking.

```systemverilog
semaphore room = new(1);
task automatic use_room (int id);
  room.get(1);
  $display("[%0t] key retrieved for %0d", $time, id);
  #15;
  room.put(1);
endtask
```

Two cautions. Nothing stops you from putting back more keys than you took. And requests are not served in FIFO order, so a thread asking for 2 keys can be passed by a later thread asking for 1.

### Step 8. Mailboxes

A mailbox is a FIFO channel between a producer and a consumer.

- new() makes an unbounded mailbox, and new(N) limits it to N items.
- put() adds an item and blocks if the mailbox is full.
- get() removes an item and blocks if it is empty.
- peek() copies the front item without removing it.
- try\_put() and try\_get() never block. They return 0 when they cannot act.

A mailbox stores handles, not objects. That leads to a classic bug where the generator builds one object outside its loop and puts the same handle in every time, so every entry points to the last value.

```systemverilog
class generator;
  mailbox #(Transaction) gen2drv;   // parameterized, one type only
  task run(int n);
    repeat (n) begin
      Transaction t = new();        // a new object every time
      assert(t.randomize());
      gen2drv.put(t);
    end
  endtask
endclass
```

The #(Transaction) part makes it a parameterized mailbox. The compiler then rejects any other type, which is good practice.

### Step 9. Keeping producer and consumer in step

With an unbounded mailbox and no synchronization, the producer dumps all its items at once and the consumer removes them one by one later. Three ways to keep them in lockstep follow.

1. Bounded mailbox of size 1 plus peek. The consumer peeks, processes, then calls get. Only then can the producer put the next item. The producer still ends up one item ahead.
2. Mailbox plus a handshake event. The producer puts an item, then waits on the event. The consumer gets the item, processes it, then triggers the event.
3. In option 2, an unbounded mailbox is not really needed, since at most one item is ever waiting.

```systemverilog
mailbox #(int) mbx = new();
event handshake;

initial for (int i = 1; i < 4; i++) begin   // producer
  mbx.put(i);
  @handshake;
end

initial forever begin                         // consumer
  int v;
  mbx.get(v);
  $display("got %0d", v);
  ->handshake;
end
```

### Traps to watch for

- Loop variables read inside join\_none without an automatic copy.
- Waiting with @ on an event that already fired in the same time step.
- One object reused for every mailbox put.
- A level sensitive wait in a zero delay loop.

### Practice

1. A fork has `#5 a();` and `#15 b();`. When does the code after it run for join, join\_any and join\_none?
2. What does the loop in Step 3 print, and what one line fixes it?
3. Thread X runs `->e;` at time 10. Thread Y runs `@e;` starting at time 10 but after X in the same time step. Does Y wake up? What if Y used `wait (e.triggered);`?
4. A semaphore was built with 2 keys. Thread A calls get(2) and holds them. Thread B calls try\_get(1). What does B get back?
5. A generator creates one Transaction before its repeat loop and inside the loop randomizes and puts it 5 times. What does the driver see?
6. Write a fork that waits for whichever comes first, a done event or 500 time units, prints which one won, and kills the other.

### Answers

1. After 15 for join, after 5 for join\_any, and immediately at the current time for join\_none.
2. It prints 3 3 3. Add `automatic int k = j;` inside the fork and print k.
3. No, because @ only sees triggers after it starts waiting. Yes with wait (e.triggered), since the flag is still set in that time step.
4. 0, because no key is free and try\_get does not block.
5. Five handles to the same object, so it tends to see the last randomized values repeated.
6. One version is below.

```systemverilog
fork
  begin @done;  $display("done first");    end
  begin #500;   $display("timeout first"); end
join_any
disable fork;
```

## Lecture 8. UVM

UVM, the Universal Verification Methodology, is a standard library of SystemVerilog base classes from the standards group Accellera. You extend its classes to build your testbench, so every UVM testbench has the same shape and parts can be reused.

The layered testbench from Lecture 5 maps almost one to one onto UVM. UVM just gives each layer a standard class name and standard ways to connect.

### Step 1. The parts and what they do

1. Sequencer. Hands out the stimulus, one transaction at a time.
2. Driver. Turns each transaction into pin wiggles on the DUT inputs.
3. Monitor. Watches the DUT pins and turns activity back into transactions.
4. Agent. A wrapper holding a sequencer, a driver and a monitor for one interface.
5. Scoreboard. Compares actual outputs with expected outputs.
6. Environment. A wrapper holding one or more agents, the scoreboard and anything else reusable.
7. Test. Picks the configuration and the sequences for one particular run.
8. Top. A plain module holding the DUT, the interface, the clock and the call that starts UVM.

&#91;embedded content: UVM testbench structure and data flow\]

Nested boxes show who builds whom. The arrows follow one transaction from the sequence through the driver into the DUT, then back through the monitor to the predictor and scoreboard.

### Step 2. Two family trees of classes

Components are the fixed structure of the testbench. They are built once and live for the whole simulation. The chain is uvm\_object, then uvm\_report\_object, then uvm\_component, and below that uvm\_sequencer, uvm\_driver, uvm\_monitor, uvm\_agent, uvm\_scoreboard, uvm\_env and uvm\_test.

Objects are data that comes and goes. The chain is uvm\_object, then uvm\_transaction, then uvm\_sequence\_item, then uvm\_sequence.

Do not mix up uvm\_sequence and uvm\_sequencer. A sequence is stimulus data. A sequencer is the component that routes it.

### Step 3. The factory and the macros

A factory is an object whose job is creating other objects. In UVM you build things with `type_id::create` instead of new. The factory then lets a test say use my\_special\_driver wherever my\_driver is requested, without editing the environment.

To take part, each class registers with the factory using a macro.

- `` `uvm_component_utils(name) `` registers a component.
- `` `uvm_object_utils(name) `` registers an object such as a transaction or sequence.
- `` `uvm_field_int(name, flags) `` registers a variable so UVM can print, copy and compare it automatically.
- `` `uvm_info(id, message, verbosity) `` prints a message. `` `uvm_error `` and `` `uvm_fatal `` report problems the same way.

### Step 4. Phases

Phases are the stages every component goes through, in the same order, all together.

1. build\_phase constructs child components. It runs top down, so a parent exists before its children.
2. connect\_phase wires components together.
3. run\_phase is where simulation time passes and stimulus is driven. It is the only one of these that is a task, because it consumes time.
4. report\_phase prints results at the end.

### Step 5. A component template

Every component you write follows this pattern. Register, write the constructor, then fill in the phases you need.

```systemverilog
class my_driver extends uvm_driver #(my_txn);
  `uvm_component_utils(my_driver)
  virtual dut_if vif;

  function new(string name, uvm_component parent);
    super.new(name, parent);
  endfunction

  function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    if (!uvm_config_db #(virtual dut_if)::get(this, "", "dut_vi", vif))
      `uvm_fatal("NOVIF", "virtual interface not found")
  endfunction

  task run_phase(uvm_phase phase);
    forever begin
      seq_item_port.get_next_item(req);   // wait for a transaction
      @(posedge vif.clk);
      vif.a <= req.a;                      // pin wiggles
      vif.b <= req.b;
      seq_item_port.item_done();           // tell the sequencer we are done
    end
  endtask
endclass
```

The driver never reads DUT outputs, but it must wait long enough for them to appear before sending the next transaction.

### Step 6. Transactions and sequences

A transaction is one high level operation, such as an address and data plus the intent to read. Thinking in transactions keeps tests away from pin level detail.

```systemverilog
class my_txn extends uvm_sequence_item;
  `uvm_object_utils(my_txn)
  rand bit [3:0] a, b;
  function new(string name = "my_txn"); super.new(name); endfunction
endclass
```

A sequence is an ordered set of transactions. Its body() task makes them and sends them through the sequencer to the driver.

```systemverilog
class my_seq extends uvm_sequence #(my_txn);
  `uvm_object_utils(my_seq)
  function new(string name = "my_seq"); super.new(name); endfunction

  task body();
    repeat (10) begin
      req = my_txn::type_id::create("req");
      start_item(req);                     // wait for the driver to be ready
      if (!req.randomize()) `uvm_error("RAND", "randomize failed")
      finish_item(req);                    // send it and wait for item_done
    end
  endtask
endclass
```

Sequences can start other sequences, which gives layered stimulus, a sequence of sequences.

### Step 7. Agent, environment and test

- The agent builds its sequencer, driver and monitor, then connects driver.seq\_item\_port to sequencer.seq\_item\_export. It needs build and connect phases and no run phase.
- The environment builds the agent and the scoreboard and connects the monitor to the scoreboard. Again no run phase.
- The test builds the environment and, in its run phase, starts a sequence on the agent's sequencer.

```systemverilog
class my_test extends uvm_test;
  `uvm_component_utils(my_test)
  my_env env;

  function new(string name, uvm_component parent); super.new(name, parent); endfunction

  function void build_phase(uvm_phase phase);
    env = my_env::type_id::create("env", this);
  endfunction

  task run_phase(uvm_phase phase);
    my_seq seq = my_seq::type_id::create("seq");
    phase.raise_objection(this);
    seq.start(env.agent.sequencer);
    phase.drop_objection(this);
  endtask
endclass
```

The environment is the reusable testbench. Each test is one way of configuring and exercising it, with different sequences or settings, until coverage is reached.

### Step 8. Objections, or how UVM knows when to stop

No single component decides when simulation ends. Any component that is still busy raises an objection, and the run phase ends when every objection has been dropped.

- Raise without a matching drop and the simulation hangs.
- Raise nothing at all and the run phase ends at time 0, so nothing gets tested.
- Drain time adds a delay after the last drop so final outputs can settle. It is usually set in the test or environment.

### Step 9. The top module and the configuration database

A virtual interface is a handle that points at a real interface instance. Classes cannot hold real wires, so they hold this handle instead.

The configuration database stores (name, value) pairs that components look up by path. The top module stores the interface there, and the test or driver fetches it.

```systemverilog
module top;
  import uvm_pkg::*;            // ::* imports everything in the package
  `include "uvm_macros.svh"

  bit clk;
  always #5 clk = ~clk;

  dut_if dut_if_instance (clk);
  my_dut dut (.a(dut_if_instance.a), .b(dut_if_instance.b), .y(dut_if_instance.y));

  initial begin
    uvm_config_db #(virtual dut_if)::set(null, "uvm_test_top", "dut_vi", dut_if_instance);
    run_test("my_test");
  end
endmodule
```

The four arguments of set are these.

1. The calling component, null when called from a module.
2. The path of components allowed to see it. Here only the test, whose instance name is always uvm\_test\_top. A \* wildcard widens it.
3. The nickname, "dut\_vi".
4. The value, here the interface instance.

The test calls get with this and an empty path, which means look at my own level. It can then pass the handle down, for example with `uvm_config_db #(virtual dut_if)::set(this, "*", "dut_vi", vif);` so every component under the test can find it. The slides pass it inside a config object instead, which works the same way.

Inside the driver, a signal y in the interface is reached as vif.y.

### Step 10. TLM connections

Transaction level modeling (TLM) means components pass whole transaction objects to each other instead of wires.

1. A port, drawn as a small square, says which methods a component will call.
2. An export, drawn as a small circle, supplies the code for those methods.
3. You connect a port to an export. Blocking methods are put and get, and non blocking ones are try\_put and try\_get.
4. An analysis port, drawn as a diamond, has one method, write(), a void function that never blocks. It broadcasts to any number of listeners, which is why monitors use it to feed scoreboards and coverage collectors.
5. A listener is often extended from uvm\_subscriber, which provides an analysis\_export and asks you to write the write() function.

### Traps to watch for

- Calling new instead of type\_id::create, which quietly disables factory overrides.
- Forgetting the registration macro, so the factory cannot find the class.
- Forgetting to raise an objection, so the test ends at time 0.
- A config\_db path or nickname that does not match between set and get.

### Practice

1. Sort these into components and objects. Driver, sequence, transaction, environment, scoreboard.
2. Which of build\_phase, connect\_phase, run\_phase and report\_phase is a task, and why?
3. Why does UVM code use type\_id::create instead of new?
4. A test starts a sequence in run\_phase but never raises an objection. What happens?
5. Top calls `uvm_config_db #(virtual dut_if)::set(null, "uvm_test_top", "dut_vi", inst);`. The driver at uvm\_test\_top.env.agent.drv calls get(this, "", "dut\_vi", vif). Does the driver find it? What one line in the test fixes it?
6. Why does a monitor use an analysis port instead of a put port?
7. Write the agent's connect\_phase that links the driver to the sequencer.

### Answers

1. Components are the driver, environment and scoreboard. Objects are the sequence and transaction.
2. run\_phase, because it is the only one that consumes simulation time.
3. So the factory can substitute a different type through an override without editing the code that builds it.
4. The run phase ends right away at time 0 and the sequence barely runs.
5. No, the setting is only visible at uvm\_test\_top. In the test, get the handle, then `uvm_config_db #(virtual dut_if)::set(this, "*", "dut_vi", vif);`.
6. write() never blocks and can feed many listeners at once, so the monitor never stalls on a slow subscriber.
7. One version is below.

```systemverilog
function void connect_phase(uvm_phase phase);
  drv.seq_item_port.connect(sqr.seq_item_export);
endfunction
```

## Lectures 9 to 11. Advanced OOP and Testbench Guidelines

This lecture shows how inheritance and virtual methods let one testbench run many different tests without being edited. Tests change behavior by swapping in extended classes. It follows chapter 8 of Spear and Tumbush.

One new word first. A method's prototype is its first line, giving the name, arguments and return type.

### Step 1. The running example

The slides use a small testbench. The test controls a generator, the generator sends random transactions to a driver through a mailbox, and the driver wiggles the DUT pins.

The base Transaction class holds source and destination addresses, 8 data words and a checksum. It has a method to compute the checksum and one to display. Both are declared virtual, which allows a child class to redefine them.

```systemverilog
class Transaction;
  rand bit [31:0] src, dst, data[8];
  bit [31:0] csm;

  virtual function void calc_csm();
    csm = src ^ dst ^ data.xor();
  endfunction

  virtual function void display(string prefix = "");
    $display("%sTr src=%h dst=%h csm=%h", prefix, src, dst, csm);
  endfunction
endclass
```

### Step 2. An extended class for error injection

BadTr extends Transaction to inject errors. It adds one property, bad\_csm, and redefines both methods. super still reaches the parent's versions.

```systemverilog
class BadTr extends Transaction;
  rand bit bad_csm;

  virtual function void calc_csm();
    super.calc_csm();          // compute the good checksum
    if (bad_csm) csm = ~csm;   // then corrupt it on purpose
  endfunction

  virtual function void display(string prefix = "");
    $write("%sBadTr bad_csm=%b ", prefix, bad_csm);
    super.display();
  endfunction
endclass
```

If the parent's new() takes arguments, the child's new() must call super.new(...) with them on its first line.

### Step 3. Base handles, extended objects, and virtual methods

The driver declares `Transaction tr;` and pulls from the mailbox. The object it gets might really be a BadTr.

1. A base handle can point at an extended object. No conversion is needed.
2. Through that base handle you can only name things the base class has, such as src, dst and csm. You cannot write tr.bad\_csm.
3. When you call a virtual method like tr.calc\_csm(), the object's real type decides which version runs. A BadTr object runs BadTr::calc\_csm().
4. Without virtual, the handle's type decides, so Transaction::calc\_csm() would run even for a BadTr. That is the key difference.

This is polymorphism, one call that behaves differently depending on the object behind it.

Two rules come with it. Every redefinition of a virtual method must have the same signature, meaning the same number and types of arguments and the same return type. And new() can never be virtual, because before it runs there is no object whose type could be checked.

### Step 4. The blueprint pattern

The first generator builds a fresh Transaction inside its loop, which avoids the shared handle bug from Lecture 6. But it can never make a BadTr, and it randomizes right after new(), so a test cannot change its constraints.

A design pattern is a reusable programming technique. The blueprint pattern fixes both problems.

1. The generator holds one object called the blueprint, built once in its constructor.
2. Each loop iteration randomizes the blueprint, then puts a copy in the mailbox.
3. The generator only knows how to copy. If the test swaps in a different kind of blueprint, copies of that kind go out instead.

```systemverilog
class Generator;
  mailbox #(Transaction) gen2drv;
  Transaction blueprint;

  function new(mailbox #(Transaction) gen2drv);
    this.gen2drv = gen2drv;
    blueprint = new();                 // default blueprint
  endfunction

  task run(int num_tr = 10);
    repeat (num_tr) begin
      assert(blueprint.randomize());
      gen2drv.put(blueprint.copy());   // send a copy, never the original
    end
  endtask
endclass
```

Declaration, construction and randomization are now three separate steps, and the test can step in between them.

### Step 5. Build, run, wrap up

The environment class has three phases, which UVM later formalizes.

1. build() is a function that constructs everything. No time passes.
2. run() is a task where the simulation actually happens.
3. wrap\_up() is a task that finishes and reports.

To inject errors, the test swaps the blueprint between build and run. The begin/end block just limits where the name bad is visible.

```systemverilog
program automatic test;
  Environment env;
  initial begin
    env = new();
    env.build();
    begin
      BadTr bad = new();
      env.gen.blueprint = bad;   // replace the blueprint
    end
    env.run();
    env.wrap_up();
  end
endprogram
```

The same trick changes constraints. A class Nearby extends Transaction with `constraint c_nearby { dst inside {[src-100 : src+100]}; }`, and the test makes a Nearby object the blueprint.

### Step 6. Upcasting, downcasting and $cast

Upcasting means copying an extended handle into a base handle. It is always legal, as in `tr = bad;`.

Downcasting means going the other way, from a base handle to an extended handle. A plain assignment `bad = tr;` is a compile error, because the object behind tr might be missing bad\_csm.

`$cast` checks the real object type at run time.

```systemverilog
Transaction tr;
BadTr       bad, b2;

bad = new();
tr  = bad;                  // upcast, fine

$cast(b2, tr);              // used as a task, run time error if it fails
if ($cast(b2, tr))          // used as a function, returns 1 or 0
  $display(b2.bad_csm);
else
  $display("tr is not a BadTr");
```

### Step 7. A copy method that works with inheritance

The copy method must keep the same signature in every class, so even BadTr::copy returns a Transaction handle. An optional argument lets the caller supply an existing object to copy into.

```systemverilog
// in Transaction
virtual function Transaction copy(Transaction to = null);
  if (to == null) copy = new();
  else            copy = to;
  copy.src = src; copy.dst = dst; copy.data = data; copy.csm = csm;
endfunction

// in BadTr
virtual function Transaction copy(Transaction to = null);
  BadTr bad;
  if (to == null) bad = new();
  else            $cast(bad, to);
  void'(super.copy(bad));   // parent copies the shared fields
  bad.bad_csm = bad_csm;
  return bad;
endfunction
```

A handle that has never been pointed at an object holds null, and you can test for it with `if (h == null)`.

### Step 8. Abstract classes

An abstract class is a base class you are never meant to construct. You mark it with virtual class. Its pure virtual methods have a prototype and no body.

```systemverilog
virtual class BaseTr;
  static int count;       // one counter shared by all
  int id;
  pure virtual function bit compare(BaseTr to);
  pure virtual function BaseTr copy(BaseTr to = null);
  pure virtual function void display(string prefix = "");
endclass
```

You can declare BaseTr handles but not BaseTr objects. Any class extending it must give a body for every pure virtual method.

### Step 9. Callbacks

The goal is one environment for every test, where a test can add behavior like dropping, delaying or corrupting a transaction without touching the driver's code.

A callback is a hook. The driver calls an empty virtual method at key points, and a test fills that method in through an extended class.

```systemverilog
virtual class Driver_cbs;                 // default hooks do nothing
  virtual task pre_tx (ref Transaction tr, ref bit drop); endtask
  virtual task post_tx(ref Transaction tr);               endtask
endclass

class Driver;
  Driver_cbs cbs[$];                      // a queue, zero or more callbacks
  task run();
    Transaction tr; bit drop;
    forever begin
      drop = 0;
      gen2drv.get(tr);
      foreach (cbs[i]) cbs[i].pre_tx(tr, drop);
      if (!drop) transmit(tr);
      foreach (cbs[i]) cbs[i].post_tx(tr);
    end
  endtask
endclass

class Driver_cbs_drop extends Driver_cbs;  // drop 1 percent
  virtual task pre_tx(ref Transaction tr, ref bit drop);
    drop = ($urandom_range(0, 99) == 0);
  endtask
endclass
```

The test adds it between build and run with `env.drv.cbs.push_back(dcd);`, where dcd is a Driver\_cbs\_drop object. The driver never learns what the callback does.

### Step 10. Scoreboards, often fed by callbacks

A scoreboard has three parts.

1. A transform function that computes the expected output for an input.
2. Storage for expected values, here a queue.
3. A compare method. When the DUT produces a result, it searches the queue. No match is an error, one match is the good case and gets removed, and several matches need a closer look.

The VMM methodology (an older methodology before UVM) recommends feeding the scoreboard from a driver callback and functional coverage from a monitor callback. Scoreboards and coverage are passive listeners, so callbacks avoid wiring a separate mailbox from every block that has data for them.

### Step 11. Parameterized classes

A parameterized class takes a type as a parameter, like a C++ template. You give a default type, and anyone can specialize it with another type.

```systemverilog
class Stack #(type T = int);
  local T stack[100];   // local means only this class can touch it
  local int idx;
  function void push(T i); stack[idx++] = i; endfunction
  function T pop();        return stack[--idx]; endfunction
endclass

Stack           int_stack;    // default, holds int
Stack #(real)   real_stack;   // specialized to real
```

The slides apply this to the generator, `class Generator #(type T = BaseTr);`, so a test can declare `Generator #(Transaction) gen;` and reuse the same code for a different transaction type.

### Traps to watch for

- Forgetting virtual on a method, so the handle type decides which version runs.
- Downcasting with plain assignment instead of $cast.
- A redefined virtual method with a different signature.
- Putting the blueprint itself in the mailbox instead of a copy.

### Practice

1. You have `BadTr b = new();`. Is `Transaction t = b;` legal? Is `BadTr b2 = t;` legal?
2. calc\_csm is not virtual. tr is a Transaction handle pointing to a BadTr object. Which calc\_csm runs on tr.calc\_csm()?
3. Same as problem 2 but calc\_csm is virtual.
4. Through a Transaction handle that points to a BadTr, can you read bad\_csm? How would you read it?
5. Why can't new() be virtual?
6. A generator puts the blueprint itself into the mailbox 10 times. What goes wrong?
7. Write a callback class that delays each transaction by a random 0 to 10 time units before it is sent.

### Answers

1. The first direction, extended into base, is legal. The second, base into extended, is a compile error. Use $cast.
2. Transaction::calc\_csm, because without virtual the handle type decides.
3. BadTr::calc\_csm, because virtual makes the object type decide.
4. Not directly. Use `if ($cast(b, tr)) $display(b.bad_csm);`.
5. A virtual call looks up the object's type, and before new() finishes there is no object.
6. All 10 entries are the same object, so the driver sees the last randomized values repeated.
7. One version is below.

```systemverilog
class Driver_cbs_delay extends Driver_cbs;
  virtual task pre_tx(ref Transaction tr, ref bit drop);
    #($urandom_range(0, 10));
  endtask
endclass
```

## Lecture 10. Assertions Basics

An assertion is a statement of something that must always be true about the design. If it ever turns out false, the simulator reports an error at that exact time and place. SVA, SystemVerilog Assertions, is the part of the language for writing them. The reference is Cerny et al., SVA, The Power of Assertions in SystemVerilog.

### Step 1. Three ways to verify

1. Directed tests apply inputs you chose by hand.
2. Constrained random verification lets the simulator choose inputs inside rules.
3. Assertions watch the design all the time and complain the moment a rule breaks.

They work together. Random tests create activity, and assertions check that activity everywhere.

### Step 2. What an assertion says

A property is a rule about signal values, either at one moment or across several clock cycles. Two examples from the slides follow.

- Two signals should never both be 1 at the same time.
- A signal should be 1 three clock cycles after another signal was 1.

The simulator checks each assertion every clock cycle. On a failure it prints the time, the assertion's name and the values involved.

```systemverilog
a1: assert property (@(posedge clk) a != b);
```

Read it as, at every rising clock edge, a must differ from b. The a1 in front is a label that appears in error messages.

### Step 3. Why not just write if statements

Take the rule that grant must be high exactly 4 cycles after req goes high. The Verilog way uses a counter.

```systemverilog
always @(posedge clk) begin
  if (req) count <= 1;
  else if (count != 0) count <= count + 1;
  if (count == 4 && !grant) $error("no grant");
end
```

This breaks when a second req arrives before the first grant. The counter restarts at 1, so the first request is silently forgotten and its missing grant is never reported.

The SVA version handles overlapping requests correctly, because each req starts its own independent check.

```systemverilog
assert property (@(posedge clk) req |-> ##4 grant);
```

Two new symbols appear here.

1. |-> means implies. If the left side is true at this clock edge, the right side must hold, starting at the same edge.
2. \##4 means wait 4 clock cycles.

So it reads, whenever req is high, grant must be high 4 cycles later.

### Step 4. Assertions are formal

SVA is a formal specification language. Unlike an English spec, it has exactly one meaning, so cases like overlapping requests cannot be left vague.

The same assertion can be checked two ways. A simulator checks it on whatever stimulus you run. A formal tool proves it mathematically for every possible input.

### Step 5. Where assertions go

- At interfaces. They describe the legal behavior of signals between blocks, such as bus protocols, memory reads and writes, data transformations and arbitration. This is black box verification, since it ignores how the blocks work inside.
- Inside a design module. The designer writes them next to the RTL, checking internal signals. This is white box verification.

The slide example is an 8 bit register with asynchronous reset and synchronous set that rotates left by one bit each clock. It has two assertions written inside module and endmodule.

```systemverilog
module rotreg (input logic clk, rst, set, output logic [7:0] q);
  always_ff @(posedge clk or posedge rst)
    if (rst)      q <= '0;
    else if (set) q <= '1;
    else          q <= {q[6:0], q[7]};

  check_shift: assert property (@(posedge clk) disable iff (rst)
                 !set |=> q == {$past(q[6:0]), $past(q[7])});

  check_rst: assert final (!rst || q == '0);
endmodule
```

This is a sketch of the idea rather than a copy of the slide. Three new pieces appear.

1. `$past(x)` returns the value x had on the previous clock edge.
2. disable iff (rst) switches the check off while reset is active, because the rule only applies during normal operation.
3. assert final marks a deferred assertion, which waits until values settle in the time step before checking. Later lectures explain it.

The |=> operator is like |-> but starts the right side one clock later.

### Step 6. Immediate assertions

Everything so far is a concurrent assertion, which runs on a clock and can span many cycles. An immediate assertion is just a check inside procedural code, run when that line executes, like an if statement.

```systemverilog
always @(posedge clk)
  assert (!(gnt && !req))
    else $error("Grant asserted without a request at %0t", $time);
```

### Step 7. Why assertions pay off

A scoreboard checks outputs at the edge of the DUT. By then a bad value may have passed through several pipeline stages, and you have to trace backward to find where it started.

An assertion inside the RTL fires at the exact block and cycle where the rule broke. In the slide's 4 stage pipeline example, a control signal wrongly cleared in stage 2 shows up at the output two cycles later. An assertion on that stage 2 signal points straight at the cause.

### Traps to watch for

- Writing the counter style check by hand and missing overlapping cases.
- Forgetting disable iff, so every reset produces false failures.
- Mixing up |-> (same cycle) and |=> (next cycle).

### Practice

1. Write an assertion that a and b are never both 1 at a rising clock edge.
2. In plain words, what does `req |-> ##2 ack` require?
3. Is `req |=> ack` the same as `req |-> ##1 ack`?
4. req is high at cycles 1 and 3. Using `req |-> ##4 grant`, at which cycles must grant be high?
5. In problem 4, the counter version from Step 3 is used instead. grant is high at cycle 7 only. What does the counter report, and what does the assertion report?
6. Write an assertion that whenever en is high, the 4 bit counter cnt equals its previous value plus 1 on the next cycle, disabled during rst.

### Answers

1. `assert property (@(posedge clk) !(a && b));`
2. Whenever req is high at a clock edge, ack must be high 2 edges later.
3. Yes, they mean the same thing.
4. Cycles 5 and 7.
5. The counter restarts at cycle 3 and checks only cycle 7, which passes, so it reports nothing. The assertion fails for the request at cycle 1, since grant was low at cycle 5.
6. `assert property (@(posedge clk) disable iff (rst) en |=> cnt == $past(cnt) + 4'd1);`

## Lecture 12. UVM Adder Example

This lecture fills in the Lecture 8 templates with a complete, working UVM testbench for a 4 bit adder. Every piece is short, so it is the best place to see how the parts fit and where data flows.

### Step 1. Lab 2 recap

Lab 2 was the scaffolding. It had a top, a package, a test and two components whose phases mostly printed messages. It showed the phase order without doing any real checking. This lecture puts real content into each placeholder.

### Step 2. The DUT and its interface

```systemverilog
interface adder_if;
  logic [3:0] a;
  logic [3:0] b;
  logic [4:0] sum;     // 5 bits, so the carry out fits
endinterface
```

The adder is the ripple carry adder from Lecture 1. Four full adders are chained, each carry out feeding the next carry in, and the last carry out becomes sum\[4\].

```systemverilog
module full_adder (output sum, output c_out, input a, input b, input c_in);
  assign sum   = a ^ b ^ c_in;
  assign c_out = (a & b) | ((a ^ b) & c_in);
endmodule

module adder (adder_if vif);
  wire [3:0] c_out;
  full_adder f_ad0 (vif.sum[0], c_out[0], vif.a[0], vif.b[0], 1'b0);
  full_adder f_ad1 (vif.sum[1], c_out[1], vif.a[1], vif.b[1], c_out[0]);
  full_adder f_ad2 (vif.sum[2], c_out[2], vif.a[2], vif.b[2], c_out[1]);
  full_adder f_ad3 (vif.sum[3], vif.sum[4], vif.a[3], vif.b[3], c_out[2]);
endmodule
```

### Step 3. The sequence item

The transaction holds two random inputs and the result.

```systemverilog
class adder_item extends uvm_sequence_item;
  `uvm_object_utils(adder_item)
  rand logic [3:0] a;
  rand logic [3:0] b;
  logic [4:0] sum;

  function new(string name = "adder_item"); super.new(name); endfunction

  virtual function void do_copy(uvm_object rhs);
    adder_item rhs_;
    if (!$cast(rhs_, rhs)) begin
      `uvm_error("ITEM_COPY", "Cast failed in do_copy")
      return;
    end
    super.do_copy(rhs);
    this.a = rhs_.a; this.b = rhs_.b; this.sum = rhs_.sum;
  endfunction

  virtual function string convert2string();
    return $sformatf("A=%0d, B=%0d | Sum=%0d", a, b, sum);
  endfunction
endclass
```

1. do\_copy is the hook UVM calls when anyone runs copy() or clone() on this item. It receives a uvm\_object handle, so it uses $cast to get an adder\_item handle, the downcast from Lectures 9 to 11.
2. convert2string returns a readable string. `$sformatf` formats text like $display but returns it instead of printing.

### Step 4. The sequence

The sequence makes 10 random items. start\_item waits until the driver is ready, and finish\_item hands the item over and waits for item\_done.

```systemverilog
class adder_sequence extends uvm_sequence #(adder_item);
  `uvm_object_utils(adder_sequence)
  function new(string name = "adder_sequence"); super.new(name); endfunction

  virtual task body();
    adder_item item;
    repeat (10) begin
      item = adder_item::type_id::create("item");
      start_item(item);
      if (!item.randomize()) `uvm_error("SEQ", "Randomization failed!")
      finish_item(item);
    end
  endtask
endclass
```

The sequencer itself needs no custom code. The agent simply uses `uvm_sequencer #(adder_item)`.

### Step 5. The driver

The driver gets the virtual interface from the config database, then loops. It takes an item, puts a and b on the pins, waits 10 time units for the combinational adder to settle, and reports done.

```systemverilog
virtual task run_phase(uvm_phase phase);
  adder_item item;
  forever begin
    seq_item_port.get_next_item(item);
    vif.a = item.a;
    vif.b = item.b;
    #10;                           // time for the math and the sampling
    seq_item_port.item_done();
  end
endtask
```

There is no clock here because the adder is purely combinational, so the testbench paces itself with delays.

### Step 6. The monitor

The monitor also waits 10 time units per item, then builds a fresh item from whatever is on the pins and broadcasts it through an analysis port.

```systemverilog
uvm_analysis_port #(adder_item) item_collected_port;   // built in new()

virtual task run_phase(uvm_phase phase);
  adder_item item;
  forever begin
    #10;
    item = adder_item::type_id::create("item");
    item.a   = vif.a;
    item.b   = vif.b;
    item.sum = vif.sum;
    item_collected_port.write(item);
  end
endtask
```

Note that analysis ports are built with new in the constructor, not with the factory.

### Step 7. The agent

The agent builds the driver, monitor and sequencer, then connects the driver's seq\_item\_port to the sequencer's seq\_item\_export.

### Step 8. The predictor, a reference model

The predictor extends uvm\_subscriber, which gives it a ready made analysis\_export and asks for one write() function. Whenever the monitor broadcasts, write() runs automatically.

```systemverilog
virtual function void write(adder_item t);
  adder_item expected_item;
  $cast(expected_item, t.clone());   // copy, so the monitor's item is untouched
  expected_item.sum = expected_item.a + expected_item.b;
  results_port.write(expected_item);
endfunction
```

clone() builds a new object and copies into it using do\_copy. It returns a uvm\_object handle, so $cast is needed again.

### Step 9. The scoreboard

The scoreboard receives two streams, actual results from the monitor and expected results from the predictor. A component can only define one function named write, so the macro uvm\_analysis\_imp\_decl creates two renamed versions.

```systemverilog
`uvm_analysis_imp_decl(_actual)
`uvm_analysis_imp_decl(_expected)

class adder_scoreboard extends uvm_scoreboard;
  `uvm_component_utils(adder_scoreboard)
  uvm_analysis_imp_actual   #(adder_item, adder_scoreboard) actual_imp;
  uvm_analysis_imp_expected #(adder_item, adder_scoreboard) expected_imp;
  adder_item actual_q[$], expected_q[$];

  function new(string name = "adder_scoreboard", uvm_component parent = null);
    super.new(name, parent);
    actual_imp   = new("actual_imp", this);
    expected_imp = new("expected_imp", this);
  endfunction

  virtual function void write_actual(adder_item item);
    actual_q.push_back(item);   compare_data();
  endfunction

  virtual function void write_expected(adder_item item);
    expected_q.push_back(item); compare_data();
  endfunction

  virtual function void compare_data();
    if (actual_q.size() > 0 && expected_q.size() > 0) begin
      adder_item act = actual_q.pop_front();
      adder_item exp = expected_q.pop_front();
      if (act.sum === exp.sum) `uvm_info("SB_PASS", "MATCH", UVM_LOW)
      else                     `uvm_error("SB_FAIL", "MISMATCH")
    end
  endfunction
endclass
```

The two queues line the streams up in order, and === compares including X and Z, so an X on the DUT output counts as a mismatch.

### Step 10. Environment, test and top

The environment builds the agent, predictor and scoreboard, then makes three connections.

1. Monitor port to the predictor's analysis\_export.
2. Monitor port to the scoreboard's actual\_imp.
3. Predictor results\_port to the scoreboard's expected\_imp.

One analysis port feeds two listeners, which is exactly what analysis ports are for.

The test raises an objection, starts the sequence on env.agent.sequencer, waits 10 more time units so the last item gets checked, and drops the objection.

```systemverilog
module top;
  adder_if inf();
  adder dut (.vif(inf));
  initial begin
    uvm_config_db #(virtual adder_if)::set(null, "*", "vif", inf);
    run_test("adder_test");
  end
endmodule
```

Here the path is "\*", so every component can get vif directly.

### Step 11. Catching a planted bug

The last slide changes one connection. Stage 2 takes c\_out\[0\] as its carry in instead of c\_out\[1\]. The scoreboard then reports MISMATCH for inputs where those two carries differ. That is the whole point, a wiring mistake found automatically, without anyone checking waveforms.

### Traps to watch for

- Modifying the monitor's item in the predictor instead of a clone. The expected and actual items would become the same object and every check would pass.
- Dropping the objection right after the sequence, before the last result is compared.
- Two write functions in one component without uvm\_analysis\_imp\_decl.

### Practice

1. Why is sum 5 bits wide while a and b are 4 bits?
2. With a = 9 and b = 8, what does the predictor put in sum, in decimal and binary?
3. Why does the monitor wait #10 before sampling?
4. In the bugged adder, find the DUT output for a = 2 and b = 2. Does the scoreboard pass or fail?
5. Give one input pair that passes even with the bug, and explain why.
6. Why must the predictor work on t.clone() instead of t?
7. Add a functional coverage subscriber that covers a and b with 4 bins each and their cross. Show its write().

### Answers

1. Two 4 bit numbers can add to at most 30, which needs 5 bits.
2. 17, which is 5'b10001.
3. The driver applies inputs and the combinational logic needs time to settle before the sum is valid.
4. Bit 1 makes a carry, but stage 2 takes carry 0, which is 0. The DUT outputs 0 instead of 4, so the scoreboard fails.
5. a = 3 and b = 0. No stage makes a carry, so c\_out\[0\] and c\_out\[1\] are both 0 and the wrong wire carries the right value.
6. The monitor's item is also going to the scoreboard. Changing it would change the actual value, and the comparison would test nothing.
7. One version is below.

```systemverilog
class adder_cov extends uvm_subscriber #(adder_item);
  `uvm_component_utils(adder_cov)
  adder_item it;
  covergroup cg;
    cp_a : coverpoint it.a { option.auto_bin_max = 4; }
    cp_b : coverpoint it.b { option.auto_bin_max = 4; }
    axb  : cross cp_a, cp_b;
  endgroup
  function new(string name, uvm_component parent);
    super.new(name, parent);
    cg = new();
  endfunction
  virtual function void write(adder_item t);
    it = t;
    cg.sample();
  endfunction
endclass
```

## Lecture 12. Advanced Interfaces

A virtual interface is a handle that points to a real interface, the way a class handle points to an object. It lets one driver class or one monitor class serve many identical ports, with the actual wires chosen at run time. This lecture follows chapter 10 of Spear and Tumbush.

### Step 1. Back to the 4x4 ATM router

The router from Lecture 5 has 4 receive ports and 4 transmit ports. Each port has an 8 bit data bus plus one bit control and status signals soc, en, clav, rclk, tclk and clk.

Each receive interface and each transmit interface has a TB modport, a DUT modport and a clocking block named cb.

```systemverilog
interface Rx_if (input logic clk);
  logic [7:0] data;
  logic soc, en, clav, rclk;

  clocking cb @(posedge clk);
    output data, soc, clav;   // testbench drives these
    input  en;                // testbench samples this
  endclocking

  modport DUT (output en, rclk, input data, soc, clav);
  modport TB  (clocking cb);
endinterface
```

The top module makes arrays of interfaces, then hands them to the testbench and the DUT.

```systemverilog
module top;
  logic clk, rst;
  Rx_if Rx[4] (clk);
  Tx_if Tx[4] (clk);
  test t1 (Rx[0], Rx[1], Rx[2], Rx[3], Tx[0], Tx[1], Tx[2], Tx[3], clk, rst);
  atm_router a1 (Rx[0], Rx[1], Rx[2], Rx[3], Tx[0], Tx[1], Tx[2], Tx[3], clk, rst);
  initial begin clk = 0; forever #20 clk = !clk; end
endmodule
```

### Step 2. The problem with physical interfaces

With only physical interfaces, a monitor task must name one specific port, such as Tx0. You end up writing receive\_cell0, receive\_cell1 and so on, four nearly identical copies.

What you want is one Driver class and one Monitor class, each built four times, each pointed at a different port.

### Step 3. Virtual interface basics

1. Declare one with the word virtual, as in `virtual Rx_if.TB vRx;`.
2. Until you assign it, it holds null, just like an unconstructed class handle.
3. It can be a class property, a function or task argument, or an array element.
4. A class usually receives it through its new() function.

The binding happens at run time, not compile time, which is why the same code can drive any port. Section 25.9 of IEEE Std 1800-2012 has more detail.

### Step 4. The testbench with virtual interfaces

```systemverilog
program automatic test (Rx_if.TB Rx0, Rx1, Rx2, Rx3,
                        Tx_if.TB Tx0, Tx1, Tx2, Tx3,
                        input logic clk, output logic rst);
  Driver  drv[4];
  Monitor mon[4];
  virtual Rx_if.TB vRx[4] = '{Rx0, Rx1, Rx2, Rx3};
  virtual Tx_if.TB vTx[4] = '{Tx0, Tx1, Tx2, Tx3};

  initial foreach (drv[i]) begin
    drv[i] = new(vRx[i]);   // driver i talks to receive port i
    mon[i] = new(vTx[i]);   // monitor i watches transmit port i
  end
endprogram
```

The slides also show a shorter form. Put the arrays straight in the port list, as in `program automatic test (Rx_if.TB Rx[4], Tx_if.TB Tx[4], ...);`, which has the same effect.

### Step 5. The monitor class

The monitor now refers to its own handle instead of the fixed name Tx0. A typedef keeps the long type name short.

```systemverilog
typedef virtual Tx_if.TB vTx_t;

class Monitor;
  vTx_t Tx;
  function new(vTx_t Tx);
    this.Tx = Tx;
  endfunction

  task receive_cell();
    Tx.cb.clav <= 1;                  // ready to accept a cell
    @(Tx.cb iff Tx.cb.soc == 1);      // wait for start of cell
    // read Tx.cb.data byte by byte here
  endtask
endclass
```

### Step 6. Two ways to connect a test to its interfaces

Option 1 is port lists. The top module passes the interface into the test's ports. It is simple, but adding a second interface means editing both the top module and the test's port list.

Option 2 is a cross module reference, or XMR. An XMR is a hierarchical path like top.arbif that reaches into another module by name. The test has no ports and grabs the interface itself.

```systemverilog
program automatic test;
  virtual arb_if.TEST arbif = top.arbif;   // XMR
  initial begin
    arbif.cb.request <= 0;
    @arbif.cb;
  end
endprogram
```

Now the top module can gain new interfaces and old tests still work unchanged. The cost is that the test depends on names inside top. If you are not reusing tests across designs, plain port lists are fine.

### Step 7. Arrays of replicated components

The last example builds a 1D array of identical 8 bit counters, and the same idea extends to 2D meshes. The interface holds din, dout, load and reset\_l, plus a clocking block and modports. A generate loop places one counter per interface.

```systemverilog
module top;
  parameter NUM_XI = 2;
  bit clk;
  initial forever #20 clk = !clk;

  X_if xi [NUM_XI] (clk);
  test tb ();

  generate
    for (genvar i = 0; i < NUM_XI; i++) begin : gen
      counter c (xi[i]);
    end
  endgenerate
endmodule
```

The test grabs the whole array by XMR and builds one driver per counter. You could pass NUM\_XI as a parameter instead of reaching for it.

```systemverilog
program automatic test;
  virtual X_if.TB vxi [top.NUM_XI];
  Driver driver [];
  initial begin
    vxi = top.xi;
    driver = new[top.NUM_XI];
    foreach (driver[i]) driver[i] = new(vxi[i], i);
  end
endprogram
```

### Traps to watch for

- Using a virtual interface before assigning it, which is a null access.
- Forgetting the modport in the virtual interface type, which loses the direction checks.
- Hard coding one port name inside a class, which defeats the purpose.

### Practice

1. In one sentence, how is a virtual interface different from an interface?
2. A class has `virtual Rx_if.TB vif;` and its new() never sets it. What happens when run() does `vif.cb.soc <= 1;`?
3. Write the declaration and initialization of an array of 4 virtual Tx\_if.TB handles from physical ports Tx0 to Tx3.
4. Why is one Driver class built four times better than four Driver classes?
5. Give one advantage and one drawback of using an XMR like top.arbif inside the test.
6. Write a Driver class that takes a virtual Rx\_if.TB in new() and has a task send\_byte(input logic \[7:0\] b) that drives data with soc high for one clock.

### Answers

1. An interface is the actual bundle of wires, while a virtual interface is a handle that points to one.
2. A null access error at run time.
3. `virtual Tx_if.TB vTx[4] = '{Tx0, Tx1, Tx2, Tx3};`
4. Any fix or feature is written once, and the ports cannot drift apart.
5. Adding interfaces in top does not change the test's ports. The drawback is that the test now depends on hierarchy names in top.
6. One version is below.

```systemverilog
class Driver;
  virtual Rx_if.TB rx;
  function new(virtual Rx_if.TB rx);
    this.rx = rx;
  endfunction

  task send_byte(input logic [7:0] b);
    rx.cb.data <= b;
    rx.cb.soc  <= 1;
    @rx.cb;
    rx.cb.soc  <= 0;
  endtask
endclass
```

## Lectures 13 and 14. Functional Coverage in Depth

This lecture revisits Lecture 4 using chapter 9 of Spear and Tumbush, and adds the workflow around coverage. You learn how to run many seeds, read the report, and shape bins and crosses so the report says something useful. The covergroup basics from Lecture 4 still apply, so this section only covers what is new.

### Step 1. Seeds

The seed is the starting number for the random generator. Every run with the default seed produces exactly the same values, so rerunning teaches you nothing new. Each run should get a different seed.

- A common choice is the time of day.
- When many jobs start at once on a farm of machines, combine the time with the machine name or process ID so no two jobs share a seed.

In VCS you pass it on the command line.

```bash
./simv +ntb_random_seed=1234
```

Two system functions read command line options inside your code. `$test$plusargs("name")` returns true if +name was given. `$value$plusargs("name=%d", var)` also reads its value into var.

```systemverilog
int seed;
initial if ($value$plusargs("ntb_random_seed=%d", seed))
  $display("Running with seed %0d", seed);
```

### Step 2. Organizing results

Each run produces a log file and coverage data. Record the seed with them, or you cannot reproduce a failure. The slides suggest one directory per run with the seed in its name.

In VCS, `urg -dir simv.vdb` builds the coverage report into a folder called urgReport. URG stands for Unified Report Generator.

### Step 3. The coverage feedback loop

1. Compile once, then run the test many times with different seeds.
2. Check that no run found a design bug. Coverage from a run that found a bug is thrown away.
3. Merge coverage across runs.
4. If coverage is short of 100 percent, first try more seeds or longer runs.
5. Then add constraints that steer stimulus into the missed areas.
6. Last, write directed tests for corners random stimulus will not reach.

Coverage climbs quickly at first and then flattens out. That flat part is your signal to change constraints rather than just add seeds.

### Step 4. Code coverage versus functional coverage

Code coverage is measured automatically by the simulator from the RTL. It is also called implementation coverage.

- Line coverage counts which lines ran.
- Path coverage counts which branches through the code ran.
- Toggle coverage counts which signals switched between 0 and 1.
- FSM coverage counts which states and transitions of a state machine were visited.

Code coverage cannot tell you about a feature that was never written. Functional coverage comes from the verification plan, so it can show a missing feature as an empty bin. Assertion coverage, which counts how often each assertion was exercised, is the third kind. A good plan uses all three.

### Step 5. Gather information, not data

A huge report is hard to act on. Aim bins at the interesting cases.

- A FIFO with 1K entries has 1K possible fill levels. The important ones are full and empty. Covering a full to empty run hits both corners with two bins.
- An N bit counter has 2 to the N states. Cover a few random values, some interesting values, and the rollover from all ones to all zeros.

### Step 6. The worked example

A Transaction class has a random 32 bit data and a random 3 bit dst, and only dst is covered.

```systemverilog
class Transaction;
  rand bit [31:0] data;
  rand bit [2:0]  dst;
endclass

program automatic test;
  Transaction tr;
  covergroup CovDst;
    coverpoint tr.dst;
  endgroup

  initial begin
    CovDst ck = new();
    repeat (32) begin
      tr = new();
      assert(tr.randomize());
      ck.sample();
    end
  end
endprogram
```

After 32 transactions, 7 of the 8 dst values were seen and only 0 was missing. Running 33 transactions reached all 8, 100 percent. Random stimulus gets the last bins slowly.

### Step 7. Embedded covergroups

A covergroup declared inside a class is an embedded covergroup. It must be constructed inside the class's new() function. Its instance name is the covergroup name itself, as in `CovDst = new();`.

Give covergroups and cover points descriptive names, because those names are all you see in the report.

### Step 8. auto\_bin\_max for one point or a whole group

With a 3 bit dst and `option.auto_bin_max = 2`, the two automatic bins are \[0:3\] and \[4:7\]. Placed inside one coverpoint it affects only that point. Placed at the covergroup level it applies to every point in the group.

```systemverilog
covergroup CovGroup;
  option.auto_bin_max = 2;     // whole group
  coverpoint tr.dst;
  coverpoint tr.data[3:0];
endgroup
```

### Step 9. Covering an expression, and width

A cover point can be an expression. Watch the width, though, because the expression's width sets how many automatic bins exist.

```systemverilog
// hdr_len is 3 bits, payload_len is 4 bits
len16 : coverpoint (p.hdr_len + p.payload_len);          // 4 bit result, only 16 bins
len32 : coverpoint (p.hdr_len + p.payload_len + 5'b0);   // 5 bit result, 32 bins
```

The largest true sum is 7 + 15 = 22, which needs 5 bits. Adding 5'b0 forces 5 bit math so large sums are not wrapped.

### Step 10. Named bins in detail

```systemverilog
coverpoint tr.kind {          // kind is 4 bits
  bins zero  = {0};           // one bin for 0
  bins lo    = {[1:3], 5};    // one bin for 1, 2, 3 and 5
  bins hi[]  = {[8:$]};       // a separate bin for each of 8 to 15
  bins misc  = default;       // everything else, 4, 6 and 7
}
```

1. Square brackets after the name, as in hi\[\], make one bin per value instead of one bin for the group.
2. The dollar sign in \[8:$\] means the largest possible value.
3. A default bin is not counted toward the coverage percentage.

### Step 11. Conditional coverage, enums and wildcards

Two ways to skip sampling during reset are equivalent. The iff form is more compact.

```systemverilog
coverpoint port iff (!bus_if.reset);

// or, from the test
cg.stop();  @(negedge bus_if.reset);  cg.start();
```

For an enum, automatic bins are one per enum name, and auto\_bin\_max is ignored.

A wildcard bin uses ? for a bit that can be 0 or 1. This splits a 3 bit dst into even and odd.

```systemverilog
coverpoint dst {
  wildcard bins even = {3'b??0};
  wildcard bins odd  = {3'b??1};
}
```

Transition bins, ignore\_bins and illegal\_bins work as in Lecture 4.

### Step 12. Cross coverage done well

If one point has M bins and the other has N, their cross has M × N bins. A 4 bit kind crossed with a 3 bit port gives 16 × 8 = 128 bins, most of them noise. Three tools fix that.

1. Label the cover points and define bins on them, so the cross inherits readable names.
2. Remove cross bins you do not care about with ignore\_bins and binsof ... intersect.
3. Set option.weight = 0 on a cover point to keep it out of the total score when only the cross matters.

```systemverilog
covergroup CovPortKind;
  port : coverpoint tr.port { bins port[] = {[0:$]}; }
  kind : coverpoint tr.kind {
    bins zero = {0};
    bins lo   = {[1:3]};
    bins hi[] = {[8:$]};
    bins misc = default;
  }
  cross kind, port {
    ignore_bins hi = binsof(port) intersect {7};
    ignore_bins md = binsof(port) intersect {0} && binsof(kind) intersect {[9:11]};
    ignore_bins lo = binsof(kind.lo);
  }
endgroup
```

Read binsof(port) intersect {7} as every cross bin where port is 7.

The slides also show two ways to cover just the useful combinations of two 1 bit signals a and b, namely a0b0, a1b0 and anything with b = 1.

```systemverilog
// with a cross and named cross bins
a  : coverpoint tr.a { bins a0 = {0}; bins a1 = {1}; option.weight = 0; }
b  : coverpoint tr.b { bins b0 = {0}; bins b1 = {1}; option.weight = 0; }
ab : cross a, b {
  bins a0b0 = binsof(a.a0) && binsof(b.b0);
  bins a1b0 = binsof(a.a1) && binsof(b.b0);
  bins b1   = binsof(b.b1);
}

// alternatively, one cover point on the concatenation {a, b}
coverpoint {tr.a, tr.b} {
  bins a0b0 = {2'b00};
  bins a1b0 = {2'b10};
  wildcard bins b1 = {2'b?1};
}
```

### Traps to watch for

- Running every simulation with the default seed.
- Counting coverage from runs that found a bug.
- An expression cover point that is too narrow and silently wraps.
- Leaving a big cross untrimmed, so the percentage stays tiny and means nothing.

### Practice

1. Two runs use the same seed and the same code. How do their coverage results compare?
2. Name the four kinds of code coverage, and give one bug that 100 percent code coverage would still miss.
3. A 3 bit dst has auto\_bin\_max = 4. List the bins.
4. hdr\_len is 3 bits and payload\_len is 3 bits. How many automatic bins does `coverpoint (hdr_len + payload_len)` get, and what goes wrong?
5. For `bins lo = {[1:3], 5}; bins hi[] = {[12:$]};` on a 4 bit kind, how many bins are created in total?
6. A 2 bit x is crossed with a 3 bit y, both with automatic bins. How many cross bins exist, and how many remain after `ignore_bins skip = binsof(y) intersect {0, 1};`?
7. Write a coverpoint on a 4 bit opcode with one bin for 0, one bin per value from 1 to 3, a bin for all even values from 4 to 15 using wildcards, and treat 15 as illegal.

### Answers

1. They are identical, because the same seed repeats the same random values.
2. Line, path, toggle and FSM. A feature that was never written, such as a missing error check, has no code to cover.
3. &#91;0:1\], \[2:3\], \[4:5\] and \[6:7\].
4. The sum is 3 bits wide, so only 8 bins exist and sums from 8 to 14 wrap around into the low bins. Add a 4'b0 to widen it.
5. lo is 1 bin and hi\[\] is 4 bins for 12 to 15, so 5 in total.
6. 4 × 8 = 32 cross bins. Removing y = 0 and y = 1 drops 2 × 4 = 8, leaving 24.
7. One version is below. The illegal 15 is excluded even though the even wildcard does not match it anyway.

```systemverilog
coverpoint opcode {
  bins zero    = {0};
  bins low[]   = {[1:3]};
  wildcard bins even = {4'b?1?0, 4'b1??0};   // 4, 6, 8, 10, 12, 14
  illegal_bins bad   = {15};
}
```

## Lectures 14 to 16. Advanced Assertions

This deck starts by repeating the Lecture 10 slides, so read that section first. The new material answers a deeper question, which is exactly when in a time step an assertion looks at the signals. Once you know the simulator's scheduling regions, the three kinds of assertions and their glitch behavior make sense.

### Step 1. Fixes to the coverage lecture

Only sample() records coverage. start() and stop() just turn recording on and off, and any sample() call between a stop() and the next start() is ignored. The slides also clarify that a coverpoint can be an expression, as covered in Step 9 of Lectures 13 and 14.

### Step 2. Severity levels for failures

A failing assertion reports at one of four levels. The default is error.

- `$fatal(finish_number, "message", args)` ends the simulation.
- `$error` reports an error and keeps going.
- `$warning` reports a warning.
- `$info` just prints a note.

For `$fatal`, finish\_number sets how much it prints on exit. 0 prints nothing extra, 1 adds the time and location, and 2 also adds CPU statistics.

`$assertoff` pauses assertions but lets any check already in progress finish. `$assertkill` pauses them and also kills checks in progress. `$asserton` turns them back on.

### Step 3. Built in functions for assertions

Each comes with the slide's example.

```systemverilog
// $past, the value on the previous clock edge
property p_counter_inc;
  @(posedge clk) disable iff (reset)
  inc |-> (count == $past(count) + 1);
endproperty

// $rose, the LSB changed to 1 since the last edge
property p_handshake;
  @(posedge clk) $rose(request) |-> ##[1:4] grant;
endproperty

// $fell, the LSB changed to 0. One cycle after ack, req must drop
property p_req_drop;
  @(posedge clk) disable iff (rst) ack |=> $fell(req);
endproperty

// $stable, unchanged since the last edge
property p_data_stable;
  @(posedge clk) (valid && !ready) |=> (valid && $stable(data));
endproperty

// $countones, the number of 1 bits
assert property (@(posedge clk) $countones(gnt_bus) <= 2);

// $isunknown, true if any bit is X or Z
chk_cmd_valid: assert property (@(posedge clk) disable iff (reset)
  !$isunknown(cmd_bus))
  else $error("Time %0t cmd_bus has X or Z: %h", $time, cmd_bus);

// $onehot, exactly one bit is 1. $onehot0, at most one bit is 1
assert property (@(posedge clk) $onehot(grant));     // 4 way arbiter, one winner
assert property (@(posedge clk) $onehot0(grant));    // also allows no winner when idle
```

The ##\[1:4\] in p\_handshake is a range. grant must arrive 1, 2, 3 or 4 cycles later.

### Step 4. Two kinds of events in the simulator

An update event is a change in a variable's value, such as a nonblocking assignment that changes a. An evaluation event is something that triggers other code to run, such as a rising edge of clk waking an always block.

### Step 5. The scheduling regions

Each simulation time step is split into regions that run in a fixed order. Here is the normal flow.

1. Preponed. The instant just before anything changes. Assertions sample their signal values here, so they always see the settled values from the end of the previous step.
2. Active. Design code runs here, such as continuous assignments, blocking assignments and the right hand sides of nonblocking assignments. Events in this queue run in any order.
3. Inactive. Statements delayed by #0 wait here until the active queue empties, then move back to active.
4. NBA. Nonblocking assignments update their left hand sides here, in the order they were written.
5. Observed. Concurrent assertions, sequences and properties are evaluated here, using the values sampled in Preponed. Nothing changes value in this region.
6. Reactive, Re-Inactive and Re-NBA. A mirror of the active set, used for testbench code in program blocks and checkers.
7. Postponed. The very end of the step. Final deferred assertions, `$monitor` and `$strobe` run here.

The flow is not strictly one way. If the reactive region changes a design signal, the simulator loops back to Active, which is where the complications come from.

The slides walk through an example with a design module procReq, a test program, and a top module, placing each event in its region at time 0 and time 5. The rule to remember is that module assignments run in the Active set and program assignments run in the Reactive set.

### Step 6. Glitches

Suppose `assign a = b | c;` and, at the same time, b goes from 1 to 0 while c goes from 0 to 1. a starts at 1 and ends at 1. But if the simulator updates b, then recomputes a, then updates c, a briefly reads 0 in between. That zero width pulse is a glitch, and it comes from a race between two events in the same region.

A check that runs in the middle of that order can report a failure that is not real.

### Step 7. The three kinds of assertions

1. Immediate assertions use plain assert. They work like an if statement inside procedural code and run when control reaches them. They can report false failures from glitches.
2. Deferred assertions are immediate assertions that wait before reporting. assert #0 is an observed deferred assertion. It filters glitches within one region set. assert final is a final deferred assertion, evaluated in Postponed, so it filters glitches across both the Active and Reactive sets. Both can sit inside or outside procedural code.
3. Concurrent assertions use assert property. They are clocked, describe behavior over many cycles, and sample in Preponed. They can sit inside or outside procedural code, but never inside a function or task.

The slides' immediate assertion example sits in an always\_comb that reruns whenever a or b changes. It reports pass at times 0, 50, 150 and 190, and fail at 90. Since passes are expected, you usually print only failures.

```systemverilog
always_comb
  a1: assert (!(a && !b)) else $error("a1 failed");
```

A trap the slides call short circuiting follows. In `assign ok = v && check3bits(x);` once v is 0 the simulator never calls check3bits. Any assertion inside that function never runs, so its error can never appear.

### Step 8. How deferral removes the false failure

At t = 50, suppose a becomes 1 a moment before b does.

1. A plain immediate assertion runs as soon as a changes, sees a = 1 and b = 0, and reports a failure. Then b changes and it passes. You get one false failure plus a pass.
2. With assert #0, the failure is put in a report queue instead of printed. When the assertion runs again after b changes, the earlier failure is flushed and only the pass is reported.
3. With assert final, reporting waits until Postponed. This also handles the case where b is changed by a program in the Reactive set, which assert #0 cannot see past.

Flushing also happens when the procedure hits an event control, such as a wait statement.

### Step 9. Building a concurrent assertion

A concurrent assertion is built in three layers.

```systemverilog
sequence s_req_ack;
  req ##[1:2] ack;              // events over time
endsequence

property p_req_ack;
  @(posedge clk) disable iff (rst)
  start |-> s_req_ack;          // built from sequences
endproperty

chk_req_ack: assert property (p_req_ack);   // checked during simulation
```

1. A sequence lists expressions in clock order. ## is the cycle delay operator, so `a ##[1:2] b` means b follows a 1 or 2 clock edges later.
2. A property combines sequences, usually with an implication.
3. The assert statement checks the property every clock.

In the label example `a1: assert property (@(posedge clk) disable iff (rst) a |-> nexttime[2] b);`, the property is a |-> nexttime\[2\] b, posedge clk is the clocking event, and rst is the disabling condition. nexttime\[2\] b means b at the second clock tick from now.

A concurrent assertion with just a signal for its clock, like `a3: assert property (@clk a != b);`, is checked on every change of clk, both edges.

### Step 10. Implication

- In `A |-> B`, A is the antecedent and B is the consequent. This overlapped form checks B starting on the same clock edge A matched.
- In `A |=> B`, the non overlapped form, B is checked starting on the next clock edge.
- If A does not match, the implication is vacuously true. It passes without checking anything, so a property can pass all simulation while never really being tested.

That last point is why cover property exists. It counts how many times a property actually matched, so you can see whether it was exercised.

```systemverilog
c_req: cover property (@(posedge clk) req ##[1:2] ack);
```

Sequences can also be combined with the operators and, intersect, or, first\_match, throughout and within, which the next lecture covers.

### Traps to watch for

- Expecting an assertion to see a value assigned earlier in the same time step. Concurrent assertions see the Preponed values.
- Trusting a passing implication that was never triggered. Add a cover property.
- Putting an assertion inside a function that may be skipped by short circuit evaluation.
- Using plain immediate assertions on combinational signals and chasing glitch failures.

### Practice

1. Which severity task stops the simulation, and which is the default for a failed assertion?
2. What is the difference between $assertoff and $assertkill?
3. An 8 bit grant bus is 8'b0000\_0000. What do $onehot and $onehot0 return?
4. A nonblocking assignment q <= d runs at a clock edge. Does a concurrent assertion at that same edge see the old q or the new q, and why?
5. Put these regions in order. Observed, NBA, Preponed, Postponed, Active, Reactive.
6. Write a property that if req rises, ack must be high within 1 to 3 cycles, disabled during rst. Then write a matching cover property for the req rising case.
7. Explain why `assign ok = v && check(x);` can hide an assertion failure inside check.

### Answers

1. $fatal stops it. The default severity is error.
2. $assertoff lets checks already running finish. $assertkill stops them immediately.
3. $onehot returns false and $onehot0 returns true.
4. The old q. Assertions sample in Preponed, before the NBA region updates q.
5. Preponed, Active, NBA, Observed, Reactive, Postponed.
6. `assert property (@(posedge clk) disable iff (rst) $rose(req) |-> ##[1:3] ack);` and `cover property (@(posedge clk) $rose(req));`.
7. When v is 0, && already knows the answer is 0, so check is never called and its assertion never runs.

## Lectures 16 to 18. SVA

This deck turns assertions into a working toolkit. It covers how to clock and organize properties, then walks through every sequence operator for repetition and combining sequences. Most slides are figures from Mehta, SystemVerilog Assertions and Functional Coverage, so the examples below are written fresh to show the same operators.

One idea makes every operator easier. A sequence can start on every clock edge, and each start is its own independent attempt, called a thread. An assertion fails if any attempt that started fails.

### Step 1. Immediate and concurrent, as Mehta frames them

An immediate assertion is not temporal. It lives inside procedural code, runs the moment it is reached, tests one condition, and runs a pass or fail action. It can be fooled by glitches, which deferred assertions fix.

A concurrent assertion is built on sequences over time and samples on a clock edge. Its property has an antecedent that is sampled and a consequent that is checked. Action blocks say what happens on pass or fail.

```systemverilog
ap_req: assert property (@(posedge clk) req |=> ack)
  $display("pass");                 // pass action, optional
  else $error("ack missing");        // fail action
```

### Step 2. Implication, again

1. If the antecedent is false, nothing is checked for that attempt.
2. If it is true, the consequent is checked.
3. |-> starts the consequent on the same edge. |=> starts it on the next edge, so `a |=> b` is exactly `a |-> ##1 b`.

You do not need sequence ... endsequence for a simple sequence. You can write it straight into the property.

### Step 3. Aside on print statements

- `$display` prints right away in the Active region. If the value it prints is set by a nonblocking assignment, it shows the old value.
- `$write` is the same but adds no newline.
- `$strobe` prints once, at the end of the time step in the Postponed region, so it shows final values.
- `$monitor` is called once and then prints in Postponed every time one of its arguments changes. Only one $monitor is active at a time, and starting a new one replaces the old one.

### Step 4. Reusability versus readability

You can name a sequence or property and give it arguments, then reuse it with different signals. That is reusable but you have to jump around to read it. Writing everything inline is easier to read once but cannot be reused.

```systemverilog
sequence s_hs (req, ack, n);
  req ##n ack;
endsequence

property p_hs (clk, req, ack);
  @(posedge clk) $rose(req) |-> s_hs(req, ack, 2);
endproperty

ap_bus0: assert property (p_hs(clk, req0, ack0));
ap_bus1: assert property (p_hs(clk, req1, ack1));
```

### Step 5. Where the clock comes from

The clock can be written in the sequence, in the property, or in the assert itself. To avoid repeating it, declare a default clocking block, and every assertion without its own clock uses it.

```systemverilog
default clocking cb @(posedge clk);
endclocking

ap1: assert property (req |=> ack);                     // uses posedge clk
ap2: assert property (@(posedge clk2) start |-> ##2 done); // overrides the default
```

The slides call this mix and match. You can override the default, or name a different clock inside a single property.

### Step 6. Delays and ranges

- `a ##2 b` means b two clock edges after a.
- `a ##[1:3] b` means b 1, 2 or 3 edges after a. Each choice is a separate possible match.
- `a ##[1:$] b` means b at some later edge, with no upper limit. The $ means unbounded.

### Step 7. A common fix, use $rose

What people often write first is `req |-> ##[1:3] ack`. If req stays high for 5 cycles, that starts 5 separate checks, each wanting its own ack. What you usually mean is better written with $rose, so only the rising edge of req starts a check.

```systemverilog
ap_good: assert property (@(posedge clk) $rose(req) |-> ##[1:3] ack);
```

The variants slides also show wrapping a common failure message in a macro so every assertion reports the same way.

```systemverilog
`define failmsg(msg) $error("[%0t] FAILURE: %s", $time, msg)
ap_x: assert property (@(posedge clk) !$isunknown(bus)) else `failmsg("bus has X");
```

### Step 8. disable iff is used once

disable iff can appear only once, at the top of a property. You cannot nest one inside a sequence or inside another disable iff. If you need several reset conditions, combine them in one expression, as in `disable iff (rst || test_mode)`.

### Step 9. Binding properties to a design

bind attaches a module full of assertions to a design module without editing the design's source. The design team keeps clean RTL and the verification team keeps its checkers separate.

```systemverilog
module fifo_props (input logic clk, rst, push, pop, full, empty);
  ap_no_push_full: assert property (@(posedge clk) disable iff (rst) full |-> !push);
  ap_no_pop_empty: assert property (@(posedge clk) disable iff (rst) empty |-> !pop);
endmodule

// every instance of fifo gets its own copy of the checker
bind fifo fifo_props u_props (.clk(clk), .rst(rst), .push(push),
                              .pop(pop), .full(full), .empty(empty));
```

### Step 10. Consecutive repetition \[\*m\]

&#91;\*m\] repeats a sequence m times with one clock between repeats.

```systemverilog
s1 ##2 s2[*4] ##5 s3
// is the same as
s1 ##2 s2 ##1 s2 ##1 s2 ##1 s2 ##5 s3
```

A range \[\*m:n\] allows any count from m to n. For example `busy[*2:4]` means busy high for 2, 3 or 4 consecutive cycles.

### Step 11. Non consecutive repetition \[=m\] and goto repetition \[->m\]

Both count occurrences that do not have to be back to back. They differ in where the sequence is allowed to end.

1. `b[->3]` (goto) means b is true 3 times, gaps allowed, and the sequence ends exactly on the third b.
2. `b[=3]` means b is true 3 times, gaps allowed, and the sequence may end on the third b or any later cycle, as long as b does not occur a fourth time.

The difference shows when something follows.

```systemverilog
$rose(start) |-> b[->3] ##1 done   // done must come the cycle right after the 3rd b
$rose(start) |-> b[=3]  ##1 done   // done may come any time after the 3rd b, if no 4th b comes first
```

Ranges work too, as in `b[=2:4]` or `b[->1:3]`.

The slide marked not obvious points out that `b[=0]` is an empty match. It means b does not occur at all.

### Step 12. Combining sequences

1. `cond throughout seq` means cond stays true on every cycle while seq is running. Example `en throughout (start ##[1:5] done)`.
2. `seq1 within seq2` means seq1 happens entirely inside the time span of seq2. It starts at or after seq2 starts and ends at or before seq2 ends.
3. `s1 and s2` means both must match, starting at the same time. They may end at different times, and the combined match ends when the later one ends.
4. `s1 intersect s2` is and with a length rule. Both must start and end at the same time.
5. `s1 or s2` means at least one matches. They do not need the same length.
6. `first_match(seq)` keeps only the earliest match of a sequence that could match in several ways, such as one with a ##\[1:5\] range.
7. `not prop` passes when prop fails.
8. `if (cond) prop1 else prop2` picks which property to check based on cond.

### Traps to watch for

- Using a level signal like req as an antecedent when you mean its rising edge.
- Mixing up \[->m\] and \[=m\] when something must follow immediately.
- Expecting intersect to accept sequences of different lengths.
- A vacuous pass, where the antecedent never fires and the assertion never really checks anything.

### Practice

1. Rewrite `a |=> b` using only |-> and ##.
2. req is high on cycles 1 through 4. How many checks does `req |-> ##2 ack` start? How many does `$rose(req) |-> ##2 ack` start?
3. Write `a ##1 a ##1 a ##1 b` using a repetition operator.
4. b is high on cycles 2, 5 and 9, and done is high on cycle 10. Starting from cycle 1, does `b[->3] ##1 done` match? Does `b[=3] ##1 done` match?
5. Same as problem 4 but done is high on cycle 12 instead. Which of the two match now?
6. Sequence s1 lasts 3 cycles and s2 lasts 5 cycles, both starting together. Can `s1 and s2` match? Can `s1 intersect s2` match?
7. Write an assertion that once start rises, en must stay high on every cycle until done arrives within 1 to 8 cycles.
8. Write a bind statement that attaches a checker module arb\_props to every instance of a module named arbiter, connecting clk, req and gnt by name.

### Answers

1. `a |-> ##1 b`
2. Four checks, one per cycle req is high. Only one with $rose, at cycle 1.
3. `a[*3] ##1 b`
4. Both match. The third b is at cycle 9 and done is at cycle 10.
5. Only `b[=3] ##1 done` matches, since no fourth b came before cycle 12. The goto form needs done at cycle 10.
6. and can match, ending at cycle 5. intersect cannot, because the lengths differ.
7. `assert property (@(posedge clk) $rose(start) |-> en throughout (##[1:8] done));`
8. `bind arbiter arb_props u_arb_props (.clk(clk), .req(req), .gnt(gnt));`

## Lecture 19. Clock Domain Crossing

A clock domain crossing (CDC) happens whenever a signal launched by a flip flop on one clock is captured by a flip flop on a different clock. Ordinary simulation and timing checks assume one clock, so these paths need their own design rules and their own verification. The lecture ends by verifying an asynchronous FIFO with UVM and assertions, which ties the whole course together.

### Step 1. Why crossing clocks is dangerous

The capturing flip flop needs its input steady for a setup time before its clock edge and a hold time after it. When the two clocks are unrelated, the data will eventually change inside that window. Nothing in the design can prevent it.

Crossings come in two kinds. A synchronous crossing has clocks with a known, fixed relationship. An asynchronous crossing has no fixed relationship and needs a synchronizer, a handshake or a FIFO.

### Step 2. Metastability

If the input changes inside the setup and hold window, the flip flop can land halfway between 0 and 1 for a while before falling to one side. That in between state is called metastability. The slides compare it to a ball balanced on top of a hill. It will roll off, but you cannot say when or which way.

Metastability cannot be eliminated, only made unlikely. The measure is MTBF, mean time between failures. The slide's variables are these.

- S is how much time the flip flop gets to settle, measured from the clock edge.
- fC is the clock frequency.
- fD is how often the data changes.
- τ and TW are flip flop constants, each close to one gate delay.

The probability that one data change causes a failure is

```latex
P_{\text{fail}} = T_W \, f_C \, e^{-S/\tau}
```

Multiplying by fD gives the failure rate, and MTBF is its inverse.

```latex
\text{MTBF} = \frac{e^{S/\tau}}{T_W \, f_C \, f_D}
```

The slide plugs in 28 nm numbers, τ = 10 ps and TW = 20 ps, with fC = 1 GHz and fD = 100 MHz. The denominator is 20 ps × 1 GHz × 100 MHz, which is 2 × 10^6 per second.

1. With S = 0.1 ps, e^(0.01) is about 1.01, so MTBF is about 1.01 / (2 × 10^6) seconds, which is 505 ns. Failure is practically constant.
2. With S = one clock period, 1 ns, e^(100) is about 2.7 × 10^43, so MTBF is about 1.3 × 10^37 seconds, or 4 × 10^29 years. The universe is about 10^10 years old.

The exponent is the whole story. Giving the flip flop one extra clock period to settle turns constant failure into never.

### Step 3. The two flop synchronizer

That is exactly what a two flop synchronizer does. The first flop may go metastable, and the second flop samples it one full clock later, after it has almost surely settled. The design only fails if both flops fail.

```systemverilog
module sync2 (input logic dst_clk, rst_n, d_async, output logic q_sync);
  logic meta;
  always_ff @(posedge dst_clk or negedge rst_n)
    if (!rst_n) {q_sync, meta} <= '0;
    else        {q_sync, meta} <= {meta, d_async};
endmodule
```

Treating the two failures as independent, the slides square the single flop term.

```latex
\text{MTBF}_{2\text{FF}} = \left(\frac{e^{S/\tau}}{T_W f_C}\right)^{2} \frac{1}{f_D}
\quad \text{versus} \quad
\text{MTBF}_{1\text{FF}} = \frac{e^{S/\tau}}{T_W f_C} \cdot \frac{1}{f_D}
```

### Step 4. Data loss and data incoherence

How close the data change lands to the clock edge decides what goes wrong.

- Data loss. A short pulse in the source domain can fall entirely between two destination edges and never be seen.
- Data incoherence. Bits of a bus can each resolve on a different cycle. In the slide, X\[1:0\] crosses into Y\[1:0\] and only 00 and 11 are legal. Going from 00 to 11, one bit may arrive a cycle before the other, so Y briefly reads 01 or 10, a value the design never intended.

### Step 5. How the two clocks can relate

1. Same frequency, no phase difference. This is really one clock domain.
2. Same frequency, constant phase difference.
3. Asynchronous, with no fixed relationship.
4. Different frequency with a varying phase difference, either integer multiples or rational multiples. Edges are sometimes never close and sometimes intermittently close, which is the dangerous case.

Jitter, small random variation in when clock edges arrive, either chip wide or local, makes even nominally related clocks drift close to each other.

### Step 6. Reconvergence

Reconvergence means two signals cross through separate synchronizers and then meet again in logic. Each synchronizer may take one cycle or two, so the two signals can arrive a cycle apart. This is incoherence again, hidden behind correct looking synchronizers.

### Step 7. Best practices and synchronizer types

- Register a signal in its source domain before it crosses. Never feed combinational logic straight into a synchronizer, because its glitches can be captured.
- Synchronize each single bit control signal with a two flop synchronizer.
- Never synchronize a multi bit bus one bit at a time. Use Gray code, a handshake or a FIFO.
- A signal crossing into a slower domain should stay stable for about 1.5 times the receiving clock period. This is called the three edge requirement, because the receiver then sees it across three consecutive clock edges.

The three standard synchronizer types follow.

1. Multiple flip flops, as in Step 3, for single bits.
2. Recirculation mux. A synchronized enable selects new data into the destination register, and otherwise the register feeds its own value back. The data bus only needs to be stable while the enable crosses.
3. Closed loop, a request and acknowledge handshake. The source holds data and raises req, the destination synchronizes req, captures the data and returns ack, and the source waits for the synchronized ack before changing anything.

For streams of data, the answer is a FIFO synchronizer, from Cummings' SNUG paper. It is the asynchronous FIFO in Step 9.

### Step 8. Verifying CDC in five steps

These steps come from Yeung's Mentor paper, Five Steps to Quality CDC Verification.

1. Identify which blocks have crossings.
2. Document the CDC requirements, meaning the operating modes, the clocks, the interface signals and the synchronization rules.
3. Formalize known exceptions. For example, configuration, status and control registers that are set once and then held stable may not need a synchronizer.
4. Define coverage goals.
5. Choose a strategy. That could be block level, top level, triage and bug hunting, or targeting coverage.

At block level, structural analysis reports correct synchronizers, missing or broken ones, complex ones that need protocol checks, and possible reconvergence. Then formal analysis verifies the protocols.

At top level, structural checks repeat with similar criteria, protocols are checked with constrained random simulation, and metastability effects are checked by injecting random extra delays at synchronizers during simulation.

### Step 9. The asynchronous FIFO example

The slides verify an open source asynchronous FIFO from GitHub. It has five parts.

1. fifo\_mem, the RAM with 8 bit data and configurable depth.
2. fifo\_wr, the write side. It produces binary write addresses and a Gray coded write pointer, gray\_w\_ptr, and computes the full flag.
3. fifo\_rd, the read side. It produces read addresses and a Gray coded read pointer, gray\_rd\_ptr, and computes the empty flag.
4. Two BIT\_SYNC multi flop synchronizers. One carries the write pointer into the read domain as w2r\_ptr, and the other carries the read pointer into the write domain as r2w\_ptr.
5. Gray code for the pointers. In Gray code only one bit changes per increment. If a crossing catches the pointer mid change, it reads either the old value or the new one, never a wild value. That is how the FIFO avoids the incoherence problem from Step 4.

The UVM environment uses exactly the parts from Lectures 8 and 12. It has an interface, a sequence item, sequences for reset, fill, empty, concurrent read and write and edge cases, a driver, a monitor, an agent, an environment with a scoreboard and coverage, and a test.

The verification plan lists each feature with a goal, and every row is checked with a concurrent assertion. The features are write, read and end to end data integrity, pointer increments and wraparound, Gray conversion, both pointer synchronizations, the full and empty flags, reset in each domain, back to back operations, different clock ratios, and full to empty transitions. The core rules are no writes when full and no reads when empty.

Here are assertions in that style. They are sketches of the idea, not the repo's exact code.

```systemverilog
// a Gray pointer changes by at most one bit per clock
ap_gray_w: assert property (@(posedge w_clk) disable iff (!w_rstn)
  $onehot0(gray_w_ptr ^ $past(gray_w_ptr)));

// a write attempted while full must not move the write pointer
ap_no_wr_full: assert property (@(posedge w_clk) disable iff (!w_rstn)
  (o_full && i_w_en) |=> $stable(w_ptr));

// a read attempted while empty must not move the read pointer
ap_no_rd_empty: assert property (@(posedge r_clk) disable iff (!r_rstn)
  (o_empty && i_r_en) |=> $stable(rd_ptr));

// after a write domain reset, the pointers are zero
ap_w_reset: assert property (@(posedge w_clk) !w_rstn |=> (w_ptr == 0 && gray_w_ptr == 0));
```

### Traps to watch for

- Synchronizing a bus bit by bit.
- Combinational logic right before a synchronizer.
- Two separately synchronized signals recombined downstream.
- Trusting a clean zero delay simulation, which never shows metastability unless delays are injected.

### Practice

1. In one sentence, what is metastability?
2. Using the MTBF formula, what happens to MTBF if S doubles? What if fC doubles while S stays fixed?
3. Recompute the slide's MTBF for S = 0.5 ns with the same τ, TW, fC and fD. Give the answer in years.
4. Why is a two flop synchronizer fine for a single enable bit but wrong for an 8 bit counter value?
5. Write the 3 bit Gray code sequence from 0 to 7. How many bits change between each pair, including 7 back to 0?
6. A pulse in a 500 MHz domain is one cycle wide and crosses into a 100 MHz domain. Will it be seen reliably? What should the source do?
7. Write an assertion that w2r\_ptr, the write pointer as seen in the read domain, changes by at most one bit per read clock.

### Answers

1. A flip flop caught between 0 and 1 for an unpredictable time because its input changed inside the setup and hold window.
2. Doubling S squares the e^(S/τ) term, so MTBF grows enormously. Doubling fC halves MTBF if S is unchanged, though in practice a faster clock also shrinks S.
3. S/τ = 500 ps / 10 ps = 50, and e^50 is about 5.2 × 10^21. Dividing by 2 × 10^6 gives about 2.6 × 10^15 seconds, which is about 8 × 10^7 years.
4. Each bit can resolve on a different cycle, so the counter can briefly read a value that never existed. Use Gray code, a handshake or a FIFO.
5. 000, 001, 011, 010, 110, 111, 101, 100, then back to 000. Exactly one bit changes at every step, including the wrap.
6. No. The 2 ns pulse can fall between 10 ns receiving edges. Stretch it to at least 1.5 receiving periods, 15 ns, or use a handshake.
7. `assert property (@(posedge r_clk) disable iff (!r_rstn) $onehot0(w2r_ptr ^ $past(w2r_ptr)));`
