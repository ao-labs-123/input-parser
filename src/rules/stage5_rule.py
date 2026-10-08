import re


UNSPECIFIED = "Unspecified"
PSYCHOLOGICAL_VERBS = {"think", "thought", "feel", "want", "hope", "stressed"}


def analyze_semantic_structure(text):
    text_clean = text.strip().rstrip(".!?")

    passive_match = re.search(
        r"\b(am|is|are|was|were|be|been)\b\s+([A-Za-z]+)\b(?:\s+by\s+(.+))?",
        text_clean,
        re.IGNORECASE,
    )
    if passive_match:
        verb = passive_match.group(2)
        if not verb.lower().endswith("ing") and re.search(
            r"(?:ed|en|t|d|n)$", verb, re.IGNORECASE
        ):
            return {
                "form": "Passive",
                "verb": verb.lower(),
                "actor": passive_match.group(3).strip() if passive_match.group(3) else "Unknown",
                "receiver": text_clean[:passive_match.start()].strip(),
            }

    progressive_match = re.search(
        r"\b(am|is|are|was|were)\b\s+(\w+ing)\b\s*(.*)",
        text_clean,
        re.IGNORECASE,
    )
    if progressive_match:
        return {
            "form": "Progressive",
            "verb": progressive_match.group(2).lower(),
            "subject": text_clean[:progressive_match.start()].strip(),
            "object": progressive_match.group(3).strip() or None,
        }

    be_state_match = re.search(
        r"\b(am|is|are|was|were)\b\s+([A-Za-z]+)\b(?:\s+(.*))?",
        text_clean,
        re.IGNORECASE,
    )
    if be_state_match:
        subject = text_clean[:be_state_match.start()].strip()
        state_value = be_state_match.group(2).lower()
        result = {
            "form": "State",
            "state": state_value,
            "subject": subject,
            "object": be_state_match.group(3).strip() if be_state_match.group(3) else None,
        }
        psych_match = subject.split()[0].lower() if subject else ""
        if psych_match in PSYCHOLOGICAL_VERBS:
            result["psychological_verb"] = psych_match
            result["verb"] = None
        else:
            result["verb"] = state_value
        return result

    non_verb_second_words = {
        "a", "an", "the", "to", "in", "on", "at", "of", "by", "for", "with",
        "from", "into", "onto", "after", "before", "because", "despite", "although",
        "though", "if", "when", "while", "as", "and", "or", "but", "not"
    }
    words = text_clean.split()
    if len(words) >= 2:
        if words[1].lower() in non_verb_second_words:
            verb = words[0].lower()
            object_value = " ".join(words[1:]) or None
        else:
            verb = words[1].lower()
            object_value = " ".join(words[2:]) or None
        return {
            "form": "Base",
            "verb": verb,
            "subject": words[0],
            "object": object_value,
        }
    return None


def _temporal_phrase(text, stage3_result):
    structure = (stage3_result or {}).get("structure")
    if isinstance(structure, dict) and structure.get("relation") == "Temporal":
        context = structure.get("context")
        marker = structure.get("marker")
        if context:
            return f"{marker} {context}".strip() if marker else context

    match = re.search(
        r"\b(?:yesterday|today|tomorrow|tonight|last\s+\w+|next\s+\w+|"
        r"this\s+\w+|at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\b",
        text,
        re.IGNORECASE,
    )
    return match.group(0).strip(" ,") if match else UNSPECIFIED


def _why_phrase(text, stage3_result):
    structure = (stage3_result or {}).get("structure")
    if isinstance(structure, dict) and structure.get("cause"):
        cause = structure["cause"]
        match = re.search(
            r"\b(?:because\s+of|due\s+to|because|since)\s+[^,.!?]+",
            text,
            re.IGNORECASE,
        )
        if match:
            return match.group(0).strip(" ,")
        marker = structure.get("marker")
        return f"{marker} {cause}".strip() if marker else cause

    match = re.search(
        r"\b(?:because\s+of|due\s+to|because|since)\s+[^,.!?]+",
        text,
        re.IGNORECASE,
    )
    if match:
        return match.group(0).strip(" ,")

    goal = re.search(r"\bto\s+(?:study|learn|understand|review|finish|help|improve)\b[^,.!?]*", text, re.IGNORECASE)
    return goal.group(0).strip(" ,") if goal else UNSPECIFIED


