
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

    is_causal = any(marker.lower() in text.lower() for marker in lexicon)
    return is_causal

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
