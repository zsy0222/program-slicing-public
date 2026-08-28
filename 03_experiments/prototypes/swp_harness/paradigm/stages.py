"""
Stage-specific prompt templates for the Slicing Workflow Paradigm (SWP).

Each stage guides the LLM through one step of dependency reasoning.
The stages are designed to be assembled into a single unified prompt
with clearly marked boundaries.
"""

# ============================================================================
# Stage 1: Code Understanding
# ============================================================================

STAGE1_CODE_UNDERSTANDING = r"""
## Stage 1: Code Understanding

First, understand the structure of the provided code. Complete the following tasks:

### 1.1 Statement Inventory
List EVERY executable statement in the code with its line number. Include:
- Variable declarations with initializers
- Assignments
- Method calls
- Conditionals (if/else, switch)
- Loops (while/for/do-while)
- Return statements
- Throw statements

Do NOT include:
- Blank lines
- Comments
- Class/interface declarations
- Method signatures (only the body statements)

### 1.2 Statement Classification
For each statement, classify it as one of:
- `ASSIGN`: assignment or declaration with initialization
- `CONDITION`: if-condition, switch-expression, loop-condition
- `CALL`: standalone method call
- `RETURN`: return statement
- `THROW`: throw statement

### 1.3 Variable Tracking
For each statement, identify:
- `DEF`: variables that are defined/assigned by this statement
- `USE`: variables that are read/used by this statement

### Output Format for Stage 1
```
<<<STAGE1_OUTPUT>>>
STATEMENTS:
L1 | int x = 5                    | ASSIGN | DEF:x       | USE:-
L2 | int y = x + 3                | ASSIGN | DEF:y       | USE:x
L3 | if (y > 0)                   | CONDITION | DEF:-   | USE:y
L4 |     System.out.println(y)    | CALL     | DEF:-   | USE:y
L5 | return y                      | RETURN   | DEF:-   | USE:y

SUMMARY:
- Total statements: N
- Variables defined: [...]
- Variables used at sink: [...]
<<<END_STAGE1_OUTPUT>>>
```
"""

# ============================================================================
# Stage 2: Data Dependency Tracing
# ============================================================================

STAGE2_DATA_DEPENDENCY = r"""
## Stage 2: Data Dependency Tracing

Now trace the DATA dependencies backward from the slicing criterion.

{stage2_role_description}

### 2.1 Identify Sink Variables
Start from the sink statement(s). List all variables that are USED at the sink.

### 2.2 Trace Reaching Definitions
For EACH variable used at the sink, find the most recent statement that DEFINES that variable — one that can reach the sink without the variable being redefined (killed) along the way.

Key rule: If variable `v` is redefined at line L_k, then any definition of `v` before L_k is KILLED and does NOT reach past L_k.

### 2.3 Recursive Tracing
For each definition statement found, check what variables IT uses. Recursively trace those variables to their reaching definitions. Continue until you hit:
- Method parameters (formal parameters are sources of data)
- Constants/literals (no further trace needed)
- The source statement (for Chop/Forward modes — STOP here)
- No more definitions to trace

### 2.4 Build the Data Slice
Collect all statements involved in the data dependency chains. This is your DATA SLICE.

### Output Format for Stage 2
```
<<<STAGE2_OUTPUT>>>
SINK_VARIABLES: [v1, v2, ...]

DATA_DEP_CHAINS:
Chain 1: L{sink} uses [v1] <- defined at L{d1} <- L{d1} uses [v3] <- defined at L{d2} <- ... [STOP: parameter/constant/source]

DATA_SLICE_STATEMENTS: [Lx, Ly, Lz, ...]
  Lx: (reason: defines v1 used at L{sink})
  Ly: (reason: defines v3 used at Lx)
  ...

STATEMENTS_OUTSIDE_DATA_SLICE: [La, Lb, ...]
  La: (reason: no data flow to sink — variable w defined here is killed/never used at sink)
<<<END_STAGE2_OUTPUT>>>
```
"""

STAGE2_FORWARD_ROLE = """
This is a FORWARD slice — trace FORWARD from the source instead of backward from the sink.
Start from the source statement. For each variable DEFINED at the source, find all subsequent
statements that USE that variable. Recursively trace: if a USE statement also DEFINES new variables,
trace those forward too.
"""

STAGE2_BACKWARD_ROLE = """
This is a BACKWARD slice — trace backward from the sink statement.
"""

STAGE2_CHOP_ROLE = """
This is a CHOP (bidirectional slice) — first trace backward from the sink to find all statements
that affect the sink (backward data slice), then in Stage 4 we will constrain this to only
statements reachable from the source.
"""

# ============================================================================
# Stage 3: Control Dependency Analysis
# ============================================================================

