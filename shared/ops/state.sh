#!/usr/bin/env bash
# Keep a job's SQLite state on a git branch, for scheduled runs on GitHub
# Actions (each run starts on a fresh machine).
#   ops/state.sh restore <db>   load <db> from the branch, if it exists yet
#   ops/state.sh save <db>      commit a dump of <db> to the branch and push
# The state is stored as a plain SQL dump (state.sql), which diffs and
# compresses well. Only for small state that may be public: anyone who can
# read the repo can read the branch.
# Env: STATE_BRANCH (default "state"), STATE_REMOTE (default "origin").
# Compatible with bash 3.2 (the macOS default).
set -euo pipefail

branch="${STATE_BRANCH:-state}"
remote="${STATE_REMOTE:-origin}"
cmd="${1:-}"
db="${2:-}"
if [[ -z "$cmd" || -z "$db" ]]; then
  echo "usage: $0 restore|save <db>" >&2
  exit 2
fi

# Prints the branch tip, or nothing if the branch doesn't exist yet.
fetch_tip() {
  if git fetch --quiet --depth=1 "$remote" "refs/heads/$branch" 2>/dev/null; then
    git rev-parse FETCH_HEAD
  fi
}

case "$cmd" in
  restore)
    tip="$(fetch_tip)"
    if [[ -z "$tip" ]]; then
      echo "no $branch branch yet; starting with an empty database"
      exit 0
    fi
    mkdir -p "$(dirname "$db")"
    rm -f "$db"
    git show "$tip:state.sql" | sqlite3 "$db"
    echo "restored $db from $branch@${tip:0:7}"
    ;;
  save)
    [[ -f "$db" ]] || { echo "no database at $db; nothing to save" >&2; exit 1; }
    dump="$(mktemp)"
    trap 'rm -f "$dump"' EXIT
    sqlite3 "$db" .dump >"$dump"
    blob="$(git hash-object -w "$dump")"
    tree="$(printf '100644 blob %s\tstate.sql\n' "$blob" | git mktree)"
    tip="$(fetch_tip)"
    if [[ -n "$tip" && "$(git rev-parse "$tip^{tree}")" == "$tree" ]]; then
      echo "state unchanged"
      exit 0
    fi
    message="chore(state): Update"
    if [[ -n "${GITHUB_RUN_ID:-}" ]]; then message="$message after run $GITHUB_RUN_ID"; fi
    export GIT_AUTHOR_NAME="${GIT_AUTHOR_NAME:-github-actions[bot]}"
    export GIT_AUTHOR_EMAIL="${GIT_AUTHOR_EMAIL:-41898282+github-actions[bot]@users.noreply.github.com}"
    export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME" GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
    if [[ -n "$tip" ]]; then
      commit="$(git commit-tree "$tree" -p "$tip" -m "$message")"
    else
      commit="$(git commit-tree "$tree" -m "$message")"
    fi
    git push --quiet "$remote" "$commit:refs/heads/$branch"
    echo "saved $db to $branch@${commit:0:7}"
    ;;
  *)
    echo "usage: $0 restore|save <db>" >&2
    exit 2
    ;;
esac
