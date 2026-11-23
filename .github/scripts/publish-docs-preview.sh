#!/usr/bin/env bash
# Only the base repository is checked out. The Pages branch is read and updated as Git trees.
set -euo pipefail
[[ "$PR" =~ ^[1-9][0-9]*$ && "$HEAD_SHA" =~ ^[a-f0-9]{40}$ ]]
site="$RUNNER_TEMP/preview"
test -s "$site/dev/index.html"
test -s "$site/dev/exercises/index.html"
[[ "$(cat "$site/dev/commit.txt")" == "$HEAD_SHA" ]]
revision="$HEAD_SHA $BUILD_ID $BUILD_ATTEMPT"
printf '%s\n' "$revision" > "$site/dev/preview-build.txt"
url="https://${PREVIEW_REPOSITORY%/*}.github.io/${PREVIEW_REPOSITORY#*/}/pr-$PR/dev/"

# Stage only the validated static files. Keep the publishing repository outside the site.
git_dir=$(mktemp -d "$RUNNER_TEMP/preview-git.XXXXXXXX")
git init --quiet --bare "$git_dir"
export GIT_DIR="$git_dir" GIT_WORK_TREE="$site"
cd "$site"
git remote add origin "git@github.com:$PREVIEW_REPOSITORY.git"
git add --force --all .
site_tree=$(git write-tree)

# Preserve other previews and retry against the latest tip if publishers race.
for attempt in 1 2 3 4 5; do
  git fetch --quiet --depth=1 origin refs/heads/docs-previews
  current=$(gh api "repos/$GITHUB_REPOSITORY/pulls/$PR" --jq 'select(.state == "open") | .head.sha')
  [[ "$current" == "$HEAD_SHA" ]] || exit 0
  parent=$(git rev-parse FETCH_HEAD)
  git read-tree "$parent"
  git ls-files -z -- "pr-$PR" | git update-index --force-remove -z --stdin
  git read-tree --prefix="pr-$PR/" "$site_tree"
  tree=$(git write-tree)
  if [[ "$tree" == "$(git rev-parse "$parent^{tree}")" ]]; then break; fi
  commit=$(git -c user.name='github-actions[bot]' -c user.email='41898282+github-actions[bot]@users.noreply.github.com' \
    commit-tree "$tree" -p "$parent" -m "Preview $GITHUB_REPOSITORY#$PR at $HEAD_SHA")
  if git push origin "$commit:refs/heads/docs-previews"; then break; fi
  [[ "$attempt" != 5 ]] || exit 1
  sleep "$attempt"
done

# Pages deploys asynchronously. Verify this run's marker before advertising the URL.
for attempt in {1..60}; do
  if [[ "$(curl -fsSL --max-time 8 "${url}preview-build.txt?run=$BUILD_ID-$BUILD_ATTEMPT-$attempt")" == "$revision" ]]; then
    exit 0
  fi
  sleep 8
done
echo "Timed out waiting for GitHub Pages to serve the new preview." >&2
exit 1
