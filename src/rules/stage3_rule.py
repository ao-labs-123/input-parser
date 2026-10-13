import re

THAT_COMPLEMENT_PREDICATES = {
    "assume", "assumed", "believe", "believed", "feel", "felt", "guess",
    "guessed", "hear", "heard", "hope", "hoped", "know", "knew", "realize",
    "realized", "say", "said", "see", "saw", "suppose", "supposed", "think",
    "thought", "understand", "understood",
}
BE_FORMS = {"am", "is", "are", "was", "were", "be", "been", "being"}
HAVE_FORMS = {"have", "has", "had"}
IRREGULAR_PAST_FORMS = {
    "bought", "brought", "built", "came", "did", "felt", "found", "gave",
    "got", "heard", "held", "knew", "left", "made", "met", "ran", "read",
    "said", "saw", "sent", "told", "took", "went", "wrote",
}
RELATIVE_SUBJECT_PATTERN = re.compile(
    r"^(?:[Ii]|[Yy]ou|[Hh]e|[Ss]he|[Tt]hey|[Ww]e|[Ii]t|[Tt]he|[Aa]|[Aa]n|"
    r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b"
)


def _is_finite_predicate(word, previous_word):
    normalized = word.strip(".,!?;:").lower()
    previous = previous_word.strip(".,!?;:").lower()
    if normalized in BE_FORMS or normalized in HAVE_FORMS or normalized in {"do", "does", "did"}:
        return True
    if previous in BE_FORMS or previous in HAVE_FORMS:
        return False
    return normalized in IRREGULAR_PAST_FORMS or normalized.endswith("ed")


def _extract_target(antecedent):
    target_match = re.search(
        r"\b(?:to|with|for|of|in|on|at)\s+(?:the|a|an)\s+"
        r"([A-Za-z]+(?:\s+(?!(?:to|with|for|of|in|on|at|from|the|a|an|and|or)\b)[A-Za-z]+)?)",
        antecedent,
        re.IGNORECASE,
    )
    if target_match:
        return target_match.group(1)
    return antecedent


