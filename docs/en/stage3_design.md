# Stage 3 — Clarification of Modification Structures & Morphism Mapping

## Overview:

This step refines the contextual precision established in Stages 1 and 2 by isolating adverbs, prepositional phrases, relative clauses, and adjectives[span_4](start_span)[span_4](end_span). By mapping these modifying elements onto downstream 5W1H slots—specifically the **How** dimensions (**Manner**, **Instrument / Means**, and **Degree**)—Stage 3 transforms structural modifiers into topological deformation operators ($\xrightarrow{}$). This ensures that modifiers correctly scale, deform, or mediate the primary Action morphisms and State nodes before particle encapsulation[span_5](start_span)[span_5](end_span).

---

## Key Points:

### 1. Modifier Tethering & Slot Mapping:
The system systematically identifies the target (head noun, verb, or action morphism) for every modifier to prevent long-distance dependency errors[span_6](start_span)[span_6](end_span). Furthermore, modifiers are mapped directly to their corresponding **How** subtypes:
* **Manner Operator ($\xrightarrow{\text{How: Manner}}$):** Modifies the trajectory or quality of an Action morphism (e.g., *quickly*, *carefully*).
* **Instrument / Means Mediator ($\xrightarrow{\text{How: Instrument}}$):** Introduces intermediate nodes or execution channels that facilitate an Action (e.g., *by working hard*, *with a key*).
* **Degree / Magnitude Scaler ($\xrightarrow{\text{How: Degree}}$):** Scales the weight or intensity of a State node or Action morphism (e.g., *very*, *apparently*).

### 2. Defining vs. Supplementary Logic:
The model categorizes attributes based on their essentiality to node identification[span_7](start_span)[span_7](end_span):
* **Defining Modifiers:** Essential to uniquely identifying a target node (e.g., "The report *that I wrote*")[span_8](start_span)[span_8](end_span).
* **Supplementary Modifiers:** Non-essential background context or soft constraints (e.g., "The report, *which was long*")[span_9](start_span)[span_9](end_span).

### 3. Contextual Anchoring:
Modifiers are cross-referenced with the agent profiles established in Stage 1, ensuring that nested descriptions of third parties do not bleed into the primary speaker's attributes[span_10](start_span)[span_10](end_span).

---

## Logic Comparison: Modifier Parsing & Morphism Mapping

| Input | Logic Process | Topological Morphism Mapping Result |
| :--- | :--- | :--- |
| **"The report was completed quickly."** | [Action: completed] + [Adverb: quickly] $\to$ [How: Manner] | $\text{Agent(System/I)} \xrightarrow{\text{Action: Complete}} \text{Node(Report)} \ \Big\vert \ \xrightarrow{\text{How: Manner(Quickly)}}$ |
| **"He succeeded by working hard."** | [Outcome: succeeded] + [Prep Phrase: by working hard] $\to$ [How: Instrument] | $\text{Agent(He)} \xrightarrow{\text{How: Instrument(Hard Work)}} \text{State(Success)}$ |
| **"Thought it was strange apparently."** | [Mental State: thought strange] + [Adverb: apparently] $\to$ [How: Degree/Uncertainty] | $\text{Agent(I)} \xrightarrow{\text{Internal Eval}} (\text{Node(It)} \to \text{State(Strange)}) \ \Big\vert \ \xrightarrow{\text{How: Degree(Apparently)}}$ |
| **"The report, which was long, is done."** | [Supplementary Clause: which was long] $\to$ [Attribute] | $\text{Node(Report)} \xrightarrow{\text{Attribute}} \text{State(Long)}$ *(Supplementary context to main Action)* |

---

## Example of Structural Clarification:

**Input:** `"I talked to the manager who was frustrated with the deadline."`

**Analysis:**
* **Target Node:** `Manager` (Third Party Agent)[span_11](start_span)[span_11](end_span)
* **Modifier:** `"who was frustrated with the deadline"` (Relative Clause / State)[span_12](start_span)[span_12](end_span)
* **Action Morphism:** `"talked to"` (Primary Action)

**Topological Morphism Graph:**
* $\text{Agent(I)} \xrightarrow{\text{Action: Talk}} \Big( \text{Agent(Manager)} \xrightarrow{\text{Attribute}} \text{State(Frustrated)} \xrightarrow{\text{Cause}} \text{Node(Deadline)} \Big)$

**AI Understanding:**
Accurately attaches the emotional state (`Frustrated`) and its cause (`Deadline`) exclusively to the target `Manager` node[span_13](start_span)[span_13](end_span). The primary Action morphism from `Agent(I)` remains clean and structurally isolated[span_14](start_span)[span_14](end_span).
