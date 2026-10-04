
import json
import re
from pathlib import Path

def get_lexicon():
    lexicon_path = Path(__file__).resolve().parent.parent / "lexicon" / "causality_markers.json"
    with lexicon_path.open("r", encoding="utf-8") as f:
        causality_list = json.load(f)
    return causality_list

def analyze_causality(text):
    lexicon = get_lexicon()
    markers = [
        marker
        for category_markers in lexicon.values()
        for marker in category_markers
    ]
    return any(
        re.search(rf"(?<!\w){re.escape(marker)}(?!\w)", text, re.IGNORECASE)
        for marker in markers
    )


def analyze_causality_and_ambiguity(text, subject_status):
    lexicon = get_lexicon()
    markers = [
        marker
        for category_markers in lexicon.values()
        for marker in category_markers
    ]
    matched_markers = [
        marker
        for marker in markers
        if re.search(rf"(?<!\w){re.escape(marker)}(?!\w)", text, re.IGNORECASE)
    ]
    ambiguous_agent = subject_status in (None, "Unknown", "Neutral")

    return {
        "status": "Ambiguous" if ambiguous_agent else "Resolved",
        "is_causal": bool(matched_markers),
        "markers": matched_markers,
    }

def analyze_context_relation(text):
    patterns = [
        (r"\bafter\s+(?P<context>[^,.!?]+)", "Temporal", "after"),
        (r"\bby\s+(?P<context>\w+ing(?:\s+\w+)*)", "Manner", "by"),
    ]

    for pattern, relation, marker in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {
                "relation": relation,
                "marker": marker,
                "context": match.group("context").strip(),
                "event": text[:match.start()].strip(),
            }

    return None
