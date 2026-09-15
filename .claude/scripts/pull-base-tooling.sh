#!/bin/sh
# Thin wrapper so the command reads the same as the other tooling scripts.
# All logic is in pull-base-tooling.py — see its docstring.
exec python3 "$(dirname "$0")/pull-base-tooling.py" "$@"
