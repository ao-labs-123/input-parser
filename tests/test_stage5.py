import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.analyzer import LogicAnalyzer
from src.rules.stage5_rule import analyze_semantic_structure


def test_passive_without_by_is_detected():
    result = analyze_semantic_structure("The report was completed quickly.")

    assert result["form"] == "Passive"
    assert result["verb"] == "completed"
    assert result["actor"] == "Unknown"
    assert result["receiver"] == "The report"

    analyzer = LogicAnalyzer({})
    output = analyzer.stage5_analyze("The report was completed quickly.", result, {"agent": "The report"})

    assert output["process"] == "[Passive: be + V-en + by]"
    assert output["result"] == "Actor: Unknown / Receiver: The report."


def test_base_and_progressive_classification_stays_correct():
    assert analyze_semantic_structure("I have a car.")["form"] == "Base"
    assert analyze_semantic_structure("I am having a party.")["form"] == "Progressive"
    assert analyze_semantic_structure("I was told by him.")["form"] == "Passive"


if __name__ == "__main__":
    test_passive_without_by_is_detected()
    test_base_and_progressive_classification_stays_correct()
    print("Stage 5 checks passed")
