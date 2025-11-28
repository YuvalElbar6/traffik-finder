import re
from functools import wraps

def auto_params(*expected_keys, defaults=None):
    """
    Converts raw string or malformed param input into a structured dict.
    FastMCP older versions pass raw strings, so we normalize it here.
    """
    defaults = defaults or {}

    def decorator(fn):
        @wraps(fn)
        def wrapper(params):
            # If params already dict → merge defaults
            if isinstance(params, dict):
                return fn({**defaults, **params})

            # Otherwise parse raw text
            text = str(params).strip()
            parsed = dict(defaults)

            # Single parameter case
            if len(expected_keys) == 1:
                key = expected_keys[0]
                match = re.search(r"([A-Za-z0-9_-]+)$", text)
                parsed[key] = match.group(1) if match else defaults.get(key)
                return fn(parsed)

            # Multi-param case: take words in sequence
            words = text.split()
            for i, key in enumerate(expected_keys):
                if i < len(words):
                    parsed[key] = words[i]
                else:
                    parsed[key] = defaults.get(key)

            return fn(parsed)

        return wrapper
    return decorator
