# Releasing

This integration uses semantic versions (`MAJOR.MINOR.PATCH`) and GitHub releases.
The Home Assistant Marketplace (2026.11+) and HACS (older versions) detect updates
from published releases, not from tags alone.

## Version choice

- **Patch** (`1.0.1` → `1.0.2`): compatible bug fixes and documentation changes.
- **Minor** (`1.0.1` → `1.1.0`): compatible new features or entities.
- **Major** (`1.x` → `2.0.0`): breaking changes that require user action.

## Release checklist

1. Ensure the `main` branch is current and the validation workflow passes.
2. Update `version` in
   `custom_components/vegvesen_vehicle_lookup/manifest.json` and add a section to
   `CHANGELOG.md`. The Marketplace refuses an integration without a valid version.
   If the release needs a newer Home Assistant, raise `homeassistant` in `hacs.json`
   so older installations are offered an earlier release instead.
3. Commit the version bump, for example `Bump version to 1.1.0`.
4. Create and push an annotated tag matching the manifest version:

   ```bash
   git tag -a v1.1.0 -m "v1.1.0"
   git push origin main
   git push origin v1.1.0
   ```

5. On GitHub, open **Releases** → **Draft a new release**, select the tag, add
   release notes, and publish it. Alternatively:

   ```bash
   gh release create v1.1.0 --notes-file notes.md --title "v1.1.0"
   ```

   The release notes are shown in the update entity under **Settings** → **Updates**.
   Put anything users must do first at the top.

6. Confirm that the HACS and hassfest validation pass for the release.

## What users experience

Users on Home Assistant 2026.11 or newer get updates from the built-in Marketplace,
under **Settings** → **Updates**. After installing, a repair asks them to restart.

While this repository is added from a link (not in the `hacs/default` catalog), the
Marketplace checks it through the GitHub API every 48 hours, and only when GitHub is
connected. Catalog repositories are refreshed every 6 hours instead.

Users still on 2026.10 or older get the update through HACS as before, and can force a
refresh with ⋮ → **Update information**.

Keep the GitHub release published and leave its tag in place: users can pick older
releases with **Install another version**. Mark prereleases as pre-releases on GitHub
so they are only offered to users who enable the **Pre-release** switch.
