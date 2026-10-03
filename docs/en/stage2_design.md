# Stage 2 — Clarification Requests for Undetermined Agents

## Overview:

This step functions as an intelligent resolution and fallback mechanism. When Stage 1's deterministic mapping encounters structural ambiguity—such as plain factual statements lacking psychological or evidential markers—the model refrains from making speculative assumptions. Instead, it marks the agent as `Unknown`.

If the agent cannot be resolved through short-term contextual analysis (e.g., via the topological mapper), the model triggers a targeted, natural-language clarification request. This mirrors human conversational behavior by intervening only when logical constraints remain unresolved.

## Key Points:

### 1. Rule-Based Ambiguity Trigger:

The system designates an agent as `Undetermined (Unknown)` and routes it to Stage 2 based on explicit structural conditions:

* **Null Subject + No Core Markers (Primary Trigger):** 
  When an input contains a null subject and lacks all core identification markers (i.e., no psychological verbs for 1st person, no imperative markers for 2nd person, and no evidential markers for 3rd person), the system cannot deterministically infer the agent. 
  * *Example:* "Went to the cafe yesterday." (カフェに行った。) → Triggers Stage 2 Clarification.

* **Equally Plausible Candidates:** 
  When multiple potential agents exist with equal structural weight and cannot be disambiguated by syntactic rules alone.

### 2. Minimalist Intervention:

To maintain natural conversational flow, inquiries are strictly limited to resolving the specific ambiguity. The model avoids exhaustive questioning, relying on targeted re-confirmation (e.g., "Are you referring to yourself or someone else?").

### 3. Human-Centric Data Integrity:

By acknowledging that certain sentences are genuinely ambiguous even to human listeners, this step prevents the AI from assigning hallucinated or unverified agents, thereby ensuring logical integrity and user trust.

## Note on Context Resolution Order:

When an Agent is marked as `Unknown` at Stage 1:
1. **Immediate Input Parsing:** The agent status is set to `Unknown`.
2. **Contextual Resolution:** The subsequent `topological-mapper` module attempts to resolve the `Unknown` agent using active discourse context or match-and-select rules.
3. **Clarification Trigger:** If contextual resolution fails to yield a unique agent, the system officially executes the Stage 2 Clarification Request to the user.

## Logic Comparison: Undetermined Agents

| Input | Logic Process | Result |
| :--- | :--- | :--- |
| **"Succeeded because you helped."** | Null Subject + Action Verb + No Psychological/Evidential Markers → [Fallback: Ambiguous Clause] | AI marks agent as `Unknown` and prepares Stage 2 clarification. |
| **"Failed despite the effort."** | Null Subject + No Contextual Clues + Action Verb → [Fallback: Completely Ambiguous] | AI marks agent as `Unknown` and prepares Stage 2 clarification. |
| **"Required further investigation."** | Null Subject + Objective Obligation/State → [Fallback: Missing Logical Agent] | AI marks agent as `Unknown` and prepares Stage 2 clarification. |
