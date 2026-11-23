#!/usr/bin/env bash
# Test stand-in for the Claude CLI: prints its arguments, counts calls.
set -euo pipefail
if [[ -n "${FAKE_CLAUDE_COUNT:-}" ]]; then echo call >>"$FAKE_CLAUDE_COUNT"; fi
echo "$*"
