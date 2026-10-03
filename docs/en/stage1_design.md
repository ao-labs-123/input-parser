# Stage 1 — Agent and Subject Estimation (with Clarification Fallback)

## Overview:

This step focuses on deterministically interpreting sentences with implicit subjects. By codifying linguistic patterns—such as psychological verbs (e.g., 'think', 'feel', 'want'), imperative markers, and evidential cues—the model maps the primary agent without relying on statistical estimation.

When an input features a null subject and lacks all core identification markers (`Null Subject + No Core Markers`), the system refrains from making speculative assumptions. Instead, it assigns the agent as `Unknown` and seamlessly triggers a targeted clarification request (or defers resolution to context-mapping modules).

## Key Points:

### 1. Explicit Subject Priority:
When an explicit subject is present in the sentence (e.g., "I", "He", "The company"), the model bypasses inference heuristics and directly assigns the specified agent. This acts as the highest-priority deterministic rule.

### 2. Second-Person Directives (Imperatives & Listener Directives):
When a sentence utilizes imperative structures, direct instructions, or second-person discourse markers without an explicit subject (e.g., "Please submit", "Check this"), the system directly infers the agent as the listener ("You").

### 3. Psychological Verb Default for Omitted Subjects:
When a psychological verb (e.g., 'think', 'feel', 'want', 'hope', 'stressed') appears without an explicit subject, the model assigns the speaker ("I") as the agent by default.

### 4. Evidentiality & Attribution Override:
If a sentence contains markers of evidentiality or indirect speech (e.g., 'seemingly', 'allegedly', 'they say', 'I heard', 'it is told'), the system overrides the speaker-default and assigns the agent to a third party ("He/She/They").

### 5. Fallback to Clarification (`Unknown` Agent):
When a sentence contains no explicit subject and lacks all core markers (no psychological verbs, no imperative markers, and no evidential cues), the model assigns `Unknown` to prevent hallucination. This state automatically prepares a natural language clarification request or routes the chunk to the topological context mapper.

---

## Structural Parsing Framework Examples

### Example 1: Formal Subject Framework (It ... that ...)
When a sentence utilizes a dummy or formal subject structure (`It is/was [predicate] that...`), the system skips the surface-level "It" and extracts the actual logical agent from within the embedded clause.

* **Input Example:** "It is required that you submit the form."
* **Logic Process:** Bypasses dummy "It" → Recognizes structural framework `It is [X] that [Y]` → Extracts the first word of the that-clause as the true agent.
* **Result:**
  ```json
  {
    "process": "Formal Subject Detected (It ... that)",
    "decision": "Priority: True Subject in Clause",
    "agent": "you",
    "structure": "It is [required] that [you submit the form]"
  }

### Example 2: Fallback Framework (⁠Unknown⁠ / Clarification Request)
When an input consists of a plain factual statement without syntactic markers, the system assigns an ⁠Unknown⁠ agent.

* **Input Example:** "Went to the cafe yesterday."
* **Logic Process:** Null Subject + No Core Markers → Refrains from speculative assignment → Flags agent as ⁠Unknown⁠.
* **result:**
 ```json
  {
   "process": "Null Subject + No Core Markers Detected",
   "decision": "Fallback: Undetermined Agent",
   "agent": "Unknown",
   "action_required": "Trigger Stage 1 Clarification / Context Resolution"
  }
```

## Logic Comparison: Deterministic Rules vs. Undetermined Fallback
| Input | Logic Process | Result |
|--|--|--|
| **"He succeeded because I helped."** | **Explicit Subject Present** → [Priority: Explicit Subject] | AI directly assigns "He" and "I" as the respective agents. |
| **"Please review the document."** | **Imperative / Direct Directive** → [Priority: Listener Address] | AI assigns "You" as the agent. |
| **"Thought was strange."** | **Psychological Verb + Null Subject** → [Default: Speaker] | AI assigns "I" as the agent. |
| **"Thought it was strange apparently."** | **Psychological Verb + Null Subject + Evidential Marker** → [Override: 3rd Party] | AI assigns "He/She/They" as the agent. |
| **"It is required that you submit the form."** | **Formal Subject Frame Detection** → Clause Extraction | AI bypasses "It" and assigns "you" as the agent. |
| **"Went to the cafe yesterday."** | **Null Subject + No Core Markers** → [Fallback: Undetermined Agent] | AI assigns ⁠Unknown⁠ and prepares clarification / context mapping. |
| **"Failed despite the effort."** | **Null Subject + No Core Markers** → [Fallback: Undetermined Agent] | AI assigns ⁠Unknown⁠ and prepares clarification / context mapping. |