# CS 182 Final Project: Dynamic Resource Scheduling using Dynamic Constraint Satisfaction Problems

A Python 2-based solver for dynamic constraint satisfaction problems (DyCSPs). Based on existing research literature, we built the DnAC-4 and DnAC-6 algorithms to perform dynamic arc-consistency tests, as well as classical backtracking search to obtain complete assignments.

Test sets include trivial CSPs, well-known CSP problems as well as CSPs that we formalized to simulate the resource scheduling and allocation problem between healthcare providers, which is the motivation behind this project.

## Understanding and Usage

`main.py` is the main file that runs the CSPs. `dyCSPAgent.py` contains the classses for dynamic CSPs and the various algorithms. `tests/` contain the various CSPs that we tested our program on, `output/` contains the results of our program on these test sets, and `statistics/` contain some charts regarding memory and runtime performances of the 2 algorithms. *For the MRI scheduling CSPs, note that for each CSP we also included the Python code that generated the respective input file. This Python code serves as both a primitive UI for an actual MRI scheduling application, as well as a verification of the correctness of our program.*

The solver can be run with the command `python main.py input output` where `input` and `output` should be accordingly replaced with the appropriate file location and name. You can either run it on any of our test input files, or create your own CSP.

Use the optional flag `--a` to choose the arc consistency algorithm to run, with `dnac4` and `dnac6` as possible arguments. The default algorithm used is DnAC-4. Use the flag `-h` for further help.

### Creating your own input files

Input files to the system should be written as such:

1. The first line contains a single integer *n* for the number of variables (which will be represented as 1 to *n*).

2. The next *n* lines should be the variable followed by its domain, space-separated.

3. Every line after that represents a constraint at some time *t*. This is written with the actual character *c*, followed by the time *t* as an integer, followed by the actual characters *a* or *r* indicating that the constraint is being added or relaxed, followed by the two variables *i* and *j*, (and if the constraint is being added) all the consistent pairs of values that *i* and *j* can be assigned to. Everything is space-separated.

*Note that the algorithms only work for binary constraints. All constraints at time t = 0 should be added, and constraints that don't already exist should not be relaxed.*

Refer to the test files for actual examples.

## Authors

* **Adam Nahari**, Harvard College Class of 2020

* **Wanqian Yang**, Harvard College Class of 2020

## Acknowledgements

* Professor Scott Kuindersma and staff of CS 182 (Fall 2017).

* DnAC-4 algorithm from:
Bessiere, C. (1991) "Arc-Consistency in Dynamic Constraint Satisfaction Problems".

* DnAC-6 algorithm from:
Debruyne, R. (1996) "Arc-Consistency in Dynamic CSPs Is No More Prohibitive".
