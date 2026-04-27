"""Shared PayPal auth helper — used by bootstrap, healthcheck, and webhook scripts."""
import os, json, base64, urllib.request, urllib.error, sys
from pathlib import Path

# Make sibling load_env importable regardless of CWD
sys.path.insert(0, str(Path(__file__).parent))
from load_env import load_env

load_env()

LIVE_BASE = 'https://api-m.paypal.com'
SANDBOX_BASE = 'https://api-m.sandbox.paypal.com'

def env_creds(env: str):
    """Return (base_url, client_id, secret) for 'sandbox' or 'live'."""
    if env == 'sandbox':
        return SANDBOX_BASE, os.environ.get('PAYPAL_SANDBOX_CLIENT_ID',''), os.environ.get('PAYPAL_SANDBOX_SECRET','')
    if env == 'live':
        return LIVE_BASE, os.environ.get('PAYPAL_LIVE_CLIENT_ID',''), os.environ.get('PAYPAL_LIVE_SECRET','')
    raise ValueError(f'Unknown env: {env!r} (use "sandbox" or "live")')

def get_token(env: str = 'sandbox'):
    """OAuth2 client_credentials grant. Returns access_token."""
    base, cid, sec = env_creds(env)
    if not cid or not sec:
        raise SystemExit(f'Missing PayPal {env.upper()} credentials in .env.keys.cat')
    auth = base64.b64encode(f'{cid}:{sec}'.encode()).decode()
    req = urllib.request.Request(
        f'{base}/v1/oauth2/token',
        data=b'grant_type=client_credentials',
        headers={
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
        },
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    return base, data['access_token']

def call(env: str, path: str, method: str = 'GET', body=None, headers=None, base_override=None, token_override=None):
    """Make an authenticated PayPal API request. Returns parsed JSON (or raw text on non-JSON)."""
    if base_override and token_override:
        base, token = base_override, token_override
    else:
        base, token = get_token(env)
    h = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    if headers:
        h.update(headers)
    data = None
    if body is not None:
        data = json.dumps(body).encode() if not isinstance(body, (bytes, str)) else (body.encode() if isinstance(body, str) else body)
    req = urllib.request.Request(f'{base}{path}', data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            raw = r.read()
        if not raw: return None
        try: return json.loads(raw)
        except: return raw.decode('utf-8','ignore')
    except urllib.error.HTTPError as e:
        body_txt = e.read().decode('utf-8','ignore') if e.fp else ''
        try:
            err = json.loads(body_txt)
        except:
            err = {'_raw': body_txt}
        err['_status'] = e.code
        return err

def update_env_key(key: str, value: str):
    """Replace or append a KEY=VAL line in .env.keys.cat."""
    p = Path('/Users/justinbabcock/Desktop/Websites/studio-one-fresno/.env.keys.cat')
    text = p.read_text() if p.exists() else ''
    import re
    pattern = re.compile(rf'^{re.escape(key)}=.*$', re.MULTILINE)
    if pattern.search(text):
        text = pattern.sub(f'{key}={value}', text)
    else:
        text = text.rstrip() + f'\n{key}={value}\n'
    p.write_text(text)
