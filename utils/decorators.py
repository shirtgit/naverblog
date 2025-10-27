# utils/decorators.py
import time
from functools import wraps

def sleep_after(seconds=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            time.sleep(seconds)
            return result
        return wrapper
    return decorator