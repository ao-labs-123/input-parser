# Stage 5 — Parsing Case Relationships & Verb Classification
## Overview:
This structural layer standardizes the relationship between nouns and verbs, and differentiates verb states. Building upon the previous stages, it resolves passive voice constructions and applies morphological analysis to distinguish between stative and action (dynamic) verbs, ensuring precise temporal and agency mapping.

## Key Points:
**1. Passive Voice Mapping**:

The system identifies the structure ⁠[Subject] + [be/get] + [V-en] + [by-agent]⁠. It assigns the grammatical subject as the "receiver" and the noun following "by" as the "actor." If "by" is omitted, the grammatical subject is defaulted as the receiver, provided the interpretation remains logically consistent.

**2. Morphological Verb Classification**:

The model utilizes morphological analysis to determine verb type based on the presence of the ⁠-ing⁠ suffix:
- Dynamic/Action Verb Detection: If the verb appears in the progressive form (⁠be + V-ing⁠), it is classified as an action (e.g., "I am understanding the concept" → active cognitive process).
- Stative Verb Detection: Verbs appearing in their base form (e.g., "I understand") are treated as states. For verbs like understand or have, the presence of ⁠be + V-ing⁠ triggers a dynamic interpretation, overriding the static default.
 
**3. Lexicon-Based Exception Handling**:

For irregular cases (e.g., "stand" as a posture vs. "stand" as a situation), the system references a dedicated ⁠lexicon⁠ to determine whether the verb should be parsed as a state or an action regardless of standard morphology.


## Logic Comparison: Case Relation Parsing

| Input | Logic Process | Result |
|--|--|--|
| **"I have a car."** | [Morphology: Base] → [Category: Stative] | Possession status.|
| **"I am having a party."** | [Morphology: be + V-ing] → [Category: Action] | Active event participation. |
| **"I was told by him."** | [Passive: be + V-en + by] | Actor: Him / Receiver: I. |

## Example of Structural & State Tracking:
**Input**: "I was standing there when I understood what was happening."

**Analysis**:
- "Was standing": Lexicon check classifies as posture (Stative/Duration).
- "Understood": Base form classification (Stative/State).
- "Was happening": Progressive form classification (Action/Dynamic).
 
 **AI Understanding**: The AI captures a continuous state of being (standing), a static cognitive state (understanding), and an active event (happening) simultaneously, without conflating their logical roles.
