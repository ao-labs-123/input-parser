import re

if __package__ == "src":
    from .rules.stage5_rule import synthesize_5w1h
else:
    from rules.stage5_rule import synthesize_5w1h


class LogicAnalyzer:
    STATIVE_VERBS = {
        "have",
        "has",
        "had",
        "know",
        "knows",
        "knew",
        "love",
        "loves",
        "like",
        "likes",
        "understand",
        "understands",
        "understood",
    }
    STATE_LIKE_WORDS = {
        "am",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "stressed",
        "angry",
        "happy",
        "sad",
        "afraid",
        "tired",
        "worried",
        "upset",
        "confused",
        "strange",
        "ready",
        "late",
        "down",
        "sick",
        "broken",
        "nervous",
    }

    def __init__(self, lexicon_data):
        self.lexicon = lexicon_data

    def _normalize_subject_prefix(self, text):
        text = text.strip()
        patterns = [
            (r"^(i|you|he|she|they|we|it)'m\b", r"\1", True),
            (r"^(i|you|he|she|they|we|it)'re\b", r"\1", True),
            (r"^(i|you|he|she|they|we|it)'s\b", r"\1", True),
            (r"^(i|you|he|she|they|we|it)\s+am\b", r"\1", True),
            (r"^(i|you|he|she|they|we|it)\s+are\b", r"\1", True),
            (r"^(i|you|he|she|they|we|it)\s+is\b", r"\1", True),
            (r"^(i|you|he|she|they|we|it)\s+was\b", r"\1", True),
            (r"^(i|you|he|she|they|we|it)\s+were\b", r"\1", True),
        ]
        for pattern, replacement, _ in patterns:
            text, count = re.subn(pattern, replacement, text, flags=re.IGNORECASE)
            if count:
                break
        return text

    def _split_actor_and_event(self, phrase):
        normalized = self._normalize_subject_prefix(phrase)
        match = re.match(
            r"^(I|You|He|She|They|We|It|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b\s*(.*)$",
            normalized,
        )
        if not match:
            return None, normalized.strip()
        actor = match.group(1)
        event = match.group(2).strip()
        return actor, event

    def _classify_mapping_label(self, phrase):
        normalized = self._normalize_subject_prefix(phrase).strip()
        lower = normalized.lower()
        if re.match(r"^(?:am|is|are|was|were|be)\b", lower):
            return "State"
        if any(
            re.search(rf"\b{re.escape(word)}\b", lower)
            for word in self.STATE_LIKE_WORDS
        ):
            return "State"
        return "Action"

    def stage1_analyze(self, text, subject_result):
        if isinstance(subject_result, dict) and subject_result.get("structure_type") == "FormalSubject":
            true_agent = subject_result.get("true_agent") or "Unknown"
            predicate = subject_result.get("predicate", "")
            that_clause = subject_result.get("that_clause", "")
            return {
                "process": "Formal Subject Detected (It ... that)",
                "decision": "Priority: True Subject in Clause",
                "agent": true_agent,
                "structure": f"It is [{predicate}] that [{that_clause}]",
            }

        if isinstance(subject_result, str) and subject_result not in ("", "Unknown", "Neutral"):
            if subject_result in ("Imperative", "Listener"):
                return {
                    "process": "Imperative / Direct Directive",
                    "decision": "Priority: Listener Address",
                    "agent": "You",
                }
            if subject_result == "Third-Person":
                return {
                    "process": "Null Subject + Evidential / Attribution Marker",
                    "decision": "Override: Third Person",
                    "agent": "He/She/They",
                }
            if subject_result == "First-Person":
                return {
                    "process": "Psychological Verb + Null Subject",
                    "decision": "Default: Speaker",
                    "agent": "I",
                }
            return {
                "process": "Explicit Subject Present",
                "decision": "Priority: Explicit Subject",
                "agent": subject_result,
            }

        if re.match(r"^\s*please\b", text, re.IGNORECASE):
            return {
                "process": "Imperative / Direct Directive",
                "decision": "Priority: Listener Address",
                "agent": "You",
            }

        return {
            "process": "Null Subject + No Core Markers Detected",
            "decision": "Fallback: Undetermined Agent",
            "agent": "Unknown",
            "action_required": "Trigger Stage 1 Clarification / Context Resolution",
        }

    def stage2_analyze(
        self,
        text,
        stage1_result,
        stage2_rule_result,
        context_result=None,
        semantic_result=None,
    ):
        stage1_result = stage1_result or {}
        rule_result = stage2_rule_result or {}
        agent = stage1_result.get("agent", "Unknown")
        state_value = (
            semantic_result.get("state")
            if semantic_result and semantic_result.get("form") == "State"
            else None
        )
        state_event = bool(state_value and not semantic_result.get("verb"))
        action = None
        if semantic_result and semantic_result.get("verb"):
            form = semantic_result.get("form")
            patient = (
                semantic_result.get("receiver")
                if form == "Passive"
                else semantic_result.get("object")
            )
            relation_markers = rule_result.get("markers", []) + rule_result.get(
                "concession_markers", []
            )
            if patient and any(
                re.search(rf"(?<!\w){re.escape(marker)}(?!\w)", patient, re.IGNORECASE)
                for marker in relation_markers
            ):
                patient = None
            action = {
                "verb": semantic_result["verb"],
                "actor": (
                    semantic_result.get("actor", "Unknown")
                    if form == "Passive"
                    else agent
                ),
                "patient": patient,
            }
            if (
                agent == "Unknown"
                and semantic_result.get("subject")
                and semantic_result["subject"].lower() == action["verb"].lower()
            ):
                action = None
            if (
                form == "Passive"
                and semantic_result["verb"].lower() in self.STATE_LIKE_WORDS
                and semantic_result.get("receiver") == agent
            ):
                action["actor"] = agent
                action["patient"] = None
            invalid_action_words = {
                "a", "an", "the", "in", "on", "at", "to", "of", "by", "after"
            }
            relation_markers = rule_result.get("markers", []) + rule_result.get(
                "concession_markers", []
            )
            if action is not None and (
                action["verb"].lower() in invalid_action_words
                or any(
                    action["verb"].lower() == marker.lower().split()[0]
                    for marker in relation_markers
                )
            ):
                action = None
            elif action is not None and context_result:
                context_marker = context_result.get("marker")
                if context_marker and patient and re.search(
                    rf"(?<!\w){re.escape(context_marker)}(?!\w)",
                    patient,
                    re.IGNORECASE,
                ):
                    action["patient"] = None

        event_info = None
        event_category = None
        if state_event:
            event_category = "State"
            event_info = {
                "category": event_category,
                "verb": None,
                "actor": agent,
                "patient": None,
                "state": state_value,
            }
        elif action:
            verb = action["verb"]
            if semantic_result.get("form") == "State" or verb.lower() in self.STATE_LIKE_WORDS:
                event_category = "State"
            elif (
                semantic_result.get("form") != "Progressive"
                and verb.lower() in self.STATIVE_VERBS
            ):
                event_category = "Stative"
            else:
                event_category = "Action"
            event_info = {
                "category": event_category,
                "verb": verb,
                "actor": action["actor"],
                "patient": action["patient"],
            }
            if event_category == "State":
                event_info["state"] = verb

        def add_event_decision(decision):
            if event_category:
                return f"{decision}; Event classified: {event_category}"
            return decision

        def add_action_mapping(relation_mapping):
            if not action:
                if state_event:
                    state_mapping = f"{agent} -> State -> {state_value}"
                    if relation_mapping == "None":
                        return state_mapping
                    return f"{relation_mapping}; {state_mapping}"
                return relation_mapping
            action_phrase = action["verb"]
            if action["patient"]:
                action_phrase = f"{action_phrase} {action['patient']}"
            actor, event = self._split_actor_and_event(action_phrase)
            if actor:
                action_phrase = event or action_phrase
                action_actor = actor
            else:
                action_actor = action["actor"]
            action_label = event_category
            action_mapping = f"{action_actor} -> {action_label} -> {action_phrase}"
            if relation_mapping == "None":
                return action_mapping
            return f"{relation_mapping}; {action_mapping}"

        concession_markers = rule_result.get("concession_markers", [])
        concession_match = None

        for marker in sorted(concession_markers, key=len, reverse=True):
            concession_match = re.search(
                rf"(?<!\w){re.escape(marker)}(?!\w)",
                text,
                re.IGNORECASE,
            )
            if concession_match:
                break

        if concession_match:
            marker = concession_match.group(0)
            outcome = text[:concession_match.start()].strip(" ,")
            concession = text[concession_match.end():].strip(" ,.!?")
            structure = {
                "relation": "Concession",
                "marker": marker,
                "concession": concession,
                "outcome": outcome,
            }
            if event_info:
                structure["event"] = event_info
            result = {
                "process": f"Concessive Marker: {marker}"
                + (f"; Event: {event_category}" if event_category else ""),
                "decision": add_event_decision("Concessive relation mapped"),
                "mapping": add_action_mapping(
                    f"{concession} -> Concession -> {outcome}"
                ),
                "structure": structure,
                "agent": agent,
                "action": action,
            }
            if context_result:
                result["context"] = context_result
            return result

        markers = rule_result.get("markers", [])
        marker_match = None

        for marker in sorted(markers, key=len, reverse=True):
            marker_match = re.search(
                rf"(?<!\w){re.escape(marker)}(?!\w)",
                text,
                re.IGNORECASE,
            )
            if marker_match:
                break

        if marker_match:
            marker = marker_match.group(0)
            before = text[:marker_match.start()].strip(" ,")
            after = text[marker_match.end():].strip(" ,.!?")
            if before:
                effect = before
                cause = after
            else:
                separator = re.search(r"[,;]", after)
                if separator:
                    cause = after[:separator.start()].strip(" ,")
                    effect = after[separator.end():].strip(" ,")
                else:
                    cause = after
                    effect = ""

            structure = {
                "relation": "CauseEffect",
                "marker": marker,
                "cause": cause,
                "effect": effect,
            }
            if event_info:
                structure["event"] = event_info
            result = {
                "process": f"Causal Marker: {marker}"
                + (f"; Event: {event_category}" if event_category else ""),
                "decision": add_event_decision("Causal relation mapped"),
                "mapping": add_action_mapping(f"{cause} -> Cause -> {effect}"),
                "structure": structure,
                "agent": agent,
                "action": action,
            }
        else:
            decision = (
                "Clarification Required (Undetermined Agent)"
                if agent == "Unknown"
                else "No causal relation"
            )
            result = {
                "process": f"Event: {event_category}"
                if event_category
                else "No causal relation found",
                "decision": add_event_decision(decision),
                "mapping": add_action_mapping("None"),
                "structure": {
                    "relation": "Event",
                    "event": event_info,
                }
                if event_info
                else None,
                "agent": agent,
                "action": action,
            }
        if context_result:
            result["context"] = context_result
        return result

    def stage3_analyze(self, text, stage1_result, modification_result=None):
        agent = (stage1_result or {}).get("agent", "Unknown")
        if not modification_result:
            return {
                "process": "No modification structure found",
                "decision": "Standard",
                "mapping": None,
                "structure": None,
                "agent": agent,
            }

        modification_type = modification_result.get("type")
        if modification_type in ("Non-defining", "Supplementary"):
            decision = "Supplementary"
            process = {
                "Adjective": "Adjectival modifier",
                "Manner": "Manner adverb",
                "Instrument": "Instrument phrase",
                "Degree": "Degree modifier",
            }.get(modification_result.get("kind"), "Non-defining clause")
        elif modification_type == "Defining":
            decision = "Essential"
            process = "Defining clause"
        else:
            return {
                "process": "Unrecognized modification structure",
                "decision": "Unspecified",
                "mapping": None,
                "structure": modification_result,
                "agent": agent,
            }

        target = modification_result.get(
            "target", modification_result.get("antecedent", "Unspecified")
        )
        modifier = modification_result.get("clause", "Unspecified")
        relative_marker = modification_result.get("relative_marker")
        modifier_subject = None
        if relative_marker == "who" or (
            relative_marker in ("which", "where")
            and re.match(r"^(?:is|was|are|were)\b", modifier, re.IGNORECASE)
        ):
            modifier_subject = target
        else:
            subject_match = re.match(
                r"^(I|You|He|She|They|We|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b",
                modifier,
            )
            if subject_match:
                modifier_subject = subject_match.group(1)

        structure = dict(modification_result)
        structure.update({
            "classification": decision,
            "target": target,
            "modifier_kind": modification_result.get("kind", "RelativeClause"),
        })

        mapping = f"Node({target})"
        modifier_kind = modification_result.get("kind")
        if modifier_kind == "Manner":
            mapping += (
                f" -> Action({modification_result['action']})"
                f" -> How: Manner({modifier.capitalize()})"
            )
        elif modifier_kind == "Instrument":
            mapping = (
                f"Agent({modification_result['actor']})"
                f" -> How: Instrument({modification_result['instrument']})"
                f" -> {modification_result['outcome_kind']}"
                f"({modification_result['outcome']})"
            )
        elif modifier_kind == "Degree":
            state = target[0].upper() + target[1:] if target else target
            mapping = (
                f"Agent({agent}) -> Internal Eval -> State({state})"
                f" -> How: Degree({modifier.capitalize()})"
            )
        elif modifier_kind == "Adjective":
            degree_match = re.match(
                r"^(very|extremely|quite|really)\s+(.+)$",
                modifier,
                re.IGNORECASE,
            )
            state = degree_match.group(2) if degree_match else modifier
            state = state[0].upper() + state[1:] if state else state
            mapping += f" -> Attribute -> State({state})"
            if degree_match:
                degree = degree_match.group(1)
                degree = degree[0].upper() + degree[1:]
                mapping += f" -> How: Degree({degree})"
        else:
            state_match = re.match(
                r"^(?:is|was|are|were)\s+(.+)$", modifier, re.IGNORECASE
            )
            if state_match:
                state = state_match.group(1)
                cause_match = re.match(
                    r"^(.+?)\s+with\s+(.+)$", state, re.IGNORECASE
                )
                if cause_match:
                    state_name = cause_match.group(1)
                    cause = cause_match.group(2)
                    state_name = state_name[0].upper() + state_name[1:]
                    mapping += (
                        f" -> Attribute -> State({state_name})"
                        f" -> Cause -> Node({cause})"
                    )
                else:
                    state = state[0].upper() + state[1:]
                    mapping += f" -> Attribute -> State({state})"
            else:
                attribute_type = (
                    "Defining Attribute" if decision == "Essential" else "Attribute"
                )
                mapping += f" -> {attribute_type} -> Clause({modifier})"

        return {
            "process": process,
            "decision": decision,
            "mapping": mapping,
            "target": target,
            "modifier": modifier,
            "attribution": {
                "target": target,
                "modifier_agent": modifier_subject or target,
                "primary_agent": agent,
            },
            "structure": structure,
            "agent": agent,
        }

    def stage4_analyze(self, text, semantic_result, stage1_result=None):
        if not semantic_result:
            return {
                "process": "No argument or verb structure found",
                "form": "Unspecified",
                "category": "Unspecified",
                "verb": "Unspecified",
                "patient": "Unspecified",
                "structure": None,
            }

        form = semantic_result.get("form", "Unspecified")
        verb = semantic_result.get("verb", "Unspecified")
        if form == "Progressive":
            category = "Action"
            process = "[Morphology: be + V-ing] → [Category: Action]"
        elif form == "Passive":
            category = "Action"
            process = "[Passive: be + V-en + by]"
        elif form == "State":
            category = "State"
            process = "[State predicate] → [Category: State]"
        else:
            stative_verbs = {"have", "has", "had", "know", "knows", "knew", "love", "loves", "like", "likes", "understand", "understands", "understood"}
            category = "Stative" if verb.lower() in stative_verbs else "Action"
            process = f"[Morphology: Base] → [Category: {category}]"

        patient = semantic_result.get("object")
        if form == "Passive":
            patient = semantic_result.get("receiver")
        patient = patient or "Unspecified"
        structure = {
            **semantic_result,
            "category": category,
            "patient": patient,
        }
        if form == "State":
            structure["state"] = semantic_result.get("state", verb)
        if stage1_result:
            structure["agent"] = stage1_result.get("agent", "Unknown")

        return {
            "process": process,
            "form": form,
            "category": category,
            "verb": verb,
            "patient": patient,
            "actor": semantic_result.get("actor", "Unspecified"),
            "receiver": semantic_result.get("receiver", "Unspecified"),
            "subject": semantic_result.get("subject", "Unspecified"),
            "structure": structure,
        }

    def stage5_analyze(
        self,
        text,
        semantic_result,
        log1,
        stage2_result=None,
        stage3_result=None,
        stage4_result=None,
    ):
        synthesis_stage3 = dict(stage3_result or {})
        stage3_structure = synthesis_stage3.get("structure")
        if not isinstance(stage3_structure, dict):
            stage3_structure = {}
        else:
            stage3_structure = dict(stage3_structure)
        context = (stage2_result or {}).get("context")
        if context:
            stage3_structure.update(context)
        if stage3_structure:
            synthesis_stage3["structure"] = stage3_structure

        return synthesize_5w1h(
            text,
            stage1_result=log1,
            stage2_result=stage2_result,
            stage3_result=synthesis_stage3,
            stage4_result=stage4_result,
            semantic_result=stage4_result or semantic_result,
        )

