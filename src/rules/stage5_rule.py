import re

def analyze_semantic_structure(text):
    text_clean = text.strip().rstrip(".")
    text_lower = text_clean.lower()
    
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
                    "verb": v_en,
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
            "verb": v_ing,
            "subject": subject,
            "object": object_noun if object_noun else None
        }
        
    # 3. 一般形（現在形・過去形など）の判定 (Morphology: Base)
    # 例: "I have a car"
    # 簡易パース：最初の単語を主語、2つ目を動詞、残りを目的語とみなす
    words = text_clean.split()
    if len(words) >= 2:
        subject = words[0]
        verb = words[1]
        object_noun = " ".join(words[2:]) if len(words) > 2 else None
        
        return {
            "form": "Base",
            "verb": verb,
            "subject": subject,
            "object": object_noun
        }
        
    return None
