# Releasing (HACS)

HACS tracks versions via GitHub **Releases**, not raw git tags - pushing a
version tag automatically creates the matching Release (see
[`.github/workflows/release.yml`](.github/workflows/release.yml)), which is
what HACS actually reads.

## Cutting a release

1. Bump `"version"` in
   [`custom_components/find_my_device/manifest.json`](custom_components/find_my_device/manifest.json)
   to `X.Y.Z` (HACS expects this to match the release tag exactly).
2. Add a `## [X.Y.Z] - YYYY-MM-DD` entry to [`CHANGELOG.md`](CHANGELOG.md)
   describing what changed - if present, this becomes the GitHub Release's
   notes; otherwise the workflow falls back to auto-generated notes from
   the commits since the last tag.
3. Commit both, then tag and push:

   ```bash
   git add custom_components/find_my_device/manifest.json CHANGELOG.md
   git commit -m "chore: Release vX.Y.Z"
   git tag vX.Y.Z
   git push origin main --tags
   ```

4. The `release.yml` workflow verifies the tag matches the manifest version
   (fails loudly if you forgot step 1) and creates the GitHub Release.
   Watch it under the repo's **Actions** tab.

## Validation

[`.github/workflows/hacs-validate.yml`](.github/workflows/hacs-validate.yml)
runs HACS's own validation action plus `hassfest` (Home Assistant's own
manifest/integration linter) on every push to `main`, every PR, and weekly
(their rules evolve independently of this repo). Fix anything it flags
before relying on a release - it's the same check the HACS default-store
reviewers run.

## Getting into HACS

- **Custom repository (works immediately)**: anyone can add this repo via
  HACS → ⋮ → *Custom repositories* → this repo's URL → category
  *Integration*. Requires at least one GitHub Release to exist.
- **Official HACS default store (searchable without adding a custom repo
  first)**: requires a PR to [hacs/default](https://github.com/hacs/default)
  adding this repo, reviewed manually by HACS maintainers. Do this once the
  repo has real releases and has passed `hacs-validate.yml` consistently.
