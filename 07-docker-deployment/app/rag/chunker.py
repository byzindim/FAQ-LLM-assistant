import re

def markdown_chunker(text: str, source: str) -> list[dict]:
    """
    Разбивает markdown на чанки по заголовкам # и ## и параграфам.
    Сохраняет метаданные: источник и заголовок раздела.
    """
    chunks = []
    
    # 🔥 ИСПРАВЛЕНО: Поддерживаем оба типа заголовков (# и ##)
    # Разделяем текст по заголовкам # или ##
    sections = re.split(r'\n(?=#{1,2} )', text)
    
    current_header = "Общая информация"
    
    for section in sections:
        if not section.strip():
            continue
            
        # 🔥 ИСПРАВЛЕНО: Извлекаем заголовок # или ##
        header_match = re.match(r'^#{1,2}\s+(.+)', section)
        if header_match:
            current_header = header_match.group(1).strip()
            section = section[header_match.end():].strip()
            
        # Разбиваем секцию на параграфы (по двойному переносу строки)
        paragraphs = re.split(r'\n\s*\n', section)
        
        current_chunk = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # Если добавление параграфа превысит лимит (800 символов) - сохраняем чанк
            if len(current_chunk) + len(para) > 800 and current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "source": source,
                    "header": current_header
                })
                current_chunk = para + "\n\n"
            else:
                current_chunk += para + "\n\n"
                
        # Сохраняем последний кусок в секции
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "source": source,
                "header": current_header
            })
            
    return chunks
