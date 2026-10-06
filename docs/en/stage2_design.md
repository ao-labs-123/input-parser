# Stage 2 — Causal & Structural Direction Analysis

## Overview:

This step builds upon the identified agents from Stage 1 to map the core logical flow and semantic structure of the input. Beyond identifying causal connections, Stage 2 categorizes all nodes and morphisms into **Actions** (external dynamic transformations), **States** (internal conditions or static nodes), and **Causes** (directional dependencies between events). By converting verbs, conjunctions, and logical markers into directional morphisms ($\xrightarrow{}$), the system constructs a unified topological graph before passing attributes to downstream modification and framing stages.

---

## Key Points:

### 1. Triadic Classification (Action, State, Cause):
The module explicitly distinguishes between dynamic actions, static/internal states, and the causal links connecting them:
* **Action Morphism ($\xrightarrow{\text{Action}}$):** External behaviors, physical operations, or explicit task executions transforming states.
* **State Node ($\text{State}(\dots)$):** Cognitive/mental conditions, emotional states, or passive situational statuses.
* **Cause Morphism ($\xrightarrow{\text{Cause}}$):** Directional dependencies linking an initial State/Event to a resulting State/Event.

### 2. Directional Morphisms & Node Transitions:
By representing both Actions and Causes as directed arrows between nodes, the model accurately traces multi-step event chains (e.g., $\text{Agent(I)} \xrightarrow{\text{Action}} \text{Node(Report)} \xrightarrow{\text{Cause}} \text{State(Success)}$). This prevents the system from confusing internal psychological evaluations with external physical actions.

### 3. Structural Disambiguation:
This step resolves complex multi-event structures, ensuring the AI correctly isolates whether an event is a driving motivation (Cause), an executed movement (Action), or a resulting psychological/environmental condition (State).

---

## Logic Comparison: Structural & Causal Parsing

| Input | Logic Process | Topological Morphism Mapping |
| :--- | :--- | :--- |
| **"I'm stressed due to the project."** | [State: Stressed] + [Cause Marker: due to] + [Node: Project] | $\text{Node(Project)} \xrightarrow{\text{Cause}} \text{Agent(I)} \to \text{State(Stressed)}$ |
| **"I succeeded because you helped."** | [Action: Succeeded] + [Cause Marker: because] + [Action: Helped] | $(\text{Agent(You)} \xrightarrow{\text{Action}} \text{Node(Help)}) \xrightarrow{\text{Cause}} (\text{Agent(I)} \xrightarrow{\text{Action}} \text{State(Success)})$ |
| **"I thought it was strange."** | [Agent: I] + [Mental State: Thought] + [Target Evaluation: Strange] | $\text{Agent(I)} \xrightarrow{\text{Internal Eval}} (\text{Node(It)} \to \text{State(Strange)})$ |
| **"I wrote the report at the office."** | [Agent: I] + [Action: wrote] + [Node: report] | $\text{Agent(I)} \xrightarrow{\text{Action: Write}} \text{Node(Report)}$ |

---

## Example of Structural & Causal Tracking:

**Input:** `"I couldn't finish the report because the system was down."`

**Analysis:**
* **Agent Node:** `Agent(I)`
* **Initial State Node:** `State(System Down)`
* **Target Object Node:** `Node(Report)`
* **Causal Marker:** `"because"` (Links initial state to action failure)

**Topological Morphism Graph:**
* $\text{State(System Down)} \xrightarrow{\text{Cause}} (\text{Agent(I)} \xRightarrow[\text{Failed}]{\text{Action: Finish}} \text{Node(Report)})$

**AI Understanding:**
The system outage is the primary environmental **State (Cause)** that obstructs the directed **Action Morphism** from `Agent(I)` to `Node(Report)`.
