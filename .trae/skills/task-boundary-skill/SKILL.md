---
name: Task Boundary Skill
description: >
  Enforces strict task boundaries: one clear task at a time, stop immediately when
  done, never auto-extend scope. Use this skill when the user gives a specific task,
  when working on a ticket-driven workflow, when the user says "just do X", "don't
  do anything else", "only fix this", "stop after", or when you notice the AI
  refactoring, optimizing, or adding features beyond what was requested.
---

# Task Boundary Skill

## Core Principle

Do EXACTLY what was asked. Nothing more. Nothing less. Then STOP.

## Task Execution Protocol

### Step 1: Understand the Boundary

Before starting, clearly identify:
- What is the EXACT task? (one sentence)
- What does "done" look like? (specific criteria)
- What is explicitly OUT OF SCOPE?

### Step 2: Execute

Work ONLY on the defined task. Resist all temptation to:
- Fix unrelated bugs you notice
- Refactor "while you're in the area"
- Optimize code that works fine
- Add "nice to have" features
- Improve documentation unless asked

### Step 3: Stop

When the task is complete:
- Report what was done
- Do NOT start the next logical step
- Wait for the user's next instruction

## Common Boundary Violations

### DO NOT:
- "While I was at it, I also..." - VIOLATION
- "I noticed X was broken so I fixed it too" - VIOLATION
- "I took the liberty of..." - VIOLATION
- "This would be better if we also..." - VIOLATION

### DO:
- Complete the exact task
- Report completion
- Wait for next instruction

## Scope Creep Detection

Watch for these warning signs:
- You're working on a file not mentioned in the task
- You're changing behavior the user didn't complain about
- You're adding parameters/options not requested
- You're thinking "this would be better if..."

When you notice these: STOP and re-read the task description.

## Multi-Step Tasks

If the user gives multiple steps:
- Do them IN ORDER as specified
- Do NOT reorder or skip steps
- Do NOT add extra steps

## When Unsure About Scope

If it's unclear whether something is in scope:
1. State your uncertainty
2. Ask the user
3. Wait for clarification before proceeding

## The Golden Rule

The user asked for A. Deliver A. Don't deliver A+B+C.
If they wanted B and C, they would have asked.
