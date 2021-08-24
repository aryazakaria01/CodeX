# Config ENV values will be loaded from here

import os

ENV = bool(os.environ.get("ENV", False))

if ENV:
    from sample_config import Config  # codex
elif os.path.exists("config.py"):
    from config import Development as Config  # codex
