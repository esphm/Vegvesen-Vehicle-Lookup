# Releasing

This integration uses semantic versions (`MAJOR.MINOR.PATCH`) and GitHub releases.
HACS detects updates from published releases, not from tags alone.

## Version choice

- **Patch** (`1.0.1` → `1.0.2`): compatible bug fixes and documentation changes.
- **Minor** (`1.0.1` → `1.1.0`): compatible new features or entities.
- **Major** (`1.x` → `2.0.0`): breaking changes that require user action.

## Release checklist

1. Ensure the `main` branch is current and the validation workflow passes.
2. Update `version` in
   `custom_components/vegvesen_vehicle_lookup/manifest.json`.
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
   gh release create v1.1.0 --generate-notes --title "v1.1.0"
   ```

6. Confirm that HACS validation passes for the release.

## What users experience

HACS periodically refreshes repository information. Existing users see the new
version as an available update, install it from HACS, and restart Home Assistant.
Users can force a refresh from HACS with ⋮ → **Update information**.

Keep the GitHub release published and leave its tag in place. Mark prereleases as
pre-releases on GitHub so they are not offered as stable updates.
