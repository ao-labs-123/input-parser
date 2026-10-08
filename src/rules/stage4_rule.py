import re

PSYCHOLOGICAL_VERBS = {"think", "thought", "feel", "want", "hope", "stressed"}
STATE_PREDICATES = {"bright", "done", "quiet", "required", "stressed"}
TEMPORAL_AND_ADJUNCT_MARKERS = (
    "because of", "due to", "thanks to", "yesterday", "tomorrow", "tonight",
    "because", "despite", "although", "though", "after", "before", "at",
    "in", "on", "with", "by",
)


def _direct_object(value, verb):
    if not value:
        return None

    markers = TEMPORAL_AND_ADJUNCT_MARKERS
    if verb.lower() in {"go", "goes", "went", "travel", "traveled", "walk", "walked"}:
        markers = (*markers, "to")
    marker_pattern = "|".join(
        re.escape(marker) for marker in sorted(markers, key=len, reverse=True)
    )
    direct_object = re.split(
        rf"\b(?:{marker_pattern})\b",
        value,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0].strip(" ,")
    return direct_object or None


def analyze_semantic_structure(text):
    text_clean = text.strip().rstrip(".")
    text_clean = re.sub(r"\bI'm\b", "I am", text_clean, flags=re.IGNORECASE)
    formal_subject_match = re.match(
        r"^It\s+(?:is|was)\s+\S+\s+that\s+(.+)$",
        text_clean,
        re.IGNORECASE,
    )
    if formal_subject_match:
        text_clean = formal_subject_match.group(1)
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
        is_participle = v_en.lower().endswith(("ed", "en")) or v_en.lower() in {
            "built", "left", "made", "sent", "told", "written"
        }

        if (
            is_participle
            and (by_actor or v_en.lower() not in STATE_PREDICATES)
        ):
            idx = text_clean.lower().find(be_verb.lower())
            receiver = text_clean[:idx].strip()
            return {
                "form": "Passive",
                "verb": v_en.lower(),
                "actor": by_actor.strip() if by_actor else "Unknown",
                "receiver": receiver,
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
            object_noun = _direct_object(" ".join(words[1:]), verb)
        else:
            subject = words[0]
            verb = words[1]
            object_noun = _direct_object(" ".join(words[2:]), verb)

        return {
            "form": "Base",
            "verb": verb.lower(),
            "subject": subject,
            "object": object_noun
        }
        
    return None
