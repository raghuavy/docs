"""Plain-English pseudocode for every SystemVerilog block in the guide.

Keys are "L<section>-<n>": section L2 is Lecture 1, L3 is Lecture 2, and so on.
n counts the SystemVerilog blocks inside that section, in order.
"""

PSEUDO = {
# ---------------- Lecture 1. SystemVerilog Review ----------------
"L2-1": """
make two 4 bit variables, sum and q_out

whenever a or b changes:
    sum becomes a + b           (just an adder, nothing is stored)

at every rising clock edge:
    q_out takes the value of d  (real flip flops, the value is stored)
""",
"L2-2": """
b is an 8 bit number that can be negative
d is a 32 bit number that can never be negative
""",
"L2-3": """
define a record type with fields:
    a, b, c   single bits
    d, e, f   integers
    g, h      4 bit values

make v of that type, filling the fields in order:
    0, 1, 0, 5, 6, 7, A, B

print field g of v      ->  a
""",
"L2-4": """
one 4 bit storage spot that can be read two ways:
    u reads it as unsigned
    s reads it as signed

store 1101 through u
print it both ways      ->  s shows -3, u shows 13
""",
"L2-5": """
arr   a 16 by 8 by 4 grid of integers
arr2  the same grid, written with explicit index ranges
b     2 rows of 4: row 0 is all 0, row 1 is all 1
c     8 integers, every one equal to 5
d     8 integers, every one set to 0 by default
""",
"L2-6": """
m is a grid with 2 rows and 3 columns

for every row i and column j of m:
    m[i][j] = i * 3 + j        (fills in 0, 1, 2, 3, 4, 5)
""",
"L2-7": """
state_t may only be IDLE, BUSY or DONE   (stored as 0, 1, 2)
color_t is 2 bits and may only be RED (01) or GREEN (10)
""",
"L2-8": """
whenever any input changes:
    if select is 1:  mux_out = in1
    otherwise:       mux_out = in0

at a rising clk, or the moment rst goes low:
    if rst is low:   q = 0
    otherwise:       q = d

while clk is high:
    q_lat follows d   (and holds still while clk is low)
""",
"L2-9": """
function max2(a, b):
    if a > b:
        give back a and stop
    give back b
""",
"L2-10": """
word is 32 bits, seen as four bytes [3] [2] [1] [0]

set all 32 bits to DEADBEEF
clear byte 0, the lowest byte
clear the top bit of byte 3
set bytes 2 and 1 together to 1234
""",

# ---------------- Lecture 2. OOP ----------------
"L3-1": """
blueprint "simple" holds address, data and check, 16 bits each

    set_check:  check = address XOR data
    print:      show all three in hex
""",
"L3-2": """
s is a handle that points at nothing yet (null)
build an object and point s at it
set address to abcd and data to 1234
compute the check value       ->  b9f9
print everything

t: declare a handle and build its object in one line
""",
"L3-3": """
base class:
    show(): print "BASE" and the time

extd, a child of base:
    show(): print "EXTD" and the time
            then also run the parent's show()
""",
"L3-4": """
every counter object shares ONE count, starting at 0
building an object adds 1 to that shared count

build c1, build c2
print counter::count          ->  2
""",
"L3-5": """
class demo has its own x

set(x) receives an argument that is also called x:
    this.x   (the object's x)   =   x   (the argument)
""",
"L3-6": """
inside the class: promise a task called report

outside the class, write its body:
    print the current time
""",
"L3-7": """
arr holds 5 handles, all empty at first

for each slot:
    build a new object and store its handle there
""",
"L3-8": """
inner holds a number x
outer holds a handle org, pointing to its own inner object

copy():
    build a brand new outer   (it gets a brand new inner too)
    copy the number x into that new inner
    give back the new outer

make dup1 and set its x to 8
dup2 = dup1.copy()
change dup1's x to 6
print both                    ->  6 and 8, nothing is shared
""",
"L3-9": """
copy():
    build a new A
    copy x across
    build a new B for it
    copy y across
    give back the new A
""",

# ---------------- Lecture 3. Randomization ----------------
"L4-1": """
repeat 3 times:
    q = a random number from 1 to 10
    print q
""",
"L4-2": """
pick ONE line at random, using weights out of 10:
    statement1   1 in 10
    statement2   4 in 10
    statement3   5 in 10
""",
"L4-3": """
class example has one random integer

build one object
repeat 10 times:
    try to randomize it
    if that worked:  print the value
    otherwise:       print "randomize failure"
""",
"L4-4": """
class small_class has a random integer x

rule allowed_x:
    x is bigger than 0
    x is smaller than 10
""",
"L4-5": """
large_class is a child of small_class
its rule has the SAME name, so it replaces the parent's rule:
    x is between 10 and 20

build a small_class object s
randomize s, adding one extra rule for this call only:  x > 5
    ->  x ends up between 6 and 9
""",
"L4-6": """
len is a random 8 bit number

rule: len must be one of
    1, 2, 4, or anything from 64 to 127
""",
"L4-7": """
line 1:  100 weight 1,  200 weight 2,  400 weight 4

line 2 (:=  every value in a range gets the full weight)
         100 weight 1,  200 weight 4,  201 weight 4

line 3 (:/  a range shares its weight)
         100 weight 1,  200 weight 2,  201 weight 2
""",
"L4-8": """
b, c and d are random 16 bit numbers

all of these must be true at the same time:
    b < d
    c equals b
    d < 30
    c > 25

->  b and c land on 26, 27 or 28
->  d lands on 27, 28 or 29
""",
"L4-9": """
slow version:
    addr divided by 4096 leaves a remainder within 20 of either end
    (the solver has to do a division)

fast version, same meaning:
    the low 12 bits of addr are within 20 of either end
    (no division, just look at bits)
""",
"L4-10": """
x is a random bit, y is a random number from 0 to 3

rule: if x is 0, then y must be 0
choose x first, then y

->  x is 0 half the time and 1 half the time
->  y is 0 with probability 1/2 + 1/8 = 5/8
""",

# ---------------- Lecture 4. Functional Coverage Basics ----------------
"L5-1": """
covergroup grp:
    watch x, and call this watcher cpx in the report

build one copy of it, named grp1
""",
"L5-2": """
x is 4 bits. The test values are 10, 11, 12, 14

covergroup grp:
    watch x as cpx, with at most 8 automatic bins (2 values per bin)

for each test value:
    x = that value
    take a coverage snapshot

->  bins [10:11], [12:13], [14:15] are hit
->  3 of 8 bins covered
""",
"L5-3": """
watch x with three named bins:
    low    0 to 3
    mid    4, 5, 6, 7
    high   8 to 15
""",
"L5-4": """
the values arrive in this order: 7, 8, 9, 7

bin from_7_to_9   hit only if 9 comes RIGHT after 7
bin from_9_to_7   hit only if 7 comes RIGHT after 9

->  9 then 7 happens, 7 then 9 never does
->  1 of 2 bins covered
""",
"L5-5": """
the values are 4, 8, 10, 12

ignore 12, 13, 14 and 15 completely
->  12 automatic bins remain, and 4, 8, 10 hit 3 of them
""",
"L5-6": """
covergroup grp:
    watch x as cpx
    watch y as cpy
    cpxy: watch every (x bin, y bin) pair
""",
"L5-7": """
covergroup DrivingGroup takes a snapshot of speed at every rising clk

build dg, which starts collecting right away
turn collecting OFF
wait until reset ends (rst falls)
turn collecting back ON
""",
"L5-8": """
watch data, but only on snapshots where OK is true
""",
"L5-9": """
at every rising clk, but only when valid is 1:
    look at opcode and sort it into a bin
        zero    0
        low     1 to 7
        high    8 to 15
""",

# ---------------- Lecture 5. The Interface Construct ----------------
"L6-1": """
interface arb_if: one bundle holding grant, request and rst
                  the clock comes in from outside

DUT arb, at a rising clk or a rising rst:
    if rst:                    grant = 00
    else if request bit 0:     grant = 01
    else if request bit 1:     grant = 10
    else:                      grant = 00

top:
    make a clock that flips every 5 time units
    make ONE bundle called arbif
    plug the DUT and the testbench into that same bundle
""",
"L6-2": """
the old DUT has normal ports, so connect each port
by pulling the matching wire out of the bundle by name
""",
"L6-3": """
same bundle as before, plus three named views:
    TEST     may drive request and rst, may only read grant and clk
    DUT      reads request, rst, clk and drives grant
    MONITOR  reads everything and drives nothing

the DUT module takes the DUT view
""",
"L6-4": """
same bundle, plus a clocking block cb tied to the rising clk:
    request is DRIVEN at the clock edge
    grant is SAMPLED at the clock edge

TEST view: go through cb, and drive rst directly (not clocked)
DUT view:  unchanged
""",
"L6-5": """
the testbench uses the TEST view

at the next clock edge, drive request = 01
wait for the next clock edge
print grant, as sampled at that edge
""",
"L6-6": """
bus_if bundles valid, ready and an 8 bit data, clock comes in

clocking block cb on the rising clk:
    drive valid and data
    sample ready

master view: goes through cb
slave view:  reads valid, data and clk, drives ready
""",

# ---------------- Lectures 6 and 7. Threads ----------------
"L7-1": """
print "start" at time 0

start two threads side by side:
    A: wait 10, print "A"
    B: wait 20, print "B"
carry on as soon as EITHER one finishes   (join_any)

print "after fork"        ->  at time 10
(B still prints later, at time 20)
""",
"L7-2": """
driver.run(): forever
    get a transaction
    drive it on the pins

environment.run():
    start gen.run() and drv.run() side by side
    do not wait for them   (join_none)
""",
"L7-3": """
for j = 0, 1, 2:
    queue up a thread that will print j   (it does not run yet)

the loop finishes, so j is now 3
wait a moment, the threads finally run   ->  each prints 3
""",
"L7-4": """
for j = 0, 1, 2:
    queue up a thread with its OWN private copy k = j
    that thread prints k

->  prints 0 1 2
""",
"L7-5": """
start two threads:
    one waits for bus.done
    one waits 1000 time units, then reports a timeout
carry on when the first one finishes
kill whichever is still running
""",
"L7-6": """
start two threads together at time 0:
    thread 1: wait 5, then wait for eventA's "triggered" flag
    thread 2: trigger eventA right now, at time 0

the flag only stays up during time 0
->  at time 5 thread 1 waits forever
""",
"L7-7": """
the room has 1 key

use_room(id):
    take the key   (wait here if someone else has it)
    print that this id got the key
    stay for 15 time units
    give the key back
""",
"L7-8": """
the generator has a mailbox that only accepts Transactions

run(n): repeat n times
    build a BRAND NEW Transaction
    randomize it
    put its handle in the mailbox
""",
"L7-9": """
producer: for i = 1, 2, 3
    put i in the mailbox
    wait until the consumer says it is done   (handshake)

consumer: forever
    take a value out   (wait if the mailbox is empty)
    print it
    trigger handshake
""",
"L7-10": """
race two threads:
    one waits for event done, then prints "done first"
    one waits 500 time units, then prints "timeout first"
carry on when either one finishes
kill the other one
""",

# ---------------- Lecture 8. UVM ----------------
"L8-1": """
my_driver is a UVM driver that handles my_txn items
register it with the factory
keep a handle vif to the interface

new: hand the name and parent up to the UVM base class

build phase:
    look up "dut_vi" in the config database, store it in vif
    if it is not there, stop with a fatal error

run phase, forever:
    wait for the next item from the sequencer
    wait for a rising clock edge
    put item.a and item.b on the pins
    tell the sequencer this item is done
""",
"L8-2": """
my_txn is ONE transaction: random a and b, 4 bits each
register it with the factory
new: give it a name
""",
"L8-3": """
my_seq produces my_txn items

body, repeat 10 times:
    create an item through the factory
    wait until the driver is ready for it
    randomize it   (report an error if that fails)
    hand it over and wait until the driver finishes it
""",
"L8-4": """
my_test

build phase:
    create the environment

run phase:
    create the sequence
    raise an objection          (keep the simulation alive)
    run the sequence on the agent's sequencer, wait until it ends
    drop the objection          (now it is ok to finish)
""",
"L8-5": """
top module:
    bring in the UVM library and its macros
    make a clock that flips every 5
    make the interface and connect the DUT to it

    at time 0:
        store the interface in the config database
            name "dut_vi", visible only to the test
        start the test called my_test
""",
"L8-6": """
connect phase:
    plug the driver's request port into the sequencer
""",

# ---------------- Lectures 9 to 11. Advanced OOP ----------------
"L9-1": """
Transaction holds random src, dst and 8 data words, plus csm

calc_csm (children may replace it):
    csm = src XOR dst XOR every data word

display (children may replace it):
    print src, dst and csm
""",
"L9-2": """
BadTr is a Transaction plus one random bit, bad_csm

calc_csm:
    compute the normal checksum (the parent's version)
    if bad_csm is 1, flip every bit of csm   (a deliberate error)

display:
    print bad_csm, then run the parent's display
""",
"L9-3": """
the Generator holds a mailbox and ONE blueprint object

new:
    remember the mailbox
    build a plain Transaction as the default blueprint

run(n), repeat n times:
    randomize the blueprint
    put a COPY of it in the mailbox   (never the blueprint itself)
""",
"L9-4": """
build the environment

build a BadTr and make it the generator's blueprint

run the environment
wrap up
""",
"L9-5": """
tr is a Transaction handle, bad and b2 are BadTr handles

build a BadTr in bad
tr = bad                       (always allowed: child into parent)

$cast(b2, tr) as a task:       error if tr is not really a BadTr

if $cast(b2, tr) succeeds:
    print b2.bad_csm
otherwise:
    say "tr is not a BadTr"
""",
"L9-6": """
Transaction.copy(to):
    if no target was given, build a new Transaction, else use the target
    copy src, dst, data and csm into it
    give it back

BadTr.copy(to):
    if no target was given, build a new BadTr, else cast the target to BadTr
    let the parent's copy fill in the shared fields
    copy bad_csm
    give it back
""",
"L9-7": """
BaseTr can never be built on its own
    count is shared by every object, id belongs to each object

every child class MUST write its own:
    compare, copy, display
""",
"L9-8": """
Driver_cbs: two hooks, pre_tx and post_tx, that do nothing by default

Driver keeps a list of callback objects
run, forever:
    drop = no
    get a transaction
    let every callback look at it first   (it may set drop)
    if not dropped, send it
    let every callback look at it after

Driver_cbs_drop:
    pre_tx: set drop with a 1 in 100 chance
""",
"L9-9": """
Stack of some type T   (int if nobody says otherwise)
    100 private slots and a private position counter
    push(i): put i at the position, move the position up
    pop():   move the position down, give back that item

int_stack holds ints, real_stack holds real numbers
""",
"L9-10": """
Driver_cbs_delay:
    pre_tx: wait a random 0 to 10 time units before sending
""",

# ---------------- Lecture 10. Assertions Basics ----------------
"L10-1": """
at every rising clk:
    a must be different from b
""",
"L10-2": """
at every rising clk:
    if req:                     restart count at 1
    else if count is running:   add 1
    if count is 4 and grant is low:
        report "no grant"

problem: a second req restarts the count,
         so the first request is forgotten
""",
"L10-3": """
at every rising clk where req is high:
    start a separate check: grant must be high 4 clocks later
""",
"L10-4": """
register q, at a rising clk or a rising rst:
    if rst:       q = all 0
    else if set:  q = all 1
    else:         rotate q left by one bit

check_shift (switched off during reset):
    if set was low, then next clock
    q must equal last clock's q rotated left

check_rst (checked after values settle):
    if rst is high, q must be 0
""",
"L10-5": """
at every rising clk:
    check that grant is NOT high while req is low
    if it is, print an error with the time
""",

# ---------------- Lecture 12. UVM Adder Example ----------------
"L11-1": """
adder_if bundles:
    a and b   4 bits each
    sum       5 bits, so the carry out fits
""",
"L11-2": """
full_adder:
    sum       = a XOR b XOR carry_in
    carry_out = 1 when at least two of a, b, carry_in are 1

adder: chain four full adders
    bit 0 gets carry_in 0
    each next bit takes the previous bit's carry_out
    the last carry_out becomes sum bit 4
""",
"L11-3": """
adder_item: random a and b, plus sum

do_copy(rhs):
    turn the general handle into an adder_item handle
        (report an error and stop if that is impossible)
    copy the parent's fields
    copy a, b and sum

convert2string:
    give back text like "A=3, B=4 | Sum=7"
""",
"L11-4": """
body, repeat 10 times:
    create an item
    wait for the driver to be ready
    randomize it   (error if that fails)
    send it
""",
"L11-5": """
forever:
    take the next item
    put a and b on the pins
    wait 10 time units for the adder to settle
    report done
""",
"L11-6": """
item_collected_port: a broadcast port, built in new

forever:
    wait 10 time units
    create a fresh item
    copy a, b and sum off the pins
    broadcast it to every listener
""",
"L11-7": """
whenever the monitor broadcasts an item t:
    make a copy of t       (never change the original)
    expected sum = a + b
    send the copy to the scoreboard
""",
"L11-8": """
two separate inputs:
    actual     from the monitor
    expected   from the predictor
two queues to hold them

new: build both inputs

write_actual(item):    add it to the actual queue, then try to compare
write_expected(item):  add it to the expected queue, then try to compare

compare:
    if both queues have something:
        take the oldest item from each
        if the sums match exactly:  report MATCH
        otherwise:                  report MISMATCH as an error
""",
"L11-9": """
top:
    make the interface and connect the adder to it
    store the interface in the config database for everyone ("*")
    start adder_test
""",
"L11-10": """
adder_cov listens to the monitor

covergroup:
    a sorted into 4 bins
    b sorted into 4 bins
    every (a bin, b bin) pair, 16 in all

new:       build the covergroup
write(t):  remember t, take a coverage snapshot
""",

# ---------------- Lecture 12. Advanced Interfaces ----------------
"L12-1": """
Rx_if bundles data (8 bits), soc, en, clav, rclk. Clock comes in.

clocking block on the rising clk:
    the testbench drives data, soc and clav
    the testbench samples en

DUT view: drives en and rclk, reads data, soc and clav
TB view:  goes through the clocking block
""",
"L12-2": """
top:
    4 receive bundles and 4 transmit bundles, all on clk
    plug every bundle into the testbench AND into the router
    clock flips every 20 time units
""",
"L12-3": """
the test receives 8 real bundles through its ports

make 4 driver slots and 4 monitor slots
vRx = handles to Rx0, Rx1, Rx2, Rx3
vTx = handles to Tx0, Tx1, Tx2, Tx3

for i = 0 to 3:
    driver i  gets handle vRx[i]
    monitor i gets handle vTx[i]
""",
"L12-4": """
vTx_t is a short name for "handle to a transmit bundle, TB view"

Monitor stores one such handle, given to it in new

receive_cell:
    say "ready" (clav = 1)
    wait for a clock edge where soc is 1
    then read the data bytes one by one
""",
"L12-5": """
the test has no ports at all

reach into top and grab arbif by its path   (top.arbif)
drive request = 0 at the next edge
wait one clock
""",
"L12-6": """
NUM_XI = 2 counters
the clock flips every 20

make 2 bundles and the test
for i = 0 to 1:
    place counter i on bundle i
""",
"L12-7": """
one handle per counter bundle

copy all of top's bundles into the handle array
make NUM_XI drivers
driver i gets bundle i and its own number i
""",
"L12-8": """
Driver keeps a handle rx, given to it in new

send_byte(b):
    at the next edge, drive data = b and soc = 1
    wait one clock
    drive soc = 0
""",

# ---------------- Lectures 13 and 14. Coverage in Depth ----------------
"L13-1": """
if the command line has +ntb_random_seed=N:
    read N into seed
    print "Running with seed N"
""",
"L13-2": """
Transaction: random 32 bit data and random 3 bit dst

covergroup CovDst watches tr.dst

build the covergroup
repeat 32 times:
    build a new transaction
    randomize it
    take a coverage snapshot

->  after 32: 7 of 8 dst values seen
->  after 33: all 8 seen
""",
"L13-3": """
for this whole group: at most 2 automatic bins per watcher

watch tr.dst             ->  bins [0:3] and [4:7]
watch low 4 bits of data ->  2 bins of 8 values each
""",
"L13-4": """
len16: watch hdr_len + payload_len
       done in 4 bit math, so sums above 15 wrap around

len32: the same sum plus a 5 bit zero
       done in 5 bit math, so nothing wraps
""",
"L13-5": """
watch kind (4 bits) with these bins:
    zero    just 0
    lo      ONE bin for 1, 2, 3 and 5
    hi[]    a SEPARATE bin for each of 8 to 15
    misc    everything else (not counted in the score)
""",
"L13-6": """
option 1: watch port only while reset is low

option 2, from the test:
    stop collecting
    wait for reset to fall
    start collecting again
""",
"L13-7": """
even:  any value whose last bit is 0
odd:   any value whose last bit is 1
""",
"L13-8": """
port:  one bin per port value
kind:  zero, lo (1 to 3), one bin for each of 8 to 15, misc

watch every (kind, port) pair, but skip:
    every pair where port is 7
    pairs where port is 0 and kind is 9, 10 or 11
    every pair where kind is in lo
""",
"L13-9": """
version 1, a cross:
    a and b each have two bins and do not count on their own
    count only three pairs:
        a is 0 and b is 0
        a is 1 and b is 0
        b is 1, whatever a is

version 2, one watcher on the 2 bit value {a, b}:
    00,  10,  and any value ending in 1
""",
"L13-10": """
watch opcode:
    zero   0
    low[]  1, 2 and 3, each its own bin
    even   4, 6, 8, 10, 12, 14
    bad    15 is illegal, an error if it ever shows up
""",

# ---------------- Lectures 14 to 16. Advanced Assertions ----------------
"L14-1": """
p_counter_inc   (off during reset)
    if inc, then count = last clock's count + 1

p_handshake
    when request rises, grant within 1 to 4 clocks

p_req_drop   (off during rst)
    one clock after ack, req has just fallen

p_data_stable
    if valid and not ready, then next clock
    valid is still high and data has not changed

at most 2 bits of gnt_bus are high

cmd_bus never contains X or Z   (off during reset)
    if it does, print an error with the time and the value

exactly one bit of grant is high
at most one bit of grant is high
""",
"L14-2": """
whenever a or b changes:
    a must not be high while b is low
    otherwise report "a1 failed"
""",
"L14-3": """
sequence s_req_ack:
    req, then ack 1 or 2 clocks later

property p_req_ack   (off during rst):
    whenever start is high, s_req_ack must follow

assert the property every clock
""",
"L14-4": """
count how many times req is followed by ack 1 or 2 clocks later
""",

# ---------------- Lectures 16 to 18. SVA ----------------
"L15-1": """
at each rising clk where req is high:
    ack must be high on the next clock
    if it passes:  print "pass"
    if it fails:   error "ack missing"
""",
"L15-2": """
s_hs(req, ack, n):
    req, then ack n clocks later

p_hs(clk, req, ack):
    on rising clk, when req rises, s_hs with n = 2 must follow

check it twice:
    bus 0 with req0 and ack0
    bus 1 with req1 and ack1
""",
"L15-3": """
the default clock for everything here is the rising clk

ap1: uses the default clock
     req means ack on the next clock

ap2: overrides it with clk2
     start means done 2 clocks later
""",
"L15-4": """
only when req RISES:
    ack must come within 1 to 3 clocks
""",
"L15-5": """
failmsg(msg): report an error with the time and msg

ap_x: bus never contains X
      if it does, report it with failmsg
""",
"L15-6": """
a separate checker module with two rules   (off during rst):
    if full, then no push
    if empty, then no pop

attach this checker to every fifo in the design,
wiring its pins to the fifo's signals by name
""",
"L15-7": """
"s2 four times in a row" is just shorthand for
writing s2 four times, one clock apart
""",
"L15-8": """
goto form [->3]:
    after start rises, done comes EXACTLY one clock after the 3rd b

nonconsecutive form [=3]:
    done comes any time after the 3rd b,
    as long as no 4th b shows up first
""",

# ---------------- Lecture 19. Clock Domain Crossing ----------------
"L16-1": """
at a rising dst_clk, or when rst_n goes low:
    if in reset:
        clear both flops
    else:
        meta   takes d_async       (may go metastable)
        q_sync takes the old meta  (had a full clock to settle)

->  q_sync is d_async, two clocks later, safe to use
""",
"L16-2": """
gray_w_ptr: at most one bit changes per write clock

write while full:   the write pointer does not move next clock
read while empty:   the read pointer does not move next clock

after a write side reset: both write pointers are 0
""",
}
