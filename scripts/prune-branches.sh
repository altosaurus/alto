#!/bin/sh
# Preview merged branches by default. --apply deletes them. --remote also
# includes origin branches. The post-merge hook uses only local references.
set -eu
set -f

apply=0
remote=0
if [ "${1:-}" = --post-merge ]; then
    [ "$#" = 1 ] || exit 2
    [ "$(git symbolic-ref --quiet HEAD)" = refs/heads/main ] || exit 0
    git show-ref --verify --quiet refs/remotes/origin/main || exit 0
    apply=1
else
    preview=0
    for arg in "$@"; do
        case "$arg" in
            --apply) apply=1 ;;
            --dry-run) preview=1 ;;
            --remote) remote=1 ;;
            *) echo "unknown option: $arg" >&2; exit 2 ;;
        esac
    done
    if [ "$preview" = 1 ] && [ "$apply" = 1 ]; then
        echo "--dry-run and --apply cannot be combined" >&2
        exit 2
    fi
    if [ "$remote" = 1 ]; then git fetch --prune origin; else git fetch --no-prune origin main; fi
fi

# Git branch names cannot contain whitespace. Match complete names, including
# paths such as release/maintenance. Disable shell globbing above.
protected=$(git config --get-all alto.keepBranch || :)
in_worktrees=$(git worktree list --porcelain | sed -n 's|^branch refs/heads/||p')
is_kept() {
    for kept in main gh-pages asv-results $protected $in_worktrees; do
        [ "$1" = "$kept" ] && return 0
    done
    return 1
}

upstream=refs/remotes/origin/main
local_branches=$(git for-each-ref --merged="$upstream" --format='%(refname:lstrip=2)' refs/heads)
for branch in $local_branches; do
    is_kept "$branch" && continue
    git merge-base --is-ancestor "refs/heads/$branch" refs/heads/main || continue
    if [ "$apply" = 1 ]; then
        # Git can also refuse if a branch has a divergent tracking upstream.
        # Retain that branch and continue handling the other candidates.
        git branch -d -- "$branch" || continue
    else
        echo "local:  $branch ($(git rev-parse --short "refs/heads/$branch"))"
    fi
done

[ "$remote" = 1 ] || exit 0
remote_branches=$(git for-each-ref --merged="$upstream" --format='%(if)%(symref)%(then)%(else)%(refname:lstrip=3)%(end)' refs/remotes/origin)
for branch in $remote_branches; do
    is_kept "$branch" && continue
    if [ "$apply" = 1 ]; then git push origin --delete "$branch"; else echo "remote: $branch"; fi
done
