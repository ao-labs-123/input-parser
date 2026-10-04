import re

def analyze_modification_structure(text):
    text_clean = text.strip()
    
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
                "clause": clause_content
            }

    # 2. 制限用法 (Defining clause) の判定: "that", "which", "who" (カンマなし)
    for m_word in ["that", "which", "who"]:
        pattern = rf"\b{m_word}\b"
        
        # 文章の中に対象の単語が単体であるか（大文字小文字を無視）
        if re.search(pattern, text_clean, flags=re.IGNORECASE):
            # カンマ付きの非制限用法ルートを先に通過しているため、ここでは単純に分割してOK
            parts = re.split(pattern, text_clean, flags=re.IGNORECASE)
            
            if len(parts) < 2:
                continue
                
            antecedent = parts[0].strip()
            
            # 主節の動詞（is, wasなど）の手前までを関係節として切り出す
            clause_parts = parts[1].split()
            clause_words = []
            for word in clause_parts:
                if word.lower() in ['is', 'was', 'are', 'were', 'has', 'have', 'done']:
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
                "clause": clause_content
            }
            
    return None
