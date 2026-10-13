import json
import re
from pathlib import Path

def get_lexicon():
    lexicon_dir = Path(__file__).resolve().parent.parent / "lexicon"
    with (lexicon_dir / "psychological_verbs.json").open("r", encoding="utf-8") as f:
        verbs = json.load(f)
    with (lexicon_dir / "attribution_markers.json").open("r", encoding="utf-8") as f:
        markers = json.load(f)
    
    combined = {**verbs, **markers}
    return combined

def determine_explicit_subject(text):
    # 前後の空白とピリオドを除去
    target_text = text.strip().rstrip(".")
    
    # ==========================================
    # 1. 【最優先】形式主語 (It is ... that ...) の判定
    # ==========================================
    formal_subject_match = re.search(r"^It\s+(is|was)\s+([^ ]+)\s+that\s+(.+)", target_text, re.IGNORECASE)
    
    if formal_subject_match:
        predicate = formal_subject_match.group(2).strip()
        that_clause = formal_subject_match.group(3).strip()
        
        clause_words = that_clause.split()
        true_agent = clause_words[0] if clause_words else "Unspecified"
        
        return {
            "structure_type": "FormalSubject",
            "formal_subject": "It",
            "predicate": predicate,
            "that_clause": that_clause,
            "true_agent": true_agent
        }

    # ==========================================
    # 2. 通常の明記された主語の判定
    # ==========================================
    # 形式主語から漏れた「単なる代名詞としての It」のみをここで拾うように分離
    explicit_subjects = ["I", "He", "She", "They", "We", "You", "It"]
    
    words = target_text.split()
    if not words:
        return None
        
    first_word = words[0].replace(",", "").replace(".", "").strip()
    
    if first_word in explicit_subjects:
        return first_word
        
    if first_word.startswith("I'm"):
        return "I"
        
    if first_word in ["The", "A", "An"] and len(words) > 1:
        second_word = words[1].replace(",", "").replace(".", "").strip()
        return f"{first_word} {second_word}"
        
    return None

def determine_subject(text):
    # 既存の心理動詞・伝聞マーカーの判定ロジック
    lexicon = get_lexicon()
    target_text = text.lower().replace('.', '')
    
    is_reported = any(m.lower() in target_text for m in lexicon.get("Attribution Override", []))
    is_psychological = any(v.lower() in target_text for v in lexicon.get("Psychological Verbs", []))
    
    if is_reported:
        return "Third-Person"
    elif is_psychological:
        return "First-Person"
    return "Neutral"
