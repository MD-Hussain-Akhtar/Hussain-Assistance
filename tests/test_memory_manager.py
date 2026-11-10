import os
import shutil
from backend.memory_manager import MemoryManager, get_memory_manager


def test_memory_manager_basic_cycle(tmp_path):
    # Run against a temporary memory dir to avoid touching repo files
    base = tmp_path / 'memory'
    os.makedirs(str(base), exist_ok=True)

    # monkeypatch Path constants in module (simple override)
    from backend import memory_manager as mm
    old_dir = mm.MEMORY_DIR
    mm.MEMORY_DIR = base
    mm.USER_PROFILE = base / 'user_profile.json'
    mm.EMOTION_HISTORY = base / 'emotion_history.json'
    mm.CONVERSATION = base / 'conversation_memory.json'

    try:
        mgr = MemoryManager()
        mgr.set_user_field('name', 'TestUser')
        profile = mgr.get_user_profile()
        assert profile.get('name') == 'TestUser'

        mgr.add_emotion('happy', trigger='voice', confidence=0.9)
        ems = mgr.list_emotions()
        assert any(e['emotion'] == 'happy' for e in ems)

        mgr.add_conversation_entry('User', 'Hello world')
        conv = mgr.get_conversation()
        assert conv[-1]['text'] == 'Hello world'

        mgr.add_fact('I like pizza')
        facts = mgr.list_facts()
        assert any('pizza' in f['text'] for f in facts)

        removed = mgr.forget_fact('pizza')
        assert removed >= 1

    finally:
        # restore
        mm.MEMORY_DIR = old_dir
        # cleanup
        shutil.rmtree(str(base), ignore_errors=True)