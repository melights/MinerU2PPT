---
name: sync-codex
description: Safely syncs .claude agents/skills/rules into .codex with OS-aware links and regenerates AGENTS.md without deleting unrelated .codex content.
disable-model-invocation: true
---

# Skill: Sync Codex (Single Script)

## Description

Synchronize `.claude` configuration into `.codex` with safe rebuild scope and cross-platform link handling.

## Required Behavior

1. Use `.claude` as source of truth.
2. Rebuild only `.codex/agents`, `.codex/skills`, and `.codex/rules`.
3. Do not delete the whole `.codex` directory.
4. Use OS-appropriate links (Windows/WSL: Junction, Linux/macOS: symlink).
5. Regenerate root `AGENTS.md`.

## Run Command

```bash
python .claude/skills/sync-codex/scripts/sync.py
```

## Failure Handling

1. If link creation fails, report exact error and stop.
2. Do not fall back to deleting `.codex`.
