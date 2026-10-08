import re

PSYCHOLOGICAL_VERBS = {"think", "thought", "feel", "want", "hope", "stressed"}


def analyze_semantic_structure(text):
    text_clean = text.strip().rstrip(".")
    text_clean = re.sub(
        r",\s*(?:who|which)\b[^,]*,",
        "",
        text_clean,
        flags=re.IGNORECASE,
    )
    relative_match = re.search(r"\b(?:who|which)\b", text_clean, re.IGNORECASE)
    if relative_match:
        main_clause = text_clean[:relative_match.start()].strip(" ,")
        if main_clause and main_clause.split()[0].lower() not in {"the", "a", "an"}:
            text_clean = main_clause
    
    # 1. 受動態の判定 (Passive: be + V-en + by)
    # 例: "I was told by him" / "The report was completed quickly"
    passive_match = re.search(
        r"\b(am|is|are|was|were|be|been)\b\s+([A-Za-z]+)\b(?:\s+by\s+(.+))?",
        text_clean,
        re.IGNORECASE,
    )
    if passive_match:
        be_verb = passive_match.group(1)
        v_en = passive_match.group(2)
        by_actor = passive_match.group(3)

        # be + V-ing は進行形であり、受動態の対象から除外する
        if v_en.lower().endswith("ing"):
            pass
        else:
            # 形容詞的な語は受動態と誤判定しないように、典型的な受動態の語尾を制限する
            if not re.search(r"(?:ed|en|t|d|n)$", v_en, re.IGNORECASE):
                pass
            else:
                idx = text_clean.lower().find(be_verb.lower())
                receiver = text_clean[:idx].strip()
                return {
                    "form": "Passive",
                    "verb": v_en.lower(),
                    "actor": by_actor.strip() if by_actor else "Unknown",
                    "receiver": receiver
                }
        
    # 2. 進行形の判定 (Morphology: be + V-ing)
    # 例: "I am having a party"
    progressive_match = re.search(r"\b(am|is|are|was|were)\b\s+(\w+ing)\b\s*(.*)", text_clean, re.IGNORECASE)
    if progressive_match:
        be_verb = progressive_match.group(1)
        v_ing = progressive_match.group(2)
        object_noun = progressive_match.group(3).strip()
        
        idx = text_clean.lower().find(be_verb.lower())
        subject = text_clean[:idx].strip()
        
        return {
            "form": "Progressive",
            "verb": v_ing.lower(),
            "subject": subject,
            "object": object_noun if object_noun else None
        }
        
    # 3. 状態述語の判定（be + adjective / be + state noun）
    # 例: "I am stressed due to the project."
    be_state_match = re.search(
        r"\b(am|is|are|was|were)\b\s+([A-Za-z]+)\b(?:\s+(.*))?",
        text_clean,
        re.IGNORECASE,
    )
    if be_state_match:
        subject = text_clean[:be_state_match.start()].strip()
        state_verb = be_state_match.group(2)
        remainder = be_state_match.group(3)
        result = {
            "form": "State",
            "state": state_verb.lower(),
            "subject": subject,
            "object": remainder.strip() if remainder else None,
        }
        psych_match = subject.split()[0].lower() if subject else ""
        if psych_match in PSYCHOLOGICAL_VERBS:
            result["psychological_verb"] = psych_match
            result["verb"] = None
        else:
            result["verb"] = state_verb.lower()
        return result

    # 4. 一般形（現在形・過去形など）の判定 (Morphology: Base)
    # 例: "I have a car"
    # 2語目が前置詞や因果・逆接マーカーなら、1語目が述語である場合がある
    non_verb_second_words = {
        "a", "an", "the", "to", "in", "on", "at", "of", "by", "for", "with",
        "from", "into", "onto", "after", "before", "because", "despite", "although",
        "though", "if", "when", "while", "as", "and", "or", "but", "not"
    }
    words = text_clean.split()
    if len(words) >= 2:
        second_word = words[1].lower()
        if second_word in non_verb_second_words:
            subject = words[0]
            verb = words[0]
            object_noun = " ".join(words[1:]) if len(words) > 1 else None
        else:
            subject = words[0]
            verb = words[1]
            object_noun = " ".join(words[2:]) if len(words) > 2 else None

        return {
            "form": "Base",
            "verb": verb.lower(),
            "subject": subject,
            "object": object_noun
        }
        
    return None
