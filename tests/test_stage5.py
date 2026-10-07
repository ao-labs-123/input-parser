import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.analyzer import LogicAnalyzer
from src.rules.stage1_rule import determine_explicit_subject, determine_subject
from src.rules.stage2_rule import analyze_causality_and_ambiguity, analyze_context_relation
from src.rules.stage3_rule import analyze_modification_structure
from src.rules.stage4_rule import analyze_semantic_structure


def test_stage1_unknown_subject_falls_to_stage2_clarification():
    text = "Went to the cafe yesterday."
    subject_status = determine_subject(text)
    analyzer = LogicAnalyzer({})

    stage1 = analyzer.stage1_analyze(text, subject_status)
    assert stage1["agent"] == "Unknown"
    assert stage1["decision"] == "Fallback: Undetermined Agent"
    assert stage1["action_required"] == "Trigger Stage 1 Clarification / Context Resolution"

    stage2 = analyzer.stage2_analyze(text, stage1, analyze_causality_and_ambiguity(text, subject_status))
    assert stage2["decision"] == "Clarification Required (Undetermined Agent)"
    assert stage2["agent"] == "Unknown"


def test_stage1_prioritizes_formal_subject_imperative_and_psychological_agent():
    analyzer = LogicAnalyzer({})

    formal = "It is required that you submit the form."
    assert analyzer.stage1_analyze(
        formal, determine_explicit_subject(formal)
    )["agent"] == "you"
    assert analyzer.stage1_analyze("Please review the document.", "Neutral")["agent"] == "You"
    assert analyzer.stage1_analyze("Thought was strange.", "First-Person")["agent"] == "I"


def test_stage2_maps_cause_to_effect_and_stage3_maps_modification():
    analyzer = LogicAnalyzer({})
    text = "I succeeded because you helped."
    stage1 = {"agent": "I"}
    stage2 = analyzer.stage2_analyze(
        text,
        stage1,
        analyze_causality_and_ambiguity(text, "I"),
        semantic_result=analyze_semantic_structure(text),
    )
    assert stage2["structure"] == {
        "relation": "CauseEffect",
        "marker": "because",
        "cause": "you helped",
        "effect": "I succeeded",
        "event": {
            "category": "Action",
            "verb": "succeeded",
            "actor": "I",
            "patient": None,
        },
    }
    assert stage2["decision"] == "Causal relation mapped; Event classified: Action"
    assert stage2["action"] == {
        "verb": "succeeded",
        "actor": "I",
        "patient": None,
    }
    assert stage2["mapping"] == (
        "you helped -> Cause -> I succeeded; I -> Action -> succeeded"
    )

    modification = analyze_modification_structure("The report, which was long, is done.")
    stage3 = analyzer.stage3_analyze("The report, which was long, is done.", stage1, modification)
    assert stage3["decision"] == "Supplementary"
    assert stage3["target"] == "The report"
    assert stage3["structure"]["classification"] == "Supplementary"
    assert stage3["mapping"] == "Node(The report) -> Attribute -> State(Long)"
    assert stage3["attribution"] == {
        "target": "The report",
        "modifier_agent": "The report",
        "primary_agent": "I",
    }


def test_stage3_keeps_modifier_agent_separate_from_primary_agent():
    text = "I talked to the manager who was frustrated with the deadline."
    modification = analyze_modification_structure(text)
    stage3 = LogicAnalyzer({}).stage3_analyze(text, {"agent": "I"}, modification)

    assert stage3["target"] == "manager"
    assert stage3["modifier"] == "was frustrated with the deadline"
    assert stage3["mapping"] == (
        "Node(manager) -> Attribute -> State(Frustrated) -> Cause -> Node(the deadline)"
    )
    assert stage3["attribution"] == {
        "target": "manager",
        "modifier_agent": "manager",
        "primary_agent": "I",
    }


