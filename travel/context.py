# utils/context.py

_context_store = {}

def set_context(thread_id, key, value):
    if thread_id not in _context_store:
        _context_store[thread_id] = {}
    _context_store[thread_id][key] = value

def get_context(thread_id, key, default=None):
    return _context_store.get(thread_id, {}).get(key, default)

def get_all_context(thread_id):
    return _context_store.get(thread_id, {})

def clear_context(thread_id):
    _context_store.pop(thread_id, None)
