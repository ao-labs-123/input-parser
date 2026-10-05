import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.analyzer import LogicAnalyzer
from src.rules.stage1_rule import determine_explicit_subject, determine_subject
from src.rules.stage2_rule import analyze_causality_and_ambiguity
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
    )
    assert stage2["structure"] == {
        "relation": "CauseEffect",
        "marker": "because",
        "cause": "you helped",
        "effect": "I succeeded",
    }

    modification = analyze_modification_structure("The report, which was long, is done.")
    stage3 = analyzer.stage3_analyze("The report, which was long, is done.", stage1, modification)
    assert stage3["decision"] == "Supplementary"
    assert stage3["target"] == "The report"


def test_stage2_maps_despite_as_concession_not_causality():
    text = "Failed despite the effort."
    stage1 = {"agent": "Unknown"}
    rule_result = analyze_causality_and_ambiguity(text, "Unknown")
    stage2 = LogicAnalyzer({}).stage2_analyze(text, stage1, rule_result)

    assert rule_result["is_causal"] is False
    assert rule_result["markers"] == []
    assert rule_result["concession_markers"] == ["despite"]
    assert stage2["structure"] == {
        "relation": "Concession",
        "marker": "despite",
        "concession": "the effort",
        "outcome": "Failed",
    }


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


if __name__ == "__main__":
    test_stage1_unknown_subject_falls_to_stage2_clarification()
    test_stage1_prioritizes_formal_subject_imperative_and_psychological_agent()
    test_stage2_maps_cause_to_effect_and_stage3_maps_modification()
    test_stage5_synthesizes_the_documented_5w1h_frame()
    test_passive_without_by_is_detected()
    test_base_and_progressive_classification_stays_correct()
    print("Analyzer stage checks passed")
