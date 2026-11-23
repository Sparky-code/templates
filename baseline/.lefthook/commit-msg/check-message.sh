#!/usr/bin/env bash
# Commit message check (from Sparky-code/templates; update with `copier update`).
#
#   type(scope)!: Imperative subject
#
#   Optional body explaining why, after a blank line.
#
# - type: feat fix refactor docs test chore build ci; scope and ! optional
# - subject: capitalised, imperative, no trailing period; whole line <= 72 chars
# - no Co-Authored-By trailers, "Generated with" lines, or session IDs/links
# Merge, revert, fixup and squash commits that git writes itself are exempt.
# Compatible with bash 3.2 (the macOS default).
set -euo pipefail

msg_file="${1:?usage: check-message.sh <commit message file>}"

# Read the message, skipping comment lines and trailing whitespace.
# (Plain read loop: this must run on macOS's bash 3.2, which has no mapfile.)
lines=()
while IFS= read -r line || [[ -n "$line" ]]; do
  [[ "$line" == \#* ]] && continue
  lines+=("${line%"${line##*[![:space:]]}"}")
done <"$msg_file"
subject="${lines[0]:-}"

fail() {
  printf 'commit-msg: %s\n' "$1" >&2
  printf '  subject: %s\n' "$subject" >&2
  printf '  expected: type(scope)!: Imperative subject  (types: feat fix refactor docs test chore build ci)\n' >&2
  exit 1
}

case "$subject" in
  "Merge "* | "Revert \""* | "fixup! "* | "squash! "* | "amend! "*) exit 0 ;;
esac

[[ -n "$subject" ]] || fail "empty commit message"

types='feat|fix|refactor|docs|test|chore|build|ci'
if [[ ! "$subject" =~ ^($types)(\([a-z0-9][a-z0-9._/-]*\))?!?:\ (.+)$ ]]; then
  fail "subject must start with a type, e.g. 'fix: Handle empty input'"
fi
text="${BASH_REMATCH[3]}"

(( ${#subject} <= 72 )) || fail "subject is ${#subject} characters; keep it to 72"
[[ "$text" =~ ^[A-Z0-9] ]] || fail "start the subject text with a capital letter"
[[ "$text" != *. ]] || fail "drop the trailing period"
first_word="${text%% *}"
case "$first_word" in
  Added | Adds | Adding | Fixed | Fixes | Fixing | Updated | Updates | Updating | \
    Removed | Removes | Removing | Changed | Changes | Changing | Renamed | Renames | \
    Moved | Moves | Improved | Improves | Refactored | Refactors | Created | Creates)
    fail "use the imperative mood ('Add', not '$first_word')"
    ;;
esac

if (( ${#lines[@]} > 1 )) && [[ -n "${lines[1]}" ]]; then
  fail "leave a blank line between the subject and the body"
fi

body="$(printf '%s\n' "${lines[@]}")"
if grep -qiE '^co-authored-by:' <<<"$body"; then
  fail "remove the Co-Authored-By trailer"
fi
if grep -qiE '(generated (with|by) .*(claude|copilot|gpt|ai))|claude\.ai/(code|chat)/|session[_ -]?id[:=]|^session: ' <<<"$body"; then
  fail "remove generated-by lines and session IDs or links"
fi
exit 0