STAGE3_CONTROL_DEPENDENCY = r"""
## Stage 3: Control Dependency Analysis

Now analyze CONTROL dependencies. A statement is control-dependent on a condition if that condition determines WHETHER the statement executes.

### 3.1 Identify Controlling Conditions
For EACH statement in your data slice (from Stage 2), check which condition(s) control its execution:
- Is the statement inside an `if` body? → It is controlled by the `if` condition.
- Is the statement inside a `while`/`for` body? → It is controlled by the loop condition.
- Is it inside an `else` block? → It is controlled by the NEGATION of the `if` condition.
- Is it in a `catch` block? → It is controlled by the exception type match.
- Is it nested? → It is controlled by ALL enclosing conditions (outer + inner).

### 3.2 Add Conditions to Slice
For each controlling condition identified, add the condition statement to your slice.
Also trace the DATA dependencies of the condition variables (repeat Stage 2 logic for condition expressions).

### 3.3 Handle Nested Structures
If statement S is inside:
```
if (a > 0) {        // outer condition
    if (b > 1) {    // inner condition
        S;           // controlled by BOTH (a > 0) AND (b > 1)
    }
}
```
Then both conditions are control dependencies and must be included.

### Output Format for Stage 3
```
<<<STAGE3_OUTPUT>>>
CONTROL_DEPS:
  L{s1}: controlled by L{cond1} (reason: inside if-body of cond1)
  L{s2}: controlled by L{cond1}, L{cond2} (reason: nested — inside both conditions)

ADDED_CONDITIONS: [L{cond1}, L{cond2}, ...]
  L{cond1}: (data deps: uses variables [...] — already in slice / newly added)
  L{cond2}: (data deps: uses variables [...] — already in slice / newly added)

EXTENDED_SLICE: [Lx, Ly, Lz, ...]  (data slice + control conditions + their data deps)
<<<END_STAGE3_OUTPUT>>>
```
"""

STAGE3_FORWARD_ROLE = """
For a forward slice: instead of finding conditions that control the sink, find statements
whose execution IS CONTROLLED BY the source condition. If the source is a condition, add
all statements in its controlled blocks.
"""

# ============================================================================
# Stage 4: Chop Constraint (bidirectional slice only)
# ============================================================================

STAGE4_CHOP_CONSTRAINT = r"""
## Stage 4: Chop Constraint (Bidirectional Restricted Reachability)

This is a CHOP (bidirectional slice). Now apply the chop constraint to filter the backward
slice to only statements on source→sink paths.

### 4.1 Forward Reachability from Source
Starting from the source statement(s), trace FORWARD along data and control dependencies.
Find ALL statements that are reachable from the source.

A statement T is forward-reachable from source S if:
- S defines a variable v, and T uses v (data-forward), OR
- S is a condition, and T is in its controlled body (control-forward), OR
- There is a chain of such forward edges from S to T

### 4.2 Constrain the Backward Slice
Take the backward slice from Stages 2-3. Remove any statement that is NOT forward-reachable
from the source. The result is the CHOP — only statements that lie on paths from source to sink.

This is NOT the same as "forward ∩ backward" — a statement might be in both forward and
backward sets but on UNRELATED paths. The correct chop algorithm (Jackson & Rollins 1994) is:
  1. Compute forward slice F from source
  2. Restrict the PDG to only nodes in F
  3. Compute backward slice from sink within the restricted graph

### Output Format for Stage 4
```
<<<STAGE4_OUTPUT>>>
FORWARD_REACHABLE: [Lx, Ly, Lz, ...]  (all statements reachable from source)

REMOVED_BY_CHOP:
  L{removed1}: (reason: not forward-reachable from source — on a different path)
  L{removed2}: (reason: not forward-reachable from source)

CHOP_SLICE: [Lx, Ly, Lz, ...]  (backward slice ∩ forward reachable)
<<<END_STAGE4_OUTPUT>>>
```
"""

# ============================================================================
# Stage 5: Verification & Structured Output
# ============================================================================

STAGE5_VERIFY_OUTPUT = r"""
## Stage 5: Verification and Structured Output

### 5.1 Inclusion Verification
For EACH statement in your final slice, provide a brief justification:
- What dependency chain connects it to the sink?
- Why MUST it be included?

### 5.2 Exclusion Verification
Identify 3-5 statements that are NOT in the slice but appear nearby in the code.
For each, explain WHY it was correctly excluded.

### 5.3 Structured Output
Output the final result in the strict format below. This format will be automatically parsed.

```
<<<SLICE_RESULT>>>
TYPE: {slice_type}
SINK_LINES: [{sink_line_numbers}]
SOURCE_LINES: [{source_line_numbers}]

INCLUDED:
L{line} | {code} | {DATA_DEF:vars / CONTROL / SINK / SOURCE} | depends_on:{dependency_list}
L{line} | {code} | {DATA_DEF:vars / CONTROL / SINK / SOURCE} | depends_on:{dependency_list}
...

EXCLUDED:
L{line} | {code} | IRRELEVANT: {brief_reason}
L{line} | {code} | IRRELEVANT: {brief_reason}
...

CHAINS:
{chain_descriptions}

STATS:
included_count={N_included} | excluded_count={N_excluded} | total={N_total}
<<<END_SLICE_RESULT>>>
```

### 5.4 Final Check
Before finalizing, verify:
- [ ] Every statement in INCLUDED has a clear dependency path to the sink
- [ ] No irrelevant statements are included
- [ ] All control dependencies of included statements are themselves included
- [ ] The output format is exactly as specified (will be machine-parsed)
"""
