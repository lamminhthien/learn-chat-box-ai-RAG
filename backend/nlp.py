import re
from dateparser import parse as parse_date

def detect_intent_and_entities(text: str):
    """
    Phát hiện intent đặt lịch, trích xuất title và datetime từ text tiếng Việt.
    """
    # intent đặt lịch
    match = re.search(r'(đặt|tạo|thêm)\s*(lịch|sự kiện|cuộc họp)?\s*(.+)?\s*lúc\s+(.+)', text, re.IGNORECASE)
    if match:
        title = match.group(3) or 'Sự kiện'
        time_str = match.group(4)
        dt = parse_date(time_str, languages=['vi'])
        if dt:
            return {
                'intent': 'create_event',
                'title': title.strip(),
                'datetime': dt.isoformat()
            }
    # intent hỏi ghi chú
    if 'ghi chú' in text.lower():
        return {'intent': 'ask_notes'}
    # intent hỏi lịch
    if 'lịch' in text.lower() or 'sự kiện' in text.lower():
        return {'intent': 'ask_events'}
    # intent chào hỏi
    if any(x in text.lower() for x in ['xin chào', 'chào', 'hello', 'hi']):
        return {'intent': 'greeting'}
    # intent hỏi tên
    if 'tên' in text.lower():
        return {'intent': 'ask_name'}
    # intent hỏi thời tiết
    if 'thời tiết' in text.lower():
        return {'intent': 'ask_weather'}
    return {'intent': 'chat'} 