"""LeetCode style problem metadata for the practice questions.

The question text and the written solution come from the guide markdown.
This file adds a short title and an answer check for each question, in order.

Check types
  fields   one or more short answers. Each field has a label "l" and accepted answers "a".
           Numbers are compared with a tolerance ("tol", absolute). "pct" means the number is a
           percent and 0.1875 or 18.75 are both fine. "opt" turns the field into a dropdown.
           "list" compares comma or space separated lists.
  choice   one correct option, index "a"
  multi    select every correct option, indices "a"
  order    type tokens in the right order
  custom   checked by a JavaScript function named in "fn"
  code     editor, then compare with the reference solution and mark it yourself
  explain  same as code, for answers in words
"""

YES_NO = ["yes", "no"]

PROBLEMS = {
"L2": [
    ("Which types can hold X", {"t": "multi", "o": ["bit", "logic", "int", "integer"], "a": [1, 3]}),
    ("Pre and post increment", {"t": "fields", "f": [
        {"l": "After n = k++, n is", "a": [5]}, {"l": "After n = k++, k is", "a": [6]},
        {"l": "After n = ++k, n is", "a": [6]}, {"l": "After n = ++k, k is", "a": [6]}]}),
    ("int unsigned", {"t": "fields", "f": [
        {"l": "Width in bits", "a": [32]}, {"l": "Can it be negative?", "opt": YES_NO, "a": ["no"]}]}),
    ("foreach over a 2D array", {"t": "code"}),
    ("Signed view of a union", {"t": "fields", "f": [{"l": "s reads", "a": [-2]}]}),
    ("Packed struct layout", {"t": "fields", "f": [
        {"l": "Total width in bits", "a": [13]},
        {"l": "Bit range that holds a", "a": ["[12:9]", "12:9", "12to9", "12-9", "bits12to9"]}]}),
    ("always_comb with no else", {"t": "choice", "o": ["plain combinational logic", "a flip flop", "a latch", "nothing, it is removed"], "a": 2}),
],
"L3": [
    ("Class, object and handle", {"t": "explain"}),
    ("Using a handle before new", {"t": "choice", "o": ["data becomes 5", "a compile error", "a null handle error at run time", "nothing happens"], "a": 2}),
    ("Static counter", {"t": "fields", "f": [{"l": "count reads", "a": [3]}]}),
    ("Copying a handle", {"t": "fields", "f": [{"l": "a1.x reads", "a": [6]}]}),
    ("Shallow copy, plain field", {"t": "fields", "f": [{"l": "a1.x reads", "a": [8]}]}),
    ("Shallow copy, nested object", {"t": "fields", "f": [{"l": "a1.b.y reads", "a": [9]}]}),
    ("Write a deep copy", {"t": "code"}),
],
"L4": [
    ("$urandom_range with one argument", {"t": "fields", "f": [{"l": "Smallest value", "a": [0]}, {"l": "Largest value", "a": [10]}]}),
    ("randcase weights", {"t": "fields", "f": [
        {"l": "Chance of the weight 2 branch", "a": [0.2], "tol": 0.002},
        {"l": "Chance of the weight 3 branch", "a": [0.3], "tol": 0.002},
        {"l": "Chance of the weight 5 branch", "a": [0.5], "tol": 0.002}]}),
    ("randc on 2 bits", {"t": "fields", "f": [{"l": "Distinct values in 4 calls", "a": [4]}]}),
    ("dist with :=", {"t": "fields", "f": [
        {"l": "Chance that x is 0", "a": [1 / 7], "tol": 0.002},
        {"l": "Chance that x is 1", "a": [2 / 7], "tol": 0.002}]}),
    ("dist with :/", {"t": "fields", "f": [
        {"l": "Chance that x is 0", "a": [1 / 3], "tol": 0.002},
        {"l": "Chance that x is 1", "a": [2 / 9], "tol": 0.002}]}),
    ("Constraints solved together", {"t": "fields", "f": [{"l": "a", "a": [2]}, {"l": "b", "a": [3]}]}),
    ("Efficient address constraint", {"t": "code"}),
    ("solve before probability", {"t": "fields", "f": [
        {"l": "P(x = 1) with no solve before", "a": [1 / 9], "tol": 0.002},
        {"l": "P(x = 1) with solve x before y", "a": [0.5], "tol": 0.002}]}),
],
"L5": [
    ("Default bins on 3 bits", {"t": "fields", "f": [{"l": "Number of bins", "a": [8]}]}),
    ("auto_bin_max on 8 bits", {"t": "fields", "f": [{"l": "Values per bin", "a": [16]}]}),
    ("Coverage from four samples", {"t": "fields", "f": [{"l": "Coverage, percent", "a": [18.75], "pct": True, "tol": 0.1}]}),
    ("Back to back transition", {"t": "fields", "f": [{"l": "Is (3 => 4) hit?", "opt": YES_NO, "a": ["yes"]}]}),
    ("Coverage with ignore_bins", {"t": "fields", "f": [{"l": "Coverage, percent", "a": [100 * 2 / 14], "pct": True, "tol": 0.1}]}),
    ("Cross of two 2 bit points", {"t": "fields", "f": [
        {"l": "Number of cross bins", "a": [16]}, {"l": "Cross coverage, percent", "a": [12.5], "pct": True, "tol": 0.1}]}),
    ("Write a filtered covergroup", {"t": "code"}),
],
"L6": [
    ("Layers of a testbench", {"t": "fields", "f": [
        {"l": "A driver is in the", "opt": ["signal layer", "command layer", "functional layer", "scenario layer", "test layer"], "a": ["command layer"]},
        {"l": "A scoreboard is in the", "opt": ["signal layer", "command layer", "functional layer", "scenario layer", "test layer"], "a": ["functional layer"]}]}),
    ("Why rst sits outside the clocking block", {"t": "choice", "o": [
        "clocking blocks cannot hold 1 bit signals",
        "rst is asynchronous, so it should not wait for a clock edge",
        "rst is only read by the DUT",
        "it is a style choice with no effect"], "a": 1}),
    ("Write bus_if with modports", {"t": "code"}),
    ("Drive and wait through the clocking block", {"t": "code"}),
    ("Wrong modport on the DUT", {"t": "choice", "o": [
        "it works, modports are only comments",
        "a null error at run time",
        "it fails to compile because grant is read only in the TEST view, so use arb_if.DUT",
        "grant is driven twice"], "a": 2}),
    ("Add a clocking block", {"t": "code"}),
],
"L7": [
    ("When does the parent continue", {"t": "fields", "f": [
        {"l": "With join, time", "a": [15]}, {"l": "With join_any, time", "a": [5]}, {"l": "With join_none, time", "a": [0]}]}),
    ("The loop variable bug", {"t": "fields", "f": [{"l": "What it prints", "a": ["333"]}]}),
    ("Edge versus level wait", {"t": "fields", "f": [
        {"l": "Does @e wake up?", "opt": YES_NO, "a": ["no"]},
        {"l": "Does wait (e.triggered) wake up?", "opt": YES_NO, "a": ["yes"]}]}),
    ("try_get with no free keys", {"t": "fields", "f": [{"l": "try_get returns", "a": [0]}]}),
    ("One object, five puts", {"t": "choice", "o": [
        "five different random transactions",
        "an empty mailbox",
        "five handles to the same object, so the last random values repeat",
        "a compile error"], "a": 2}),
    ("Race a timeout", {"t": "code"}),
],
"L8": [
    ("Components or objects", {"t": "multi", "q": "Select every component.", "o": ["driver", "sequence", "transaction", "environment", "scoreboard"], "a": [0, 3, 4]}),
    ("The phase that is a task", {"t": "choice", "o": ["build_phase", "connect_phase", "run_phase", "report_phase"], "a": 2}),
    ("Why type_id::create", {"t": "choice", "o": [
        "create runs faster than new",
        "the factory can swap in a different type through an override",
        "new cannot take a parent argument",
        "create also randomizes the object"], "a": 1}),
    ("Forgotten objection", {"t": "choice", "o": [
        "the test runs forever",
        "a compile error",
        "the run phase ends at time 0, so the sequence barely runs",
        "nothing changes"], "a": 2}),
    ("config_db scope", {"t": "fields", "f": [{"l": "Does the driver find it?", "opt": YES_NO, "a": ["no"]}]}),
    ("Why an analysis port", {"t": "choice", "o": [
        "write() never blocks and can feed many listeners at once",
        "put ports cannot carry transactions",
        "analysis ports compile faster",
        "only analysis ports can be connected in connect_phase"], "a": 0}),
    ("Connect driver to sequencer", {"t": "code"}),
],
"L9": [
    ("Upcast and downcast", {"t": "fields", "f": [
        {"l": "Transaction t = b;", "opt": ["legal", "compile error"], "a": ["legal"]},
        {"l": "BadTr b2 = t;", "opt": ["legal", "compile error"], "a": ["compile error"]}]}),
    ("Non virtual call", {"t": "choice", "o": ["Transaction::calc_csm", "BadTr::calc_csm"], "a": 0}),
    ("Virtual call", {"t": "choice", "o": ["Transaction::calc_csm", "BadTr::calc_csm"], "a": 1}),
    ("Reaching a child field", {"t": "choice", "o": [
        "yes, directly as tr.bad_csm",
        "only after $cast into a BadTr handle",
        "never, the field is gone"], "a": 1}),
    ("Why new is never virtual", {"t": "choice", "o": [
        "new returns void",
        "virtual methods cannot take arguments",
        "a virtual call checks the object's type, and before new finishes there is no object"], "a": 2}),
    ("Blueprint in the mailbox", {"t": "choice", "o": [
        "the mailbox overflows",
        "every entry is the same object, so the driver sees the last values repeated",
        "a compile error",
        "nothing goes wrong"], "a": 1}),
    ("Write a delay callback", {"t": "code"}),
],
"L10": [
    ("Never both high", {"t": "code"}),
    ("Read an implication", {"t": "choice", "o": [
        "req and ack must both stay high for 2 edges",
        "ack must be high within 2 edges after req",
        "whenever req is high at an edge, ack must be high exactly 2 edges later"], "a": 2}),
    ("|=> versus |-> ##1", {"t": "fields", "f": [{"l": "Same meaning?", "opt": YES_NO, "a": ["yes"]}]}),
    ("When must grant be high", {"t": "fields", "f": [
        {"l": "For the req at cycle 1, cycle", "a": [5]}, {"l": "For the req at cycle 3, cycle", "a": [7]}]}),
    ("Counter versus assertion", {"t": "fields", "f": [
        {"l": "The counter reports", "opt": ["nothing", "a failure"], "a": ["nothing"]},
        {"l": "The assertion reports", "opt": ["nothing", "a failure"], "a": ["a failure"]}]}),
    ("Counter increment assertion", {"t": "code"}),
],
"L11": [
    ("Why sum has 5 bits", {"t": "fields", "f": [
        {"l": "Largest sum of two 4 bit numbers", "a": [30]}, {"l": "Bits needed to hold it", "a": [5]}]}),
    ("Predict a sum", {"t": "fields", "f": [
        {"l": "sum in decimal", "a": [17]}, {"l": "sum in binary", "a": ["10001", "5'b10001", "b10001", "0b10001"]}]}),
    ("Why the monitor waits", {"t": "choice", "o": [
        "UVM requires a delay in every monitor",
        "the combinational adder needs time to settle after the inputs change",
        "to make the simulation slower to watch"], "a": 1}),
    ("Run the bug by hand", {"t": "fields", "f": [
        {"l": "DUT output for a = 2, b = 2", "a": [0]},
        {"l": "The scoreboard says", "opt": ["MATCH", "MISMATCH"], "a": ["MISMATCH"]}]}),
    ("Find an input the bug misses", {"t": "custom", "fn": "adder_bug", "f": [{"l": "a (0 to 15)"}, {"l": "b (0 to 15)"}]}),
    ("Why clone in the predictor", {"t": "choice", "o": [
        "clone() is faster than reading the fields",
        "write() is not allowed to change its argument",
        "the monitor's item also goes to the scoreboard, so changing it would make actual equal expected"], "a": 2}),
    ("Coverage subscriber", {"t": "code"}),
],
"L12": [
    ("Interface versus virtual interface", {"t": "choice", "o": [
        "they are the same thing",
        "an interface is the bundle of wires, a virtual interface is a handle that points to one",
        "a virtual interface has no clock"], "a": 1}),
    ("Unassigned virtual interface", {"t": "choice", "o": [
        "it silently drives nothing",
        "a compile error",
        "a null access error at run time"], "a": 2}),
    ("Array of virtual interfaces", {"t": "code"}),
    ("One class or four", {"t": "explain"}),
    ("XMR trade off", {"t": "explain"}),
    ("Write send_byte", {"t": "code"}),
],
"L13": [
    ("Same seed twice", {"t": "choice", "o": ["identical results", "different results"], "a": 0}),
    ("Kinds of code coverage", {"t": "multi", "q": "Select the four kinds of code coverage.", "o": ["line", "path", "functional", "toggle", "FSM", "assertion"], "a": [0, 1, 3, 4]}),
    ("auto_bin_max of 4", {"t": "fields", "f": [{"l": "The bins", "a": ["0:1,2:3,4:5,6:7"], "list": True}]}),
    ("A sum that wraps", {"t": "fields", "f": [{"l": "Number of automatic bins", "a": [8]}]}),
    ("Counting named bins", {"t": "fields", "f": [{"l": "Total bins", "a": [5]}]}),
    ("Trim a cross", {"t": "fields", "f": [{"l": "Cross bins at first", "a": [32]}, {"l": "Cross bins left", "a": [24]}]}),
    ("Wildcard bins", {"t": "code"}),
],
"L14": [
    ("Severity levels", {"t": "fields", "f": [
        {"l": "Stops the simulation", "opt": ["$fatal", "$error", "$warning", "$info"], "a": ["$fatal"]},
        {"l": "Default for a failed assertion", "opt": ["$fatal", "$error", "$warning", "$info"], "a": ["$error"]}]}),
    ("$assertoff versus $assertkill", {"t": "choice", "o": [
        "they do the same thing",
        "$assertoff lets checks already running finish, $assertkill stops them too",
        "$assertkill only stops new checks"], "a": 1}),
    ("onehot of zero", {"t": "fields", "f": [
        {"l": "$onehot(8'b0)", "opt": ["true", "false"], "a": ["false"]},
        {"l": "$onehot0(8'b0)", "opt": ["true", "false"], "a": ["true"]}]}),
    ("Old or new value", {"t": "choice", "o": ["the old q", "the new q"], "a": 0}),
    ("Order the regions", {"t": "order", "tok": ["preponed", "active", "nba", "observed", "reactive", "postponed"]}),
    ("Assert and cover a handshake", {"t": "code"}),
    ("Short circuit", {"t": "choice", "o": [
        "check runs twice",
        "assertions are not allowed in functions",
        "when v is 0, && never calls check, so its assertion never runs"], "a": 2}),
],
"L15": [
    ("Rewrite |=>", {"t": "fields", "f": [{"l": "a |=> b is the same as", "a": ["a|->##1b"]}]}),
    ("How many checks start", {"t": "fields", "f": [
        {"l": "Checks started by req |-> ##2 ack", "a": [4]},
        {"l": "Checks started by $rose(req) |-> ##2 ack", "a": [1]}]}),
    ("Use a repetition operator", {"t": "fields", "f": [{"l": "Shorter form", "a": ["a[*3]##1b"]}]}),
    ("Goto and nonconsecutive, done at 10", {"t": "fields", "f": [
        {"l": "b[->3] ##1 done matches?", "opt": YES_NO, "a": ["yes"]},
        {"l": "b[=3] ##1 done matches?", "opt": YES_NO, "a": ["yes"]}]}),
    ("Goto and nonconsecutive, done at 12", {"t": "fields", "f": [
        {"l": "b[->3] ##1 done matches?", "opt": YES_NO, "a": ["no"]},
        {"l": "b[=3] ##1 done matches?", "opt": YES_NO, "a": ["yes"]}]}),
    ("and versus intersect", {"t": "fields", "f": [
        {"l": "s1 and s2 can match?", "opt": YES_NO, "a": ["yes"]},
        {"l": "s1 intersect s2 can match?", "opt": YES_NO, "a": ["no"]}]}),
    ("throughout", {"t": "code"}),
    ("Write a bind", {"t": "code"}),
],
"L16": [
    ("Metastability in a sentence", {"t": "explain"}),
    ("MTBF trends", {"t": "fields", "f": [
        {"l": "If S doubles, MTBF", "opt": ["halves", "doubles", "grows enormously"], "a": ["grows enormously"]},
        {"l": "If fC doubles with S fixed, MTBF", "opt": ["halves", "doubles", "grows enormously"], "a": ["halves"]}]}),
    ("Recompute MTBF", {"t": "fields", "f": [{"l": "MTBF in years (for example 3e5)", "a": [8.2e7], "tol": 1.2e7}]}),
    ("Why not synchronize a bus bit by bit", {"t": "choice", "o": [
        "two flops cannot hold 8 bits",
        "each bit can resolve on a different cycle, so the value can briefly be one that never existed",
        "the counter would count too slowly"], "a": 1}),
    ("Gray code", {"t": "fields", "f": [
        {"l": "The 8 codes, in order", "a": ["000,001,011,010,110,111,101,100"], "list": True},
        {"l": "Bits that change per step", "a": [1]}]}),
    ("Fast pulse into a slow clock", {"t": "fields", "f": [
        {"l": "Seen reliably?", "opt": YES_NO, "a": ["no"]},
        {"l": "Minimum safe width in ns", "a": [15], "tol": 0.5}]}),
    ("Gray pointer assertion", {"t": "code"}),
],
}