def _where_phrase(text):
    match = re.search(
        r"\b(?P<preposition>at|in|on|to|near|inside)\s+"
        r"(?P<place>(?:(?:the|a|an)\s+)?[A-Za-z][\w'-]*"
        r"(?:\s+(?!at\b|in\b|on\b|to\b|near\b|inside\b|yesterday\b|today\b|tomorrow\b|tonight\b)"
        r"[A-Za-z][\w'-]*)?)"
        r"(?=\s+(?:at|in|on|to|near|inside|yesterday|today|tomorrow|tonight)\b|[,.!?]|$)",
        text,
        re.IGNORECASE,
    )
    if not match:
        return UNSPECIFIED
    preposition = match.group("preposition").lower()
    place = match.group("place").strip()
    if preposition == "to" and re.search(
        r"\b(?:due|thanks)\s+$", text[:match.start()], re.IGNORECASE
    ):
        return UNSPECIFIED
    if preposition == "to" and re.match(
        r"(?:study|learn|understand|review|finish|help|improve)\b", place, re.IGNORECASE
    ):
        return UNSPECIFIED
    if preposition == "to":
        return re.sub(r"^(?:the|a|an)\s+", "", place, flags=re.IGNORECASE)
    return f"{preposition} {place}"


def _how_phrase(text, stage3_result):
    structure = (stage3_result or {}).get("structure")
    if isinstance(structure, dict) and structure.get("relation") == "Manner":
        context = structure.get("context")
        marker = structure.get("marker")
        if context:
            return f"{marker} {context}".strip() if marker else context

    match = re.search(r"\bby\s+\w+ing(?:\s+\w+)*", text, re.IGNORECASE)
    if match:
        return match.group(0).strip(" ,")

    match = re.search(r"\b\w+ly\b", text, re.IGNORECASE)
    return match.group(0).strip(" ,") if match else UNSPECIFIED


def _resolved_value(sources, keys):
    for source in sources:
        if not isinstance(source, dict):
            continue
        candidates = [source, source.get("structure")]
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            for key in keys:
                value = candidate.get(key)
                if isinstance(value, str) and value.strip() and value != UNSPECIFIED:
                    return value.strip()
    return UNSPECIFIED


