---
name: learn
description: Analyzes the conversation for repetitive user actions and corrections to suggest new skills or improvements to existing ones. Use this skill when you want to reflect on the recent interaction and abstract a pattern into a reusable skill.
---

# Skill: Learn from Interaction (Optimized)

## Description
This skill enables you to analyze the current conversation, identify patterns of inefficiency, and then **initiate the skill creation/modification process** by invoking the `skill-creator` skill.

## Instructions
When this skill is invoked, you MUST perform the following steps:

1.  **Analyze Conversation for Patterns:** Carefully review the recent conversation history, focusing specifically on:
    *   **Repetitive Operations:** Identify sequences of commands or actions that you have performed multiple times to achieve a similar goal for the user.
    *   **User Corrections:** Pinpoint instances where the user had to correct your assumptions, provide clarifying information, or steer you back on course. This often indicates a gap in your procedural knowledge.

2.  **Identify a Skill Opportunity:** Based on the patterns you find, determine the most impactful opportunity for abstraction.
    *   If you found a **repetitive operation**, the opportunity is to **create a new skill**.
    *   If you found a **user correction**, the opportunity is to **modify an existing skill**.

3.  **Summarize Findings & Prepare for Handoff:**
    *   Concisely summarize your analysis and the core logic of the proposed skill (new or modified).
    *   Prepare a clear statement of intent to pass to the `skill-creator`. For example: "I have identified a repetitive workflow for analyzing US stock indices. I need to modify the 'get-stock-info' skill to formally include this capability."

4.  **Invoke the `skill-creator` Skill (CRITICAL NEW STEP):**
    *   Instead of manually drafting the skill file, you MUST now **invoke the `skill-creator` skill**.
    *   Use the summary from the previous step as the input/argument for `skill-creator`.
    *   The `skill-creator` will then guide you and the user through the standardized, five-step process of creating or updating the skill file and any associated resources.

5.  **Handle No Opportunity:** If, after careful analysis, you cannot find any clear repetitive patterns or significant user corrections, inform the user of this. State that you analyzed the conversation but did not identify any patterns suitable for abstraction at this moment.
