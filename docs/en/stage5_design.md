# Stage 5 — 5W1H Frame Extraction and Semantic Synthesis

## Overview:

This final stage inside the `input-parser` pipeline integrates the structural components resolved in Stages 1 through 4 (Agent identification, Causal relationships, Modification structures, and Case relations) to synthesize a complete 5W1H (Who, What, When, Where, Why, How) semantic frame. 

By binding these parsed elements into a standardized 5W1H schema before data leaves the parsing module, this step ensures that the downstream `particle-encapsulation` module receives fully resolved, deterministic attributes. This eliminates the need for linguistic interpretations during particle creation and preserves strict separation of concerns.

## Key Points:

### 1. Deterministic Attribute Binding:
The module directly maps resolved logical components from previous stages to the 5W1H slots without performing speculative guessing:
* **Who:** Mapped directly from Stage 1 (`agent` / explicit or inferred subject).
* **What:** Mapped from Stage 4 (`patient` / direct object / core action predicate).
* **When:** Extracted from temporal modifiers (Stage 3 & 4 case markers like "yesterday", "at 5 PM").
* **Where:** Extracted from locative case markers and spatial adjuncts (Stage 4).
* **Why:** Mapped from Causal clauses and logical dependencies resolved in Stage 2.
* **How:** Extracted from modal, instrument, or manner modifiers resolved in Stage 3 & 4.

### 2. Handling Missing Attributes (`Null` / `Unspecified` Slots):
If a 5W1H slot is not explicitly mentioned or inferable from the sentence structure (e.g., no location or cause specified), the system explicitly tags the slot as `Unspecified` rather than generating speculative values. This preserves data integrity for topological mapping.

### 3. Handoff to Particle Encapsulation:
The output of Stage 5 serves as the finalized JSON payload for the `particle-encapsulation` module, transforming discrete linguistic features into a clean, encapsulated input vector/dictionary.

---

## Structural Parsing Framework Examples

### Example: Multi-Clause Input Synthesis
Synthesis of a complex sentence through all previous parsing stages into a unified 5W1H schema.

* **Input Example:** "Yesterday, I bought a book at the store to study logic."
* **Logic Process:** 
  * Agent = "I" (Stage 1: Explicit)
  * What = "bought a book" (Stage 4: Patient / Action)
  * When = "Yesterday" (Stage 3/4: Temporal Modifier)
  * Where = "at the store" (Stage 4: Locative)
  * Why = "to study logic" (Stage 2: Causal Goal)
  * How = `Unspecified`
* **Result:**
  ```json
  {
    "stage": "Stage 5 - 5W1H Synthesis",
    "frame": {
      "who": "I",
      "what": "bought a book",
      "when": "Yesterday",
      "where": "at the store",
      "why": "to study logic",
      "how": "Unspecified"
    },
    "status": "Ready for Particle Encapsulation"
  }

## Logic Comparison: Attribute Mapping Matrix
| Input | 5W1H Mapping Strategy | Target Frame Output |
|--|--|--|
| **"Went to the cafe yesterday."** | Agent=⁠Unknown⁠ (Stage 1 Fallback), Location="cafe", Time="yesterday" | Who: ⁠Unknown⁠
What: "went"
When: "yesterday"
Where: "cafe"
Why/How: ⁠Unspecified⁠ |
| **"Please review the document carefully."** | Agent=⁠you⁠ (Stage 1 Imperative), Manner="carefully" | Who: "you"
What: "review the document"
How: "carefully"
When/Where/Why: ⁠Unspecified⁠ |
| **"Failed the exam because of bad luck."** | Agent=⁠Unknown⁠ (Stage 1 Fallback), Cause="bad luck" | Who: ⁠Unknown⁠
What: "failed the exam"
Why: "because of bad luck"
When/Where/How: ⁠Unspecified⁠ |