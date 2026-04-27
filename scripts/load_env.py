"""Load global WES keys + Studio One project keys into os.environ.

Usage:
    from scripts.load_env import load_env
    load_env()
    import os
    paypal_id = os.environ['PAYPAL_LIVE_CLIENT_ID']

Project-specific keys override globals when both define the same variable.
"""
import os
import re
from pathlib import Path

GLOBAL_KEYS = Path("/Users/justinbabcock/Desktop/Websites/.env.keys")
PROJECT_KEYS = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno/.env.keys.cat")


def _parse_env_file(p: Path) -> dict:
    """Parse a simple KEY=VALUE file. Skips blanks and # comments."""
    out = {}
    if not p.exists():
        return out
    for raw in p.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r'^([A-Z][A-Z0-9_]*)\s*=\s*(.*)$', line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        # Strip surrounding quotes if present
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        out[key] = val
    return out


def load_env() -> None:
    """Populate os.environ from global + project key files."""
    for f in (GLOBAL_KEYS, PROJECT_KEYS):
        for k, v in _parse_env_file(f).items():
            os.environ[k] = v


def get_required(*keys: str) -> dict:
    """Load env and return required keys; raise if any are missing or blank."""
    load_env()
    out = {}
    missing = []
    for k in keys:
        v = os.environ.get(k, "").strip()
        if not v:
            missing.append(k)
        out[k] = v
    if missing:
        raise SystemExit(
            f"Missing required keys: {', '.join(missing)}\n"
            f"Add them to {PROJECT_KEYS} (or {GLOBAL_KEYS} for global keys)."
        )
    return out


if __name__ == "__main__":
    # Self-test: list what's loaded (without exposing secrets)
    load_env()
    print("Loaded keys:")
    for k in sorted(os.environ):
        if any(s in k for s in ("PAYPAL", "RECAPTCHA", "GITHUB", "VERCEL", "SUPABASE", "ORDER_", "SHIPPING", "TAX")):
            v = os.environ[k]
            preview = v[:4] + "***" + v[-2:] if len(v) > 12 else "(empty)" if not v else "***"
            print(f"  {k:32} {preview}")
