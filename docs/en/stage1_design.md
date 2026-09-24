# Stage1 — Agent and Subject Estimation

## Overview:
This step focuses on optimizing the model's ability to interpret sentences with implicit subjects. By codifying linguistic patterns—such as the way psychological verbs (e.g., 'think', 'feel', 'notice') consistently map to the speaker as the primary agent—the model eliminates ambiguity in subject identification and significantly increases conversational accuracy, regardless of the underlying language.

1. Explicit Subject Present: 
   Highest priority; directly assigned as specified.
2. Null Subject + Psychological Verb: 
   Inferred as the speaker ("I") based on syntactic structure.
3. Null Subject + Evidential Marker: 
   Overridden and assigned to a third party ("He/She/They").
4. Null Subject + Psychological Verb + Evidential Marker: 
   Overridden and assigned to a third party ("He/She/They").
5. Null Subject + No Core Markers: 
   Falls back to Stage 2 clarification (Undetermined agent).


## Key Points:

**1. Explicit Subject Priority**:

   When an explicit subject is present in the sentence (e.g., "I," "He," "The company"), the model bypasses inference heuristics and directly assigns the specified agent. This acts as the highest-priority deterministic rule.

**2. Psychological Verb Default for Omitted Subjects**:

   When a psychological verb (e.g., 'think', 'feel', 'want', 'hope', 'stressed') appears without an explicit subject, assign the speaker as the agent by default.

**3. Evidentiality & Attribution Override**:

   If a sentence contains markers of evidentialities or indirect speech (e.g., 'seemingly', 'allegedly', 'they say', 'I heard', 'it is told'), treat the agent as a second or third party, overriding the speaker-default.

**4. Formal Subject Framework (It ... that ...)**:

When a sentence utilizes a dummy or formal subject structure (`It is/was [predicate] that...`), the system skips the surface-level `"It"` and extracts the actual logical agent from within the embedded clause.

* **Input Example**: `"It is required that you submit the form."`
* **Logic Process**: Bypasses dummy `"It"` $\rightarrow$ Recognizes the structural framework `It is [X] that [Y]` $\rightarrow$ Extracts the first word of the that-clause as the true agent.
* **Result**:
  ```json
  {
    "process": "Formal Subject Detected (It ... that)",
    "decision": "Priority: True Subject in Clause",
    "agent": "you",
    "structure": "It is [required] that [you submit the form]"
  }


## Logic Comparison: Implicit Subject vs. Evidential Override

| Input | Logic Process | Result |
| --- | --- | --- |
| "He succeeded because I helped." | Explicit Subject Present $\rightarrow$ [Priority: Explicit Subject] | AI directly assigns "He" and "I" as the respective agents. |
| "Thought was strange." | Psychological Verb + Null Subject → [Default: Speaker] | AI assigns "I" as the agent. |
| "Thought it was strange apparently." | Psychological Verb + Null Subject + Evidential Marker → [Override: 3rd Party] | AI assigns "He/She/They" as the agent. |
| ⁠"It is required that you submit the form."⁠ | Formal Subject Frame Detection → Clause Extraction | AI bypasses "It" and assigns "you" as the agent. |
