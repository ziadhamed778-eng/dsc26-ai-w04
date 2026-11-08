from bayyina.types import Hit

def verify_citation(quote: str, document: str, start: int, end: int) -> bool:
    # 1. التأكد من صحة الحدود
    if not (0 <= start < end <= len(document)):
        return False
        
    # 2. التأكد إن الاقتباس مش فارغ
    if not quote or not quote.strip():
        return False
        
    # 3. توحيد المسافات (Collapsed Whitespace)
    collapsed_quote = " ".join(quote.split())
    collapsed_doc_span = " ".join(document[start:end].split())
    
    # 4. التأكد إن الاقتباس موجود داخل النطاق المحدد
    return collapsed_quote in collapsed_doc_span

def format_citation(hit: Hit, max_quote: int = 160) -> str:
    # 1. توحيد المسافات
    collapsed_quote = " ".join(hit.text.split())
    
    # 2. قص النص إذا كان أطول من الحد الأقصى
    if len(collapsed_quote) > max_quote:
        # أخذ أول max_quote حروف
        truncated = collapsed_quote[:max_quote]
        # التراجع لأخر مسافة
        last_space_idx = truncated.rfind(" ")
        
        if last_space_idx != -1:
            truncated = truncated[:last_space_idx]
            
        collapsed_quote = truncated + "…"
        
    # 3. بناء الشكل النهائي: [doc_id:start-end] "quote"
    return f'[{hit.doc_id}:{hit.start}-{hit.end}] "{collapsed_quote}"'