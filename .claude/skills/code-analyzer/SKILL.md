---
name: code-analyzer
description: Analyzes a codebase to understand its structure, technology stack, and core logic. It can answer questions about the code, analyze errors with stack traces, and document key workflows. Use this for deep dives into unfamiliar open-source projects.
---

# Code Analyzer Skill

This skill provides a structured workflow for analyzing a software project. It creates a persistent analysis document to build a knowledge base about the codebase over time.

## Workflow

The process is divided into two main phases: Initialization (one-time analysis) and Interaction (Q&A and further analysis).

### Phase 1: Initialization & Analysis

Your primary goal is to create a comprehensive analysis document located at `docs/analyze/project.md`.

1.  **Check for Existing Analysis**:
    *   First, use the `Glob` tool to check if `"docs/analyze/project.md"` already exists.
    *   If it exists, read the file using the `Read` tool and proceed directly to **Phase 2: Interaction**.
    *   If it does not exist, proceed with the following steps to create it.

2.  **Gather High-Level Information**:
    *   Use `Glob` to find all Markdown files (`"**/*.md"`) in the repository.
    *   Read the main `README.md` (and other relevant `.md` files like `CONTRIBUTING.md`, `ARCHITECTURE.md`, etc.) to understand the project's purpose.
    *   Pay attention to multi-language files (e.g., `README.zh-CN.md`). Prioritize the English version or the one that seems most complete.

3.  **Analyze Technology Stack**:
    *   Read the reference file `references/common_config_files.md` to identify which configuration files to look for.
    *   Use `Glob` and `Read` to find and inspect files like `package.json`, `pom.xml`, `go.mod`, etc.
    *   Determine the programming languages, frameworks, and key dependencies.

4.  **Analyze Codebase Structure**:
    *   Use the `Bash` tool with `ls -F` to list the top-level directory structure.
    *   From the structure, identify the key directories (e.g., `src/`, `lib/`, `tests/`, `docs/`).

5.  **Generate Analysis Document**:
    *   Use `Bash` to create the `docs/analyze` directory if it doesn't exist: `mkdir -p docs/analyze`.
    *   Read the template `references/analysis_template.md`.
    *   Populate the template with the information gathered in the steps above.
    *   Write the final analysis to `docs/analyze/project.md`.

### Phase 2: Interaction

Once the `project.md` analysis document is available, use it as your primary source of truth for the project's architecture and purpose.

1.  **Answering User Questions**:
    *   When the user asks a question (e.g., "Where is the authentication logic?"), first consult `docs/analyze/project.md`.
    *   Use the information in the analysis to form a hypothesis about where the relevant code lives.
    *   Use `Grep` to search for keywords in the codebase to confirm your hypothesis and find specific code snippets.
    *   Read the relevant code files and provide a detailed answer, including file paths and line numbers (`path/to/file.js:123`).

2.  **Analyzing Errors with Stack Traces**:
    *   If the user provides an error message with a stack trace, parse the file paths and line numbers from the trace.
    *   Use `Read` to directly access the specified code locations.
    *   Analyze the code in the context of the error and provide a diagnosis.

3.  **Analyzing and Documenting Workflows**:
    *   If the user asks you to analyze a specific workflow (e.g., "Trace the user login process"), perform a series of `Grep` and `Read` calls to follow the logic through the codebase.
    *   After the analysis is complete, summarize the workflow.
    *   Ask the user if they want to save this analysis: "This analysis of the 'user login process' seems valuable. Shall I save it as a knowledge document for future reference?"
    *   If they agree, write the summary to a new file in `docs/analyze/flow-user-login.md` (use a descriptive name).

4.  **Using Web Search**:
    *   If you are stuck on a problem after a few attempts, or if the user's error is generic, use the `WebSearch` tool.
    *   Search for the error message or a description of the problem to find external solutions or documentation. Use these findings to inform your next steps.
