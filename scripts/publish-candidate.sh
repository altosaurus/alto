#!/usr/bin/env bash
# Stage the verified candidate as a draft until GitHub confirms every asset's digest.
set -euo pipefail
export LC_ALL=C
tag=$GITHUB_REF_NAME
if ! gh release view "$tag" --json isDraft >/dev/null 2>&1; then
    gh release create "$tag" --draft --verify-tag --title "Alto ${tag#v}" --notes-file notes.md
fi
draft=$(gh release view "$tag" --json isDraft --jq .isDraft)
if [[ "$draft" == true ]]; then
    # A retry can resume a partially uploaded draft. Leave existing assets in place for comparison.
    uploaded=$(gh release view "$tag" --json assets --jq '.assets[].name')
    for file in dist/*; do
        if ! grep -Fxq -- "${file##*/}" <<< "$uploaded"; then
            gh release upload "$tag" "$file"
        fi
    done
fi
(cd dist && sha256sum *) | sort > "$RUNNER_TEMP/reviewed"
release_url=$(gh release view "$tag" --json apiUrl --jq .apiUrl)
gh api --paginate "$release_url/assets" |
    jq -er '.[] | (.digest | sub("^sha256:"; "")) + "  " + .name' |
    sort > "$RUNNER_TEMP/uploaded"
diff -u "$RUNNER_TEMP/reviewed" "$RUNNER_TEMP/uploaded"
if [[ "$draft" == true ]]; then
    gh release edit "$tag" --draft=false --prerelease=false
fi