def _core_action(
    text, agent, semantic_result, modifiers, stage2_result, stage3_result
):
    action = text.strip().rstrip(".!?")
    action = re.sub(r"^\s*I'm\b", "I am", action, flags=re.IGNORECASE)

    formal_subject_match = re.match(
        r"^It\s+(?:is|was)\s+\S+\s+that\s+(.+)$",
        action,
        re.IGNORECASE,
    )
    if formal_subject_match:
        action = formal_subject_match.group(1)

    structure = (stage3_result or {}).get("structure")
    if isinstance(structure, dict):
        if structure.get("type") == "Non-defining":
            action = re.sub(
                r",\s*(?:who|which)\b[^,]*(?:,|$)",
                "",
                action,
                flags=re.IGNORECASE,
            )
        relative_marker = structure.get("relative_marker")
        relative_clause = structure.get("clause")
        if relative_marker and relative_clause:
            action = re.sub(
                rf"\s+{re.escape(relative_marker)}\s+{re.escape(relative_clause)}",
                "",
                action,
                flags=re.IGNORECASE,
            )
        if structure.get("kind") == "Instrument":
            action = re.sub(
                r"\s+(?:by\s+[A-Za-z]+ing(?:\s+[^,.!?]+)?|"
                r"with\s+(?:a|an|the)\s+[^,.!?]+)$",
                "",
                action,
                flags=re.IGNORECASE,
            )

    stage2_structure = (stage2_result or {}).get("structure")
    if (
        isinstance(stage2_structure, dict)
        and stage2_structure.get("relation") == "Concession"
    ):
        marker = stage2_structure.get("marker")
        concession = stage2_structure.get("concession")
        if marker and concession:
            action = re.sub(
                rf"\s+{re.escape(marker)}\s+{re.escape(concession)}$",
                "",
                action,
                flags=re.IGNORECASE,
            )

    where = modifiers[1]
    if where != UNSPECIFIED and not re.match(
        r"^(?:at|in|on|to|near|inside)\s+", where, re.IGNORECASE
    ):
        action = re.sub(
            r"\bto\s+(?:(?:the|a|an)\s+)?" + re.escape(where) + r"\b",
            "",
            action,
            flags=re.IGNORECASE,
        )

    for modifier in modifiers:
        if modifier != UNSPECIFIED:
            action = re.sub(re.escape(modifier), "", action, flags=re.IGNORECASE)

    action = re.sub(r"^\s*(?:yesterday|today|tomorrow|tonight)\s*,?\s*", "", action, flags=re.IGNORECASE)
    action = re.sub(r"^\s*please\s+", "", action, flags=re.IGNORECASE)
    action = action.strip(" ,")

    if agent not in (None, "", "Unknown", UNSPECIFIED):
        if agent.lower() == "i":
            agent_pattern = r"^\s*I(?:['’]m\s+|\s+)"
        else:
            agent_pattern = r"^\s*" + re.escape(agent) + r"\b[\s,]*"
        action = re.sub(agent_pattern, "", action, flags=re.IGNORECASE)

    if semantic_result and semantic_result.get("form") == "Progressive":
        semantic_structure = semantic_result.get("structure", {})
        progressive_parts = [
            semantic_result.get("verb") or semantic_structure.get("verb")
        ]
        progressive_object = semantic_result.get("object") or semantic_structure.get(
            "object"
        )
        if progressive_object:
            progressive_parts.append(progressive_object)
        action = " ".join(part for part in progressive_parts if part)

    if semantic_result and semantic_result.get("form") == "State":
        action = re.sub(r"^\s*(?:am|is|are|was|were)\s+", "", action, flags=re.IGNORECASE)

    if semantic_result and semantic_result.get("form") == "Passive":
        verb = semantic_result.get("verb")
        receiver = semantic_result.get("receiver")
        if verb and receiver:
            receiver = {
                "i": "me",
                "he": "him",
                "she": "her",
                "we": "us",
                "they": "them",
            }.get(receiver.lower(), receiver)
            receiver = re.sub(r"^(The|A|An)\b", lambda match: match.group(1).lower(), receiver)
            action = f"{verb} {receiver}"

    action = re.sub(r"\s+", " ", action).strip(" ,")
    if action:
        action = action[0].lower() + action[1:]
    return action or UNSPECIFIED


def synthesize_5w1h(
    text,
    stage1_result=None,
    stage2_result=None,
    stage3_result=None,
    stage4_result=None,
    semantic_result=None,
):
    """Bind resolved stage outputs into the deterministic 5W1H handoff frame."""
    stage1_result = stage1_result or {}
    agent = stage1_result.get("agent", "Unknown")
    if agent in (None, ""):
        agent = "Unknown"
    if agent == "Unknown" and re.match(r"^\s*please\s+\w+", text, re.IGNORECASE):
        agent = "you"

    if semantic_result and semantic_result.get("form") == "Passive":
        actor = semantic_result.get("actor")
        if actor and actor != "Unknown":
            agent = actor

    when = _temporal_phrase(text, stage3_result)
    where = _where_phrase(text)
    why = _why_phrase(text, stage3_result)
    how = _how_phrase(text, stage3_result)

    resolved_when = _resolved_value((stage3_result, stage4_result), ("when", "time", "temporal"))
    resolved_where = _resolved_value((stage4_result,), ("where", "location", "locative"))
    resolved_why = _resolved_value((stage2_result, stage3_result), ("why", "reason", "causal_clause"))
    resolved_how = _resolved_value((stage3_result, stage4_result), ("how", "manner", "instrument", "modal"))
    when = resolved_when if resolved_when != UNSPECIFIED else when
    where = resolved_where if resolved_where != UNSPECIFIED else where
    why = resolved_why if resolved_why != UNSPECIFIED else why
    how = resolved_how if resolved_how != UNSPECIFIED else how

    what = _core_action(
        text,
        agent,
        semantic_result,
        (when, where, why, how),
        stage2_result,
        stage3_result,
    )

    return {
        "stage": "Stage 5 - 5W1H Synthesis",
        "frame": {
            "who": agent,
            "what": what,
            "when": when,
            "where": where,
            "why": why,
            "how": how,
        },
        "status": "Ready for Particle Encapsulation",
    }