# Current Phase: Input Parsing
**At this stage, incoming text is captured and parsed into a lightweight, deterministic rule-based structure—bypassing heavy statistical prediction.**

<img width="960" height="540" alt="image" src="https://github.com/user-attachments/assets/7844b856-c666-433f-9344-dffe1ab9bc0c" />



# The 5-Stage Logical Pipeline
**Our engine processes language through a bottom-up logical hierarchy:**

- [stage1:Subject Inference](docs/en/stage1_design.md)
- [stage2:Clarification Request](docs/en/stage2_design.md)
- [stage3:Context & Causality Inference](docs/en/stage3_design.md)
- [stage4:Modification Clarification](docs/en/stage4_design.md)
- [stage5:Argument Mapping](docs/en/stage5_design.md)

# Verification with `log.json`

**The output and intermediate state of each stage are recorded deterministically in [`log.json`](data/log.json). This log serves as proof that the 5-stage inference operates through explainable logical compression without relying on heavy statistical predictions.**

## Example: Logical Inference vs. Probabilistic Guessing
Our engine avoids errors by using structural overrides instead of statistical weightings.

| Input | Logic Process | Result |
|--|--|--|
| "Thought it was strange." | Psychological Verb + Null Subject → [Default: Speaker] | AI correctly identifies "I". |
| "Thought it was strange, apparently." | Psychological Verb + Evidential Marker → [Override: 3rd Party] | AI identifies the agent as a 3rd party. |

In the second case, the "Evidential Marker" (⁠apparently⁠) acts as a logical trigger to override the default speaker-centric perspective. This deterministic logic ensures precision that probabilistic models often miss.

## Core Philosophy
Traditional AI relies on massive statistical models (LLMs) to predict the next word, often leading to "black box" decisions, high computational costs, and conversational misinterpretations. This project takes a different path: **Deterministic Logical Abstraction.**

By codifying the structural and cognitive rules of language into a lightweight engine, we achieve human-level contextual reasoning with a fraction of the memory and processing power.

## Key Pillars
1. **Explainability (Transparent Reasoning)**:

   Every inference step is driven by clear, rule-based logic. You can trace exactly why the AI interpreted a sentence a certain way.
   
2. **Extreme Efficiency**:

   Our engine performs inference via logic, not massive matrix multiplication. It is designed to run on low-cost hardware, from home appliances to embedded systems.

3. **Language Agnostic Structure**:

   The logical core (Subject Inference, Semantic Categorization) is designed to be applicable across multiple languages, including Japanese and English.


## Repository Structure

```repository

├── docs  
│    ├── ROADMAP.md
│    ├── stage1_design.md
│    ├── stage2_design.md
│    ├── stage3_design.md
│    ├── stage4_design.md
│    └── stage5_design.md  
│
├── data
│    ├── examples
│    └── log.json
│
├── src
│    ├── lexicon
│    ├── rules
│    ├── analyzer.py
│    └── main.py
│  
├── README.md
└── LICENSE

```

