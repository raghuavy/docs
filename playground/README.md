# EE 8350 playground

A place to run the course's SystemVerilog yourself. Every example here was checked with the tools this folder installs.

## Open it

1. Go to https://codespaces.new/raghuavy/docs?quickstart=1 and click Create codespace.
2. Wait a few minutes the first time while it installs the simulators. You get VS Code in your browser with a terminal at the bottom.
3. In the terminal, type `./run scratch.sv` and press Enter.

Stop the codespace when you are done (top left menu, then Stop Current Codespace), so it does not use up your free monthly hours. Your files stay saved.

## Run something

```bash
./run scratch.sv                         # build with Verilator and run
./run -D BUG 12-uvm-adder/adder_tb.sv    # pass a define
./run --wave 19-cdc/sync.sv              # also write wave.vcd, then click it to see waveforms
./run --icarus 01-sv-review/basics.sv    # use Icarus Verilog, which keeps X values
./run --vcs --uvm my_uvm_test.sv         # on the department servers with VCS and UVM
```

The top module in each file must be called `tb`. Put your own experiments in `scratch.sv`, or copy any file and change it.

## Examples by lecture

1. `01-sv-review/basics.sv` shows two state versus four state types, a packed struct, a union, increment operators, foreach, enums and packed arrays. Run it with `--icarus` to see X.
2. `02-oop/copies.sv` shows handle copy, shallow copy and deep copy, static members and super.
3. `03-randomization/constraints.sv` covers constraints solved together, a child class replacing a constraint, inline `with`, randcase and `$urandom_range`.
4. `03-randomization/dist_and_solve.sv` counts outcomes to show `dist` weights and `solve before`.
5. `04-coverage/bins.sv` repeats the slide samples and prints the coverage for automatic bins, named bins, ignore_bins and a cross.
6. `05-interfaces/arbiter.sv` is an interface with modports and a clocking block driving a small arbiter. Try `--wave`.
7. `06-07-threads/forks.sv` covers join, join_any, join_none and the loop variable bug with its fix.
8. `06-07-threads/mailbox.sv` covers a mailbox with a handshake event and a one key semaphore.
9. `09-11-advanced-oop/virtual_and_callbacks.sv` covers virtual methods, `$cast`, the blueprint pattern and a drop callback.
10. `10-assertions/req_grant.sv` shows overlapping requests where the assertion catches the first one, plus a cover property.
11. `12-uvm-adder/adder_tb.sv` is the adder with a predictor and scoreboard in plain SystemVerilog. Run it again with `-D BUG`.
12. `19-cdc/sync.sv` has two clocks, a two flop synchronizer and a Gray code counter with an assertion. Try `--wave`.

The `browser/` folder holds a second set of examples, one per lecture, written for the website's Code tab. That tab runs Icarus Verilog inside the browser, so these stick to what Icarus supports and build things like constraints, coverage and assertion checks by hand.

## What the free tools cannot do

The playground uses Verilator 5.054 and Icarus Verilog 13. They handle classes, constraints, covergroups, threads, mailboxes and most assertions. Some things they do not cover:

- Full UVM (Lectures 8 and 12). Run UVM code with VCS on the department servers (`./run --vcs --uvm file.sv`), or on https://www.edaplayground.com with a free account by choosing UVM 1.2 and a commercial simulator. The course's own UVM adder files are in the .tgz on Canvas.
- Verilator treats every X as 0. Use `--icarus` when you want to see X and Z.
- Most SVA works, including `##[m:n]`, `[*m]`, `[->m]`, `throughout`, `within`, `intersect` and `first_match`. The nonconsecutive repetition `[=m]` does not work in Verilator yet. Use VCS or EDA Playground for that one.

## Without Codespaces

On any Ubuntu 24.04 machine or in WSL, run `bash .devcontainer/setup.sh` from the repo folder once, open a new terminal, then use `./run` the same way.
