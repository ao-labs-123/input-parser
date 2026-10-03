# Stage 2 — Causal Direction Analysis
## Overview:
This step builds upon the identified agents from Stage 1 to map the logical flow of the conversation. By analyzing conjunctions, conjunctive adverbs, and causal prepositions (e.g., `because`,`due to`, `therefore`, `however`), the model determines the direction of causality between events, preventing the misinterpretation of premise and conclusion.

## Key Points:
**1. Logical Marker Mapping**:

The system identifies specific linguistic "connectors" to categorize the sentence structure into cause-and-effect pairs, logical reversals, or sequential events.

**2. Directional Dependency**:

By anchoring the cause and the result to the agents identified in previous stages, the model maps the "who" and "why" behind an action, ensuring that causality remains attached to the correct entity.

**3. Structural disambiguation**:

This step resolves complex sentences where multiple events are linked, preventing the AI from conflating an outcome with an underlying motivation.

## Logic Comparison: Causal Parsing
| Input | Logic Process | Result |
|--|--|--|
| **"I'm stressed due to the project."** | [Agent: I] + [Preposition: due to] + [Noun: project] | AI maps: Project → Causes → I (Stress). |
| **"I succeeded because you helped."** | [Agent: I] + [Conjunction: because] + [Agent: You] | AI maps: You (Help) → Causes → I (Success). |

## Example of Causal Tracking:
 **Input**: "I couldn't finish the report because the system was down."
 
 **Analysis**:
 
 - Agent: "I" (Speaker).
 
 - Causal Marker: "Because" (indicates the reason follows).
 
 - Event Chain: System down (Condition) → Result in failure to finish report (Outcome).
 
 **AI Understanding**: The system failure is the primary cause; the speaker is the affected agent.
