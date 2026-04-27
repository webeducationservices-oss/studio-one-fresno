#!/bin/bash
# Source helper: loads global WES keys + Studio One project keys.
# Usage in scripts:   source ./scripts/load-env.sh
#
# Project-specific keys override globals when both define the same variable.

set -e

GLOBAL_KEYS="/Users/justinbabcock/Desktop/Websites/.env.keys"
PROJECT_KEYS="/Users/justinbabcock/Desktop/Websites/studio-one-fresno/.env.keys.cat"

if [ -f "$GLOBAL_KEYS" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$GLOBAL_KEYS"
  set +a
fi

if [ -f "$PROJECT_KEYS" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$PROJECT_KEYS"
  set +a
fi
