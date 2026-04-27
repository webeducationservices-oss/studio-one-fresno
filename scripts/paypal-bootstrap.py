#!/usr/bin/env python3
"""PayPal one-time bootstrap.

Registers webhooks on both sandbox + live so PayPal can notify our /api/paypal-webhook
endpoint of payment captures, refunds, and disputes. Saves the webhook IDs back into
.env.keys.cat for signature verification.

Idempotent — checks for existing webhooks at the same URL and updates rather than
creating duplicates.

Usage:
    python3 scripts/paypal-bootstrap.py
    python3 scripts/paypal-bootstrap.py --env sandbox     # only sandbox
    python3 scripts/paypal-bootstrap.py --env live        # only live
"""
import sys, argparse, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paypal_auth import call, get_token, update_env_key

WEBHOOK_URL = 'https://studio-one-fresno.vercel.app/api/paypal-webhook'

# Events we want PayPal to notify us about
EVENTS = [
    'CHECKOUT.ORDER.APPROVED',         # buyer approved order (pre-capture)
    'PAYMENT.CAPTURE.COMPLETED',       # payment captured = order paid
    'PAYMENT.CAPTURE.REFUNDED',        # refund issued
    'PAYMENT.CAPTURE.REVERSED',        # chargeback / dispute reversal
    'PAYMENT.CAPTURE.DENIED',          # capture denied
    'CUSTOMER.DISPUTE.CREATED',        # buyer opened a dispute
    'CUSTOMER.DISPUTE.RESOLVED',       # dispute resolved
    'CUSTOMER.DISPUTE.UPDATED',        # status update on dispute
]

def list_webhooks(env):
    """Return existing webhooks subscribed for this app."""
    res = call(env, '/v1/notifications/webhooks')
    return res.get('webhooks', []) if isinstance(res, dict) else []

def register(env):
    base, token = get_token(env)
    print(f'\n=== {env.upper()} ===')

    # 1. Find existing webhook with our URL
    existing = list_webhooks(env)
    print(f'  {len(existing)} existing webhooks on this app')
    matching = next((w for w in existing if w.get('url') == WEBHOOK_URL), None)

    payload = {
        'url': WEBHOOK_URL,
        'event_types': [{'name': e} for e in EVENTS],
    }

    if matching:
        wid = matching['id']
        print(f'  ↻ Updating existing webhook {wid}')
        # Replace event subscriptions (PATCH wholesale)
        patch = [
            {'op': 'replace', 'path': '/url', 'value': WEBHOOK_URL},
            {'op': 'replace', 'path': '/event_types', 'value': [{'name': e} for e in EVENTS]},
        ]
        res = call(env, f'/v1/notifications/webhooks/{wid}', method='PATCH', body=patch,
                   base_override=base, token_override=token)
        if isinstance(res, dict) and res.get('_status', 200) >= 400:
            print(f'  ✗ PATCH failed: {res}')
            # Fall back: delete + recreate
            print('  trying delete + recreate...')
            call(env, f'/v1/notifications/webhooks/{wid}', method='DELETE',
                 base_override=base, token_override=token)
            res = call(env, '/v1/notifications/webhooks', method='POST', body=payload,
                       base_override=base, token_override=token)
            if isinstance(res, dict) and 'id' in res:
                wid = res['id']
                print(f'  ✓ Created new webhook {wid}')
            else:
                print(f'  ✗ Recreate failed: {res}')
                return None
        else:
            print(f'  ✓ Updated webhook {wid} with {len(EVENTS)} event subscriptions')
    else:
        print(f'  + Creating new webhook → {WEBHOOK_URL}')
        res = call(env, '/v1/notifications/webhooks', method='POST', body=payload,
                   base_override=base, token_override=token)
        if not isinstance(res, dict) or 'id' not in res:
            print(f'  ✗ Create failed: {res}')
            return None
        wid = res['id']
        print(f'  ✓ Created webhook {wid}')

    # 2. Verify subscription
    res = call(env, f'/v1/notifications/webhooks/{wid}',
               base_override=base, token_override=token)
    actual_events = sorted(e['name'] for e in res.get('event_types', []))
    expected = sorted(EVENTS)
    if actual_events == expected:
        print(f'  ✓ All {len(EVENTS)} event subscriptions active')
    else:
        missing = set(expected) - set(actual_events)
        extra = set(actual_events) - set(expected)
        if missing: print(f'  ! Missing events: {missing}')
        if extra: print(f'  ! Extra events: {extra}')

    # 3. Save webhook ID to env file
    env_key = f'PAYPAL_{env.upper()}_WEBHOOK_ID'
    update_env_key(env_key, wid)
    print(f'  ✓ Saved {env_key}={wid[:12]}... to .env.keys.cat')
    return wid

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--env', choices=['sandbox', 'live', 'both'], default='both')
    args = ap.parse_args()

    targets = ['sandbox', 'live'] if args.env == 'both' else [args.env]
    results = {}
    for e in targets:
        results[e] = register(e)

    print('\n' + '=' * 50)
    if all(v for v in results.values()):
        print('✓ Bootstrap complete. PayPal will deliver webhooks to:')
        print(f'  {WEBHOOK_URL}')
        print('\nNext: deploy api/paypal-webhook.js so the endpoint exists')
        print('      to receive these events.')
    else:
        print('✗ One or more environments failed — see output above.')
        sys.exit(1)
