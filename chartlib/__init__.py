"""Publication-quality academic figure and table utilities.

See SKILL.md for the operating rules. Source data stays read-only and every
permitted transformation is recorded in AuditLog.

Matplotlib normally stores its font cache in a user directory. Point the cache
to a temporary cache before importing Matplotlib so font discovery also works in
restricted environments.
"""
from __future__ import annotations

import os
import tempfile

_EC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MPLCACHE = os.environ.get("MPLCONFIGDIR") or os.path.join(tempfile.gettempdir(), "econfigure-matplotlib")
os.makedirs(_MPLCACHE, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", _MPLCACHE)

__version__ = "0.1.0"
