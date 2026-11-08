from bayyina.types import Chunk

def chunk_text(doc_id: str, text: str, max_chars: int = 500, overlap: int = 50) -> list[Chunk]:
    if max_chars <= 0 or not (0 <= overlap < max_chars):
        raise ValueError("Invalid max_chars or overlap")
    
    if not text or text.isspace():
        return []
        
    chunks = []
    s = 0
    chunk_idx = 0
    
    # تجاوز أي مسافات فارغة في بداية النص
    while s < len(text) and text[s].isspace():
        s += 1
        
    while s < len(text):
        if len(text) - s <= max_chars:
            c = len(text) - s
            cut_point = s + c
        else:
            window = text[s : s + max_chars]
            c = max_chars
            
            found = False
            # 1. البحث عن نهاية براجراف (\n\n) في النصف الثاني من النافذة
            for i in range(max_chars, max_chars // 2 - 1, -1):
                if i >= 2 and window[i-2:i] == "\n\n":
                    c = i
                    found = True
                    break
            
            # 2. البحث عن نهاية جملة
            if not found:
                sent_ends = set(".!?؟۔\n")
                for i in range(max_chars, max_chars // 2 - 1, -1):
                    if i >= 1 and window[i-1] in sent_ends:
                        c = i
                        found = True
                        break
                        
            # 3. البحث عن مسافة
            if not found:
                for i in range(max_chars, max_chars // 2 - 1, -1):
                    if i >= 1 and window[i-1].isspace():
                        c = i
                        found = True
                        break
                        
            cut_point = s + c
            
        chunk_text_str = text[s:cut_point].rstrip()
        if chunk_text_str:
            chunks.append(Chunk(
                doc_id=doc_id,
                chunk_id=f"{doc_id}#{chunk_idx}",
                start=s,
                end=s + len(chunk_text_str),
                text=chunk_text_str
            ))
            chunk_idx += 1
            
        if cut_point == len(text):
            break
            
        # تحديد بداية الفقرة التالية (التداخل - Overlap)
        is_mid_word = not text[cut_point - 1].isspace() and not text[cut_point].isspace()
        
        s_next = cut_point - overlap
        if s_next <= s:
            s_next = s + 1 # ضمان التقدم للأمام دائماً
            
        # إذا لم يكن القطع من منتصف كلمة، فيجب ألا تبدأ الفقرة الجديدة من منتصف كلمة
        if not is_mid_word:
            while s_next < cut_point and s_next > 0 and not text[s_next - 1].isspace():
                s_next += 1
                
        # تجاوز المسافات الفارغة لبداية الفقرة الجديدة
        while s_next < len(text) and text[s_next].isspace():
            s_next += 1
            
        s = s_next
        
    return chunks