def analyze_modification_structure(text):
    text_clean = text.strip()

    if re.match(
        r"^It\s+(?:is|was)\s+\S+\s+that\b",
        text_clean,
        re.IGNORECASE,
    ):
        return None
    
    # 1. 非制限用法 (Non-defining clause) の判定: ", which" や ", who"
    for marker in [", which", ", who", ",which", ",who"]:
        if marker in text_clean.lower():
            idx = text_clean.lower().find(marker)
            antecedent = text_clean[:idx].strip()
            remaining = text_clean[idx + len(marker):].strip()
            
            # 次のカンマかピリオドの手前までを節の中身とする
            clause_content = remaining.split(",")[0].replace(".", "").strip()
            
            return {
                "type": "Non-defining",
                "antecedent": antecedent,
                "target": _extract_target(antecedent),
                "clause": clause_content
            }

    # 2. 制限用法 (Defining clause) の判定: relative clauses without a comma
    for m_word in ["that", "which", "who", "where"]:
        pattern = rf"\b{m_word}\b"
        
        # 文章の中に対象の単語が単体であるか（大文字小文字を無視）
        if re.search(pattern, text_clean, flags=re.IGNORECASE):
            # カンマ付きの非制限用法ルートを先に通過しているため、ここでは単純に分割してOK
            parts = re.split(pattern, text_clean, flags=re.IGNORECASE)
            
            if len(parts) < 2:
                continue
                
            antecedent = parts[0].strip()
            antecedent_words = antecedent.lower().split()
            is_that_complement = (
                m_word == "that"
                and antecedent_words
                and (
                    antecedent_words[-1] in THAT_COMPLEMENT_PREDICATES
                    or (
                        len(antecedent_words) > 1
                        and antecedent_words[-2] in BE_FORMS
                    )
                )
            )
            if is_that_complement:
                continue
            
            # 主節の動詞（is, wasなど）の手前までを関係節として切り出す
            clause_parts = parts[1].split()
            clause_words = []
            explicit_subject = bool(
                clause_parts and RELATIVE_SUBJECT_PATTERN.match(clause_parts[0])
            )
            finite_predicate_seen = False
            previous_word = ""
            for index, word in enumerate(clause_parts):
                if explicit_subject and index > 0:
                    if _is_finite_predicate(word, previous_word):
                        is_coordinated_predicate = previous_word.lower() in {
                            "and", "or",
                        }
                        if finite_predicate_seen and not is_coordinated_predicate:
                            break
                        finite_predicate_seen = True
                    clause_words.append(word)
                    previous_word = word
                    continue

                is_clause_initial_copula = index == 0 and word.lower() in {
                    "is", "was", "are", "were"
                }
                if word.lower() in ["is", "was", "are", "were", "has", "have", "done"] and not is_clause_initial_copula:
                    break
                clause_words.append(word)
                
            clause_content = " ".join(clause_words).replace(".", "").strip()
            
            # analyzer側の判定に合わせるため、小文字の "i" を大文字の "I" に補正
            if clause_content == "i" or clause_content.startswith("i "):
                clause_content = "I" + clause_content[1:]
            clause_content = clause_content.replace(" i ", " I ")
            
            return {
                "type": "Defining",
                "antecedent": antecedent,
                "target": _extract_target(antecedent),
                "clause": clause_content,
                "kind": "RelativeClause",
                "relative_marker": m_word,
            }

    # 3. Pre-nominal adjectives are supplementary attributes, not target IDs.
    adjective_match = re.search(
        r"\b(?:the|a|an)\s+((?:(?:very|extremely|quite|really)\s+)?"
        r"[A-Za-z]+)\s+([A-Za-z]+)\b",
        text_clean,
        re.IGNORECASE,
    )
    known_adjectives = {
        "angry", "complex", "difficult", "frustrated", "happy", "hard",
        "important", "large", "long", "new", "old", "quiet", "sad",
        "small", "strange",
    }
    if adjective_match and adjective_match.group(1).split()[-1].lower() in known_adjectives:
        adjective = adjective_match.group(1)
        noun = adjective_match.group(2)
        return {
            "type": "Supplementary",
            "antecedent": noun,
            "target": noun,
            "clause": adjective,
            "kind": "Adjective",
        }

    instrument_match = re.search(
        r"\b(?:by\s+(?P<gerund>[A-Za-z]+ing(?:\s+[^,.!?]+)?)|"
        r"with\s+(?P<tool>(?:a|an|the)\s+[^,.!?]+))[.!?]*$",
        text_clean,
        re.IGNORECASE,
    )
    if instrument_match:
        event = text_clean[:instrument_match.start()].strip()
        event_match = re.match(
            r"^(?P<actor>I|You|He|She|They|We|[A-Z][a-z]+)\s+"
            r"(?P<verb>[A-Za-z]+)\b",
            event,
        )
        if event_match:
            verb = event_match.group("verb")
            outcomes = {
                "succeed": ("Success", "State"),
                "succeeded": ("Success", "State"),
                "fail": ("Failure", "State"),
                "failed": ("Failure", "State"),
                "opened": ("Open", "Action"),
            }
            outcome, outcome_kind = outcomes.get(
                verb.lower(), (verb.capitalize(), "Action")
            )
            instrument = (
                instrument_match.group("gerund") or instrument_match.group("tool")
            ).strip()
            instrument = re.sub(
                r"^working\s+hard$", "hard work", instrument, flags=re.IGNORECASE
            )
            instrument = " ".join(word.capitalize() for word in instrument.split())
            return {
                "type": "Supplementary",
                "antecedent": event,
                "target": outcome,
                "clause": instrument,
                "kind": "Instrument",
                "actor": event_match.group("actor"),
                "outcome": outcome,
                "outcome_kind": outcome_kind,
                "instrument": instrument,
            }

    adverb_match = re.search(
        r"\b(?P<adverb>[A-Za-z]+ly)[.!?]*$", text_clean, re.IGNORECASE
    )
    if adverb_match:
        adverb = adverb_match.group("adverb")
        event = text_clean[:adverb_match.start()].strip(" ,")
        degree_adverbs = {"apparently", "seemingly", "possibly", "probably"}
        if adverb.lower() in degree_adverbs:
            state_match = re.search(
                r"\b(?:am|is|are|was|were)\s+(?P<state>[A-Za-z]+)$",
                event,
                re.IGNORECASE,
            )
            if state_match:
                state = state_match.group("state")
                return {
                    "type": "Supplementary",
                    "antecedent": state,
                    "target": state,
                    "clause": adverb,
                    "kind": "Degree",
                }
        else:
            passive_match = re.match(
                r"^(?P<target>.+?)\s+(?:am|is|are|was|were)\s+"
                r"(?P<verb>[A-Za-z]+)$",
                event,
                re.IGNORECASE,
            )
            if passive_match:
                verb = passive_match.group("verb")
                action = {"completed": "Complete"}.get(
                    verb.lower(), verb.capitalize()
                )
                return {
                    "type": "Supplementary",
                    "antecedent": passive_match.group("target"),
                    "target": passive_match.group("target"),
                    "clause": adverb,
                    "kind": "Manner",
                    "action": action,
                }
            
    return None
