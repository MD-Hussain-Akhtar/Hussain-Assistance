import json
from pathlib import Path
from datetime import datetime, timezone

MEMORY_FILE = Path('data') / 'memory.json'

class MemoryStore:
    def __init__(self):
        MEMORY_FILE.parent.mkdir(exist_ok=True)
        self._data = {'facts': [], 'preferences': {}, 'reminders': []}
        self._load()

    def _load(self):
        if MEMORY_FILE.exists():
            try:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {'facts': [], 'preferences': {}, 'reminders': []}

    def _save(self):
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    # Facts
    def add_fact(self, text: str):
        item = {"text": text, "timestamp": datetime.now(timezone.utc).isoformat()}
        self._data.setdefault('facts', []).append(item)
        self._save()
        return item

    def list_facts(self):
        return list(self._data.get('facts', []))

    # Preferences
    def set_preference(self, key: str, value):
        self._data.setdefault('preferences', {})[key] = value
        self._save()
        return {key: value}

    def get_preferences(self):
        return dict(self._data.get('preferences', {}))

    # Reminders
    def add_reminder(self, text: str, due_iso: str):
        reminder = {"text": text, "due": due_iso, "sent": False, "id": int(datetime.now(timezone.utc).timestamp() * 1000)}
        self._data.setdefault('reminders', []).append(reminder)
        self._save()
        return reminder

    def list_reminders(self):
        return list(self._data.get('reminders', []))

    def mark_reminder_sent(self, reminder_id):
        for r in self._data.get('reminders', []):
            if r.get('id') == reminder_id:
                r['sent'] = True
        self._save()

    def remove_reminder(self, reminder_id):
        self._data['reminders'] = [r for r in self._data.get('reminders', []) if r.get('id') != reminder_id]
        self._save()
        return True
