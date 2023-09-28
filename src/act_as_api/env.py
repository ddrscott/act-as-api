"""
All environment variable access should be performed via this module.
- allows tracing of where variables are used
- provide sensible defaults
- reduce string typos
"""
import re
import os
import sys

BOTS_PATH = 'sample_data/bots'
DEFAULT_LLM_MODEL = 'gpt-3.5-turbo-0613'
DEFAULT_LLM_TEMPERATURE = '0.5'
OPENAI_API_KEY = 'must be set'


def keys():
    # must be all caps or underscores
    return [k for k in globals() if re.match(r"\b[A-Z_]+\b", k)]

# Magic: Override locals with environment settings
for key in dict(locals()):
    if key in os.environ:
        setattr(sys.modules[__name__], key, os.getenv(key))
