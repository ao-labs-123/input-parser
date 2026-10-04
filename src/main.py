import json
from datetime import datetime
from pathlib import Path

if __package__:
    from .rules.stage1_rule import (
        determine_explicit_subject,
        determine_subject,
        get_lexicon,
    )
    from .rules.stage2_rule import analyze_causality_and_ambiguity, analyze_context_relation
    from .rules.stage3_rule import analyze_modification_structure
    from .rules.stage4_rule import analyze_semantic_structure
    from .analyzer import LogicAnalyzer
else:
    from rules.stage1_rule import (
        determine_explicit_subject,
        determine_subject,
        get_lexicon,
    )
    from rules.stage2_rule import analyze_causality_and_ambiguity, analyze_context_relation
    from rules.stage3_rule import analyze_modification_structure
    from rules.stage4_rule import analyze_semantic_structure
    from analyzer import LogicAnalyzer


def _extract_examples(input_data):
    if isinstance(input_data, list):
        examples = input_data
    elif isinstance(input_data, dict):
        examples = []
        for category, category_examples in input_data.items():
            if not isinstance(category_examples, list):
                raise ValueError(f"Examples for {category!r} must be a JSON array.")
            examples.extend(category_examples)
    else:
        raise ValueError("Examples JSON must be an array of strings or an object of arrays.")

    if not all(isinstance(example, str) for example in examples):
        raise ValueError("Every example must be a string.")
    return examples


def run_test(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        input_data = json.load(f)

    examples = _extract_examples(input_data)
    analyzer = LogicAnalyzer(get_lexicon())

    for text in examples:
        log1 = log2 = log3 = log4 = log5 = None

        explicit_status = determine_explicit_subject(text)
        subject_status = explicit_status or determine_subject(text)
        log1 = analyzer.stage1_analyze(text, subject_status)

        stage2_res = analyze_causality_and_ambiguity(text, subject_status)
        context_res = analyze_context_relation(text)
        log2 = analyzer.stage2_analyze(text, log1, stage2_res, context_res)

        mod_res = analyze_modification_structure(text)
        log3 = analyzer.stage3_analyze(text, log1, mod_res)

        sem_res = analyze_semantic_structure(text)
        log4 = analyzer.stage4_analyze(text, sem_res, log1)

        log5 = analyzer.stage5_analyze(
            text,
            sem_res,
            log1,
            stage2_result=log2,
            stage3_result=log3,
            stage4_result=log4,
        )

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "input": text,
            "stage1": log1,
            "stage2": log2,
            "stage3": log3,
            "stage4": log4,
            "stage5": log5
        }

        append_log_entry(log_entry)


def reset_log_file():
    log_file_path = Path(__file__).resolve().parent.parent / "data" / "log.json"
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    with log_file_path.open("w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)


def append_log_entry(log_entry):
    log_file_path = Path(__file__).resolve().parent.parent / "data" / "log.json"
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    existing_logs = []
    if log_file_path.exists() and log_file_path.stat().st_size > 0:
        try:
            with log_file_path.open("r", encoding="utf-8") as f:
                existing_logs = json.load(f)
        except json.JSONDecodeError:
            existing_logs = []

    existing_logs.append(log_entry)
    with log_file_path.open("w", encoding="utf-8") as f:
        json.dump(existing_logs, f, ensure_ascii=False, indent=4)
        
if __name__ == "__main__":
    reset_log_file()
    examples_dir = Path(__file__).resolve().parent.parent / "data" / "examples"
    run_test(examples_dir / "all_examples.json")