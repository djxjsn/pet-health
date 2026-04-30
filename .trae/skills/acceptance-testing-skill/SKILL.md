---
name: Acceptance Testing Skill
description: >
  Validates deliverables against specification documents with pass/fail results and
  prioritized fix list. Use this skill when reviewing completed work, when the user
  says "check if it's done", "verify the output", "test against spec", "acceptance
  check", or after any development or fix is complete. This skill ensures work
  actually matches requirements instead of just "looking correct".
---

# Acceptance Testing Skill

## Core Principle

Judge the output against the SPEC, not against your own judgment.

## Testing Protocol

### Step 1: Load the Specification

Before testing:
1. Read the PRD / requirements document
2. Read the API contract (if applicable)
3. Read the acceptance criteria
4. Load the test cases

### Step 2: Execute Checks

For each requirement in the spec:
1. Find the corresponding implementation
2. Verify it satisfies the requirement exactly
3. Record: PASS, FAIL, or PARTIAL

### Step 3: Report Results

Output format:
```
## Acceptance Test Results

### Summary
- Total requirements checked: N
- Passed: X
- Failed: Y
- Partial: Z

### Failures (by priority)
| # | Requirement | Status | Issue | Priority |
|---|-------------|--------|-------|----------|
| 1 | [req desc] | FAIL | [what's wrong] | P0/P1/P2 |
| 2 | [req desc] | PARTIAL | [what's missing] | P0/P1/P2 |
```

## Priority Classification

- **P0 (Critical)**: Core functionality broken, blocks release
- **P1 (High)**: Important feature missing or incorrect, needs fix before release
- **P2 (Low)**: Minor issue, nice-to-have, can be deferred

## Checking Dimensions

Check each requirement across these dimensions:

1. **Completeness**: Is everything specified actually implemented?
2. **Correctness**: Does the implementation behave as specified?
3. **Format**: Does the output match the contracted format?
4. **Edge Cases**: Are error cases and boundary conditions handled?

## Anti-Patterns

### DO NOT:
- "Looks good to me" - not a valid assessment
- Skip requirements you think are "obviously correct"
- Mark as PASS without actually verifying
- Add requirements that weren't in the spec

### DO:
- Check EVERY requirement systematically
- Quote the spec requirement when reporting a failure
- Be specific about what's wrong (not just "it fails")
- Prioritize fixes so the developer knows what to address first

## Re-Testing After Fixes

When a fix is delivered:
1. Re-test ONLY the failed requirements that were addressed
2. Run a regression check on previously-passed requirements
3. Report updated results
4. Close the loop until all requirements pass

## Self-Assessment Warning

If you wrote the code you're now testing:
1. Acknowledge the conflict of interest
2. Be EXTRA critical of your own work
3. Better yet, ask for a separate testing pass
