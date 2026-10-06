import re

if __package__ == "src":
    from .rules.stage5_rule import synthesize_5w1h
else:
    from rules.stage5_rule import synthesize_5w1h


class LogicAnalyzer:
    def __init__(self, lexicon_data):
        self.lexicon = lexicon_data

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

        def add_action_mapping(relation_mapping):
            if not action:
                return relation_mapping
            action_phrase = action["verb"]
            if action["patient"]:
                action_phrase = f"{action_phrase} {action['patient']}"
            action_mapping = f"{action['actor']} -> Action -> {action_phrase}"
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
            return {
                "process": f"Concessive Marker: {marker}",
                "decision": "Concessive relation mapped",
                "mapping": add_action_mapping(
                    f"{concession} -> Concession -> {outcome}"
                ),
                "structure": structure,
                "agent": agent,
                "action": action,
            }

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
            result = {
                "process": f"Causal Marker: {marker}",
                "decision": "Causal relation mapped",
                "mapping": add_action_mapping(f"{cause} -> Causes -> {effect}"),
                "structure": structure,
                "agent": agent,
                "action": action,
            }
        else:
            decision = "Clarification Required (Undetermined Agent)" if agent == "Unknown" else "No causal relation found"
            result = {
                "process": "No causal relation found",
                "decision": decision,
                "mapping": add_action_mapping("None"),
                "structure": None,
                "agent": agent,
                "action": action,
            }
        return result

    def stage3_analyze(self, text, stage1_result, modification_result=None):
        agent = (stage1_result or {}).get("agent", "Unknown")
        if not modification_result:
            return {
                "process": "No modification structure found",
                "decision": "Standard",
                "structure": None,
                "agent": agent,
            }

        modification_type = modification_result.get("type")
        if modification_type == "Non-defining":
            decision = "Supplementary"
            process = "Non-defining clause"
        elif modification_type == "Defining":
            decision = "Essential"
            process = "Defining clause"
        else:
            return {
                "process": "Unrecognized modification structure",
                "decision": "Unspecified",
                "structure": modification_result,
                "agent": agent,
            }

        return {
            "process": process,
            "decision": decision,
            "target": modification_result.get("antecedent", "Unspecified"),
            "modifier": modification_result.get("clause", "Unspecified"),
            "structure": modification_result,
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

