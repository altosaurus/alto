#!/usr/bin/env bash
# The annotated version tag identifies the exact ZIP the maintainer reviewed.
set -euo pipefail
version=$(python3 -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')
if [[ "$GITHUB_REF_NAME" != "v$version" || $(git cat-file -t "$GITHUB_REF") != tag ]]; then
    echo "Expected an annotated tag named v$version." >&2
    exit 1
fi
annotation=$(git for-each-ref --format='%(contents:subject)' "$GITHUB_REF")
if [[ ! "$annotation" =~ ^Candidate:\ ([0-9]+)\ ([0-9a-f]{64})$ ]]; then
    echo "Use the Candidate annotation from the reviewed Release run summary." >&2
    exit 1
fi
artifact_id=${BASH_REMATCH[1]}
digest=${BASH_REMATCH[2]}
commit=$(git rev-parse HEAD)
api="repos/$GITHUB_REPOSITORY/actions"
metadata=$(gh api "$api/artifacts/$artifact_id")
run=$(jq -er --arg commit "$commit" --arg digest "sha256:$digest" '
    select(.name == "release-candidate" and .expired == false and .digest == $digest
           and .workflow_run.head_sha == $commit) | .workflow_run.id' <<< "$metadata")
gh api "$api/runs/$run" | jq -e '
    .path == ".github/workflows/release.yml" and .event == "workflow_dispatch"
    and .head_branch == "main" and .conclusion == "success"' > /dev/null

archive="$RUNNER_TEMP/candidate.zip"
gh api "$api/artifacts/$artifact_id/zip" > "$archive"
echo "$digest  $archive" | sha256sum --strict --check
mkdir dist
unzip -q "$archive" -d dist
cd dist
[[ $(cat SOURCE-COMMIT) == "$commit" ]]
test -s SHA256SUMS.sig
sha256sum --strict --check SHA256SUMS
# Every file promoted from the ZIP must appear in the signed inventory.
find . -maxdepth 1 -type f ! -name SHA256SUMS ! -name SHA256SUMS.sig -printf '%f\n' | sort > "$RUNNER_TEMP/files"
cut -c67- SHA256SUMS | sort | diff -u "$RUNNER_TEMP/files" -
