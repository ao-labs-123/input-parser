import json
import re
from datetime import datetime
from pathlib import Path

from rules.stage1_rule import determine_explicit_subject
from rules.stage1_rule import determine_subject
from rules.stage2_rule import analyze_causality_and_ambiguity
from rules.stage4_rule import analyze_modification_structure
from rules.stage5_rule import analyze_semantic_structure
from analyzer import LogicAnalyzer

def run_test(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        input_data = json.load(f)

    stage_name, examples = next(iter(input_data.items()))
    target_stage = int(re.search(r"\d+", stage_name).group())
    
    from rules.stage1_rule import get_lexicon
    from rules.stage3_rule import get_lexicon
    lexicon_data = get_lexicon()
    analyzer = LogicAnalyzer(lexicon_data)

    for text in examples:
        log1 = log2 = log3 = log4 = log5 = None

        if target_stage >= 1:
            explicit_status = determine_explicit_subject(text)
            subject_status = explicit_status or determine_subject(text)
            log1 = analyzer.stage1_analyze(text, subject_status)

        if target_stage >= 2:
            stage2_res = analyze_causality_and_ambiguity(text, subject_status)
            log2 = analyzer.stage2_analyze(text, log1, stage2_res)

        if target_stage >= 3:
            log3 = analyzer.stage3_analyze(text, log1)

        if target_stage >= 4:
            mod_res = analyze_modification_structure(text)
            log4 = analyzer.stage4_analyze(text, mod_res, log1)

        if target_stage >= 5:
            sem_res = analyze_semantic_structure(text)
            log5 = analyzer.stage5_analyze(text, sem_res, log1)

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
    examples_dir = Path(__file__).resolve().parent.parent / "data" / "examples"
    for input_file in sorted(examples_dir.glob("stage*_input.json")):
        run_test(input_file)