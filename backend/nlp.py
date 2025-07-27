import re
from dateparser import parse as parse_date

def detect_intent_and_entities(text: str):
    """
    Detect scheduling intent, extract title and datetime from Vietnamese text.
    """
    # Schedule creation intent
    match = re.search(r'(schedule|create|add)\s*(event|meeting|appointment)?\s*(.+)?\s*at\s+(.+)', text, re.IGNORECASE)
    if match:
        title = match.group(3) or 'Event'
        time_str = match.group(4)
        dt = parse_date(time_str, languages=['vi'])
        if dt:
            return {
                'intent': 'create_event',
                'title': title.strip(),
                'datetime': dt.isoformat()
            }
    # Note inquiry intent
    if 'note' in text.lower():
        return {'intent': 'ask_notes'}
    # Schedule inquiry intent
    if 'schedule' in text.lower() or 'event' in text.lower():
        return {'intent': 'ask_events'}
    # Greeting intent
    if any(x in text.lower() for x in ['hello', 'hi', 'greetings']):
        return {'intent': 'greeting'}
    # Name inquiry intent
    if 'name' in text.lower():
        return {'intent': 'ask_name'}
    # Weather inquiry intent
    if 'weather' in text.lower():
        return {'intent': 'ask_weather'}
    return {'intent': 'chat'} 