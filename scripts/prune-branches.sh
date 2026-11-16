#!/bin/sh
# Delete branches that are already merged into origin/main.
#
# Usage: sh scripts/prune-branches.sh [--apply] [--remote]
#
# Without --apply it only lists what it would delete. Local branches are
# deleted with `git branch -d`, which refuses anything unmerged. With --remote,
# merged branches on origin are deleted too. The current branch, branches
# checked out in a worktree and the protected names below are always kept.

set -eu

PROTECTED="main gh-pages asv-results"
apply=0
remote=0
for arg in "$@"; do
    case "$arg" in
        --apply) apply=1 ;;
        --remote) remote=1 ;;
        *) echo "unknown option: $arg" >&2; exit 2 ;;
    esac
done

git fetch --prune origin
current=$(git rev-parse --abbrev-ref HEAD)
in_worktrees=$(git worktree list --porcelain | sed -n 's|^branch refs/heads/||p')

is_kept() {
    for kept in $PROTECTED $current $in_worktrees; do
        [ "$1" = "$kept" ] && return 0
    done
    return 1
}

for branch in $(git for-each-ref --format='%(refname:short)' refs/heads); do
    is_kept "$branch" && continue
    git merge-base --is-ancestor "$branch" origin/main || continue
    if [ "$apply" = 1 ]; then git branch -d "$branch"; else echo "local:  $branch"; fi
done

[ "$remote" = 1 ] || exit 0
for ref in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin); do
    branch=${ref#origin/}
    [ "$branch" = "origin" ] && continue
    is_kept "$branch" && continue
    git merge-base --is-ancestor "$ref" origin/main || continue
    if [ "$apply" = 1 ]; then git push origin --delete "$branch"; else echo "remote: $branch"; fi
done
