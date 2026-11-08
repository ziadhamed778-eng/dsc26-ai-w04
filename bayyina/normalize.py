import re

def normalize_ar(text: str) -> str:
    if not text:
        return ""
        
    # 1. تحويل الحروف الإنجليزية لـ lowercase
    text = text.lower()
    
    # 2. إزالة التشكيل (U+064B–U+0652 و U+0670) وإزالة التطويل (U+0640)
    text = re.sub(r'[\u064B-\u0652\u0670\u0640]', '', text)
    
    # 3. توحيد أشكال الألف
    text = re.sub(r'[أإآٱ]', 'ا', text)
    
    # 4. توحيد الياء والتاء المربوطة (ملاحظة: ؤ و ئ بيفضلوا زي ما هما بناءً على التعليمات)
    text = text.replace('ى', 'ي').replace('ة', 'ه')
    
    # 5. تحويل الأرقام العربية والفارسية إلى أرقام إنجليزية (0-9)
    ar_digits = '٠١٢٣٤٥٦٧٨٩'
    fa_digits = '۰۱۲۳۴۵۶۷۸۹'
    en_digits = '0123456789'
    trans = str.maketrans(ar_digits + fa_digits, en_digits + en_digits)
    text = text.translate(trans)
    
    # 6. دمج المسافات المتكررة في مسافة واحدة وإزالة المسافات من الأطراف
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def tokenize(text: str) -> list[str]:
    # 1. تنظيف النص أولاً
    norm_text = normalize_ar(text)
    
    # 2. استخراج الكلمات (بما فيها الكلمات الفرانكو والأرقام) باستخدام Regex \w+
    return re.findall(r'\w+', norm_text)