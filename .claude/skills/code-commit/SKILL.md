---
name: code-commit
description: Fast commit flow with minimal safety gates (secret sanity check + Conventional Commit).
argument-hint: "-m <[commit-message]>"
---

# Code Commit Skill

## Description

This skill is the **lightweight finalization step**.
It should be fast, deterministic, and focused on safely creating a commit.

Heavy quality/security validation (build, type/lint, broad test execution, deep architectural/security checks) belongs outside this skill.

## Workflow

1. **Inspect and Split Commit Scope (Lightweight)**
   - Read current git state (`status`, staged/unstaged diff summary).
   - Separate changes into:
     - **Current-task related changes** (this request's modifications).
     - **Existing pending changes** (pre-existing uncommitted backlog).
   - Confirm there are changes to commit.

2. **Minimal Safety Gates (Mandatory, Per Commit Batch)**
   - **Secret sanity check (fast):** scan files being committed for obvious hardcoded credentials/tokens.
   - **Commit message validity:** ensure Conventional Commit format.

3. **Commit Message Handling**
   - If `-m` is provided, use it for the first commit (current-task related changes), and generate additional Conventional Commit message(s) for remaining batch(es) when needed.
   - If `-m` is not provided, generate concise Conventional Commit messages based on each batch diff and ask for confirmation when needed.

4. **Create Commit(s) for Current-Task Related Changes First**
   - Stage only current-task related files/hunks.
   - Execute one or more `git commit` operations when splitting is needed.
   - Return intermediate commit hash(es) and status.

5. **Then Commit Existing Pending Changes**
   - Stage remaining backlog files/hunks.
   - Execute one or more additional `git commit` operations when splitting is needed (skip if none remain).
   - Return final commit hash(es) and final status.

## What This Skill Does NOT Do

- No full build/type/lint/test pipelines.
- No automatic dependency/tool installation.
- No deep architectural or security validation.

These should be handled before invoking this skill, via your preferred validation workflow.

## When to Use

- As the last step after implementation is complete.
- When you want a reliable, low-latency commit flow.

## Guardrails

- Abort if there is nothing to commit.
- Abort on unresolved secret warnings.
- Do not use destructive git operations.
- Keep behavior predictable; avoid hidden side effects.