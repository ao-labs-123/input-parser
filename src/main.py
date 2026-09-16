import json
from datetime import datetime
from pathlib import Path

from rules.stage1_rule import determine_explicit_subject
from rules.stage1_rule import determine_subject
from rules.stage2_rule import analyze_causality_and_ambiguity
from rules.stage3_rule import analyze_causality
from rules.stage4_rule import analyze_modification_structure
from rules.stage5_rule import analyze_semantic_structure
from analyzer import LogicAnalyzer

def run_test(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        examples = json.load(f)
    
    from rules.stage1_rule import get_lexicon
    from rules.stage3_rule import get_lexicon
    lexicon_data = get_lexicon()
    analyzer = LogicAnalyzer(lexicon_data)

    for text in examples:
        explicit_status = determine_explicit_subject(text)
        
        if explicit_status:
            subject_status = explicit_status
        else:
            subject_status = determine_subject(text)
            
        # 因果関係の判定は主語の有無に関わらず共通で実行
        causality_status = analyze_causality(text)

        mod_res = analyze_modification_structure(text)
        sem_res = analyze_semantic_structure(text)

        stage2_res = analyze_causality_and_ambiguity(text,subject_status)

        log1 = analyzer.stage1_analyze(text, subject_status)
        log2 = analyzer.stage2_analyze(text,log1,stage2_res)
        log3 = analyzer.stage3_analyze(text, log1)
        log4 = analyzer.stage4_analyze(text, mod_res,log1)
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