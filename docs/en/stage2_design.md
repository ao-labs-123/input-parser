# Stage 2 — Causal & Structural Direction Analysis

## Overview:

This step builds upon the identified agents from Stage 1 to map the core logical flow and semantic structure of the input. Beyond identifying causal connections, Stage 2 categorizes nodes and morphisms into **Actions** (external dynamic behaviors), **States** (internal conditions or situational static nodes), and **Causes** (directional causal dependencies between events). By analyzing verbs, conjunctions, and logical markers, the system construct a clear topological graph before passing attributes to downstream modification and framing stages.

---

## Key Points:

### 1. Triadic Classification (Action, State, Cause):
The module explicitly distinguishes between dynamic actions, static/internal states, and the causal links connecting them:
* **Action (Dynamic Morphism):** External behaviors, physical operations, or explicit task execution (e.g., *wrote*, *submitted*, *bought*).
* **State (Static Node / Internal Condition):** Cognitive/mental conditions, emotional states, or passive situational statuses (e.g., *stressed*, *thought*, *system was down*).
* **Cause (Directional Dependency):** Connective logic linking an initial State/Action to a resulting State/Action (e.g., *because*, *due to*, *therefore*).

### 2. Directional Dependency & Node Transition:
By anchoring Cause arrows to Agents and distinguishing Actions from States, the model accurately maps event sequences (e.g., `State: System Down` $\to$ `Cause` $\to$ `Action/Failure: Could not finish report`). This prevents the system from confusing an internal psychological state with an external physical action.

### 3. Structural Disambiguation:
This step resolves complex multi-event structures, ensuring the AI correctly isolates whether an event is a driving motivation (Cause), an executed movement (Action), or a resulting psychological/environmental condition (State).

---

## Logic Comparison: Structural & Causal Parsing

| Input | Logic Process | Topological Mapping Result |
| :--- | :--- | :--- |
| **"I'm stressed due to the project."** | [State: Stressed] + [Cause Marker: due to] + [Node: Project] | `Node: Project` $\xrightarrow{\text{Cause}}$ `State: Stressed (Agent: I)` |
| **"I succeeded because you helped."** | [Action: Succeeded] + [Cause Marker: because] + [Action: Helped] | `Action: You (Help)` $\xrightarrow{\text{Cause}}$ `Action/Outcome: I (Success)` |
| **"I thought it was strange."** | [Agent: I] + [Mental State: Thought] + [Target Evaluation: Strange] | `Agent: I` $\xrightarrow{\text{Internal Eval}}$ `State: Strange` *(Non-Action)* |

---

## Example of Structural & Causal Tracking:

**Input:** `"I couldn't finish the report because the system was down."`

**Analysis:**
* **Agent:** `"I"` (Speaker)
* **State Node:** `"the system was down"` (Environmental Condition / Initial State)
* **Action/Outcome Node:** `"couldn't finish the report"` (Failed Execution)
* **Causal Marker:** `"because"` (Establishes direction: State $\to$ Outcome)

**Topological Graph Generation:**
* `State: System Down` $\xrightarrow{\text{Cause}}$ `Action: Fail to finish report`

**AI Understanding:**
The system outage is the primary environmental **State (Cause)**; the speaker is the affected agent whose physical **Action** was obstructed