def test_stage3_classifies_adjectival_description_as_supplementary():
    text = "Please review the long report."
    modification = analyze_modification_structure(text)
    stage3 = LogicAnalyzer({}).stage3_analyze(text, {"agent": "You"}, modification)

    assert stage3["decision"] == "Supplementary"
    assert stage3["target"] == "report"
    assert stage3["modifier"] == "long"
    assert stage3["mapping"] == "Node(report) -> Attribute -> State(Long)"
    degree_modification = analyze_modification_structure("Please review the very long report.")
    degree_stage3 = LogicAnalyzer({}).stage3_analyze(
        "Please review the very long report.", {"agent": "You"}, degree_modification
    )
    assert degree_stage3["mapping"] == (
        "Node(report) -> Attribute -> State(Long) -> How: Degree(Very)"
    )

    manner_text = "The report was completed quickly."
    manner_modification = analyze_modification_structure(manner_text)
    manner_stage3 = LogicAnalyzer({}).stage3_analyze(
        manner_text, {"agent": "The report"}, manner_modification
    )
    assert manner_stage3["mapping"] == (
        "Node(The report) -> Action(Complete) -> How: Manner(Quickly)"
    )

    instrument_text = "He succeeded by working hard."
    instrument_modification = analyze_modification_structure(instrument_text)
    instrument_stage3 = LogicAnalyzer({}).stage3_analyze(
        instrument_text, {"agent": "He"}, instrument_modification
    )
    assert instrument_stage3["mapping"] == (
        "Agent(He) -> How: Instrument(Hard Work) -> State(Success)"
    )
    assert analyze_modification_structure("I was told by him.") is None

    tool_text = "I opened the door with a key."
    tool_modification = analyze_modification_structure(tool_text)
    tool_stage3 = LogicAnalyzer({}).stage3_analyze(
        tool_text, {"agent": "I"}, tool_modification
    )
    assert tool_stage3["mapping"] == (
        "Agent(I) -> How: Instrument(A Key) -> Action(Open)"
    )

    degree_text = "Thought it was strange apparently."
    degree_modification = analyze_modification_structure(degree_text)
    degree_stage3 = LogicAnalyzer({}).stage3_analyze(
        degree_text, {"agent": "He/She/They"}, degree_modification
    )
    assert degree_stage3["mapping"] == (
        "Agent(He/She/They) -> Internal Eval -> State(Strange)"
        " -> How: Degree(Apparently)"
    )


def test_stage2_does_not_emit_relation_words_as_actions():
    analyzer = LogicAnalyzer({})
    for text, expected_mapping in (
        (
            "Succeeded because you helped.",
            "you helped -> Cause -> Succeeded",
        ),
        (
            "Failed the exam because of bad luck.",
            "bad luck -> Cause -> Failed the exam",
        ),
    ):
        stage2 = analyzer.stage2_analyze(
            text,
            {"agent": "Unknown"},
            analyze_causality_and_ambiguity(text, "Unknown"),
            semantic_result=analyze_semantic_structure(text),
        )

        assert stage2["action"] is None
        assert stage2["mapping"] == expected_mapping


def test_stage2_preserves_manner_context_without_adding_it_to_patient():
    text = "He succeeded by working hard."
    stage2 = LogicAnalyzer({}).stage2_analyze(
        text,
        {"agent": "He"},
        analyze_causality_and_ambiguity(text, "He"),
        context_result=analyze_context_relation(text),
        semantic_result=analyze_semantic_structure(text),
    )

    assert stage2["action"] == {
        "verb": "succeeded",
        "actor": "He",
        "patient": None,
    }
    assert stage2["mapping"] == "He -> Action -> succeeded"
    assert stage2["context"] == {
        "relation": "Manner",
        "marker": "by",
        "context": "working hard",
        "event": "He succeeded",
    }


def test_stage2_preserves_temporal_context_for_state_predicate():
    text = "I was stressed after the long meeting."
    stage2 = LogicAnalyzer({}).stage2_analyze(
        text,
        {"agent": "I"},
        analyze_causality_and_ambiguity(text, "I"),
        context_result=analyze_context_relation(text),
        semantic_result=analyze_semantic_structure(text),
    )

    assert stage2["action"] == {
        "verb": "stressed",
        "actor": "I",
        "patient": None,
    }
    assert stage2["mapping"] == "I -> State -> stressed"
    assert stage2["context"]["relation"] == "Temporal"
    assert stage2["context"]["context"] == "the long meeting"


def test_stage2_emits_action_while_stage4_keeps_category_label():
    text = "Please review the document."
    analyzer = LogicAnalyzer({})
    stage1 = analyzer.stage1_analyze(text, "Neutral")
    semantic = analyze_semantic_structure(text)

    stage2 = analyzer.stage2_analyze(
        text,
        stage1,
        analyze_causality_and_ambiguity(text, "Neutral"),
        semantic_result=semantic,
    )
    stage4 = analyzer.stage4_analyze(text, semantic, stage1)

    assert stage2["action"] == {
        "verb": "review",
        "actor": "You",
        "patient": "the document",
    }
    assert stage2["mapping"] == "You -> Action -> review the document"
    assert stage4["category"] == "Action"


def test_stage2_classifies_events_without_causal_relations():
    analyzer = LogicAnalyzer({})
    examples = (
        ("Please review the document.", "Action", "review", "You"),
        ("I am stressed.", "State", "stressed", "I"),
        ("I have a car.", "Stative", "have", "I"),
    )

    for text, category, verb, actor in examples:
        stage2 = analyzer.stage2_analyze(
            text,
            {"agent": actor},
            analyze_causality_and_ambiguity(text, actor),
            semantic_result=analyze_semantic_structure(text),
        )

        assert stage2["process"] == f"Event: {category}"
        assert stage2["decision"] == (
            f"No causal relation; Event classified: {category}"
        )
        assert stage2["structure"] == {
            "relation": "Event",
            "event": {
                "category": category,
                "verb": verb,
                "actor": actor,
                "patient": stage2["action"]["patient"],
            },
        }


def test_stage2_uses_state_label_for_state_like_events():
    text = "I am stressed due to the project."
    analyzer = LogicAnalyzer({})
    stage1 = {"agent": "I"}
    stage2 = analyzer.stage2_analyze(
        text,
        stage1,
        analyze_causality_and_ambiguity(text, "I"),
        semantic_result=analyze_semantic_structure(text),
    )

    assert "-> Cause ->" in stage2["mapping"]
    assert "-> State ->" in stage2["mapping"]
    assert stage2["structure"]["event"]["category"] == "State"
    assert stage2["decision"] == "Causal relation mapped; Event classified: State"


def test_stage2_maps_despite_as_concession_not_causality():
    text = "I failed despite the effort."
    stage1 = {"agent": "Unknown"}
    rule_result = analyze_causality_and_ambiguity(text, "Unknown")
    stage2 = LogicAnalyzer({}).stage2_analyze(
        text,
        stage1,
        rule_result,
        semantic_result=analyze_semantic_structure(text),
    )

    assert rule_result["is_causal"] is False
    assert rule_result["markers"] == []
    assert rule_result["concession_markers"] == ["despite"]
    assert stage2["structure"] == {
        "relation": "Concession",
        "marker": "despite",
        "concession": "the effort",
        "outcome": "I failed",
        "event": {
            "category": "Action",
            "verb": "failed",
            "actor": "Unknown",
            "patient": None,
        },
    }
    assert stage2["decision"] == "Concessive relation mapped; Event classified: Action"
    assert stage2["mapping"] == (
        "the effort -> Concession -> I failed; Unknown -> Action -> failed"
    )


def test_stage2_does_not_treat_role_as_as_causal():
    text = "I work as a teacher."
    rule_result = analyze_causality_and_ambiguity(text, "I")

    assert rule_result["is_causal"] is False
    assert rule_result["markers"] == []


def test_stage5_synthesizes_the_documented_5w1h_frame():
    text = "Yesterday, I bought a book at the store to study logic."
    analyzer = LogicAnalyzer({})

    output = analyzer.stage5_analyze(
        text,
        None,
        {"agent": "I"},
    )

    assert output == {
        "stage": "Stage 5 - 5W1H Synthesis",
        "frame": {
            "who": "I",
            "what": "bought a book",
            "when": "Yesterday",
            "where": "at the store",
            "why": "to study logic",
            "how": "Unspecified",
        },
        "status": "Ready for Particle Encapsulation",
    }


def test_passive_without_by_is_detected():
    text = "The report was completed quickly."
    result = analyze_semantic_structure(text)

    assert result["form"] == "Passive"
    assert result["verb"] == "completed"
    assert result["actor"] == "Unknown"
    assert result["receiver"] == "The report"

    analyzer = LogicAnalyzer({})
    stage4 = analyzer.stage4_analyze(text, result, {"agent": "The report"})
    output = analyzer.stage5_analyze(text, result, {"agent": "The report"}, stage4_result=stage4)

    assert stage4["category"] == "Action"
    assert stage4["patient"] == "The report"
    assert output["stage"] == "Stage 5 - 5W1H Synthesis"
    assert output["frame"]["who"] == "The report"
    assert output["frame"]["what"] == "completed the report"
    assert output["frame"]["how"] == "quickly"


def test_base_and_progressive_classification_stays_correct():
    assert analyze_semantic_structure("I have a car.")["form"] == "Base"
    assert analyze_semantic_structure("I am having a party.")["form"] == "Progressive"
    assert analyze_semantic_structure("I was told by him.")["form"] == "Passive"
    analyzer = LogicAnalyzer({})
    assert analyzer.stage4_analyze("I have a car.", analyze_semantic_structure("I have a car."))["category"] == "Stative"
    assert analyzer.stage4_analyze("I am having a party.", analyze_semantic_structure("I am having a party."))["category"] == "Action"


def test_base_parsing_ignores_causal_and_concessive_markers_as_verbs():
    assert analyze_semantic_structure("Succeeded because you helped.")["verb"] == "succeeded"
    assert analyze_semantic_structure("Failed despite the effort.")["verb"] == "failed"


def test_state_predicates_expose_state_value_separately():
    result = analyze_semantic_structure("Thought was strange.")
    assert result["form"] == "State"
    assert result["state"] == "strange"
    assert result["verb"] == "strange"


if __name__ == "__main__":
    test_stage1_unknown_subject_falls_to_stage2_clarification()
    test_stage1_prioritizes_formal_subject_imperative_and_psychological_agent()
    test_stage2_maps_cause_to_effect_and_stage3_maps_modification()
    test_stage5_synthesizes_the_documented_5w1h_frame()
    test_passive_without_by_is_detected()
    test_base_and_progressive_classification_stays_correct()
    print("Analyzer stage checks passed")
