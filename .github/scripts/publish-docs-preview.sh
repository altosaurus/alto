#!/usr/bin/env bash
# Run from the trusted checkout with the preview-only branch in pages/.
set -euo pipefail
[[ "$PR" =~ ^[1-9][0-9]*$ && "$HEAD_SHA" =~ ^[a-f0-9]{40}$ ]]
site="$RUNNER_TEMP/preview"
test -s "$site/dev/index.html"
test -s "$site/dev/exercises/index.html"
[[ "$(cat "$site/dev/commit.txt")" == "$HEAD_SHA" ]]
revision="$HEAD_SHA $BUILD_ID $BUILD_ATTEMPT"
printf '%s\n' "$revision" > "$site/dev/preview-build.txt"
url="https://${PREVIEW_REPOSITORY%/*}.github.io/${PREVIEW_REPOSITORY#*/}/pr-$PR/dev/"

# Different PRs write different directories on the same branch. Reapply this directory to the
# latest tip after a competing push. Recheck the upstream PR for every attempt.
for attempt in 1 2 3 4 5; do
  git -C pages fetch --quiet --depth=1 origin docs-previews
  git -C pages checkout --quiet --detach --force FETCH_HEAD
  current=$(gh api "repos/$GITHUB_REPOSITORY/pulls/$PR" --jq 'select(.state == "open") | .head.sha')
  [[ "$current" == "$HEAD_SHA" ]] || exit 0
  rsync --recursive --delete "$site/" "pages/pr-$PR/"
  git -C pages add --all -- "pr-$PR"
  if git -C pages diff --cached --quiet; then break; fi
  git -C pages -c user.name='github-actions[bot]' -c user.email='41898282+github-actions[bot]@users.noreply.github.com' \
    commit --quiet -m "Preview $GITHUB_REPOSITORY#$PR at $HEAD_SHA"
  if git -C pages push origin HEAD:refs/heads/docs-previews; then break; fi
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
