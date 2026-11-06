# Changelog

All notable changes to this project are documented in this file.

## [1.2.0] - 2026-11-06

### Changed

- Ready for the Home Assistant Marketplace that replaces HACS in 2026.11: README
  install instructions and My links for both the Marketplace and HACS, a Marketplace
  exclude block, an integration category, and `country` in `hacs.json`. The removed
  `render_readme` key is gone.
- The `lookup` action is registered when Home Assistant starts, and raises a
  translated error for an invalid or missing registration number instead of only
  logging a warning. The **Lookup Now** button does the same.
- Action names and descriptions moved to the translation files.
- Uses `entry.runtime_data` instead of `hass.data`, and declares a single config
  entry in the manifest.

### Added

- Norwegian Bokmål translation.
- Tests for setup, unloading, the lookup action, and long values.

### Fixed

- Free-text values longer than 255 characters, such as vehicle remarks, are
  truncated instead of failing to write the sensor state.
- The raw response attribute is no longer written to the recorder database, where
  large responses exceeded the attribute size limit.

### Removed

- `strings.json`, which custom integrations do not use. Translations live in
  `translations/`.

## [1.1.0] - 2026-09-17

### Added

- Reauthentication flow for replacing an expired or revoked API key without
  removing and recreating the integration.
- Automated HACS, hassfest, Ruff, and test validation with GitHub Actions.
- Tests for API responses, config flows, coordinator behavior, and the sensor
  inventory.
- Bundled Home Assistant brand assets.
- Maintainer release guide.

### Fixed

- Correct repository links, code owner, integration type, and minimum Home
  Assistant metadata.
- Always close API responses, including API-key validation responses.
- Reject malformed API payloads instead of treating them as successful lookups.
- Cancel pending debounce timers when an immediate lookup is requested.
- Cancel all scheduled callbacks when the text entity is removed.
- Clear stale raw response data and timestamp every lookup attempt.
- Keep status and timestamp diagnostics available after a failed lookup.
- Expose the last-updated value as a proper Home Assistant timestamp sensor.

### Changed

- Only one integration instance can be configured because one API key can look
  up any supported registration number.
- Minimum supported Home Assistant version is now 2024.11.0.

## [1.0.1] - 2026-02-12

- Allow an optional space in registration number input.

## [1.0.0] - 2026-02-11

- Initial release.

[1.2.0]: https://github.com/esphm/Vegvesen-Vehicle-Lookup/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/esphm/Vegvesen-Vehicle-Lookup/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/esphm/Vegvesen-Vehicle-Lookup/releases/tag/v1.0.1
[1.0.0]: https://github.com/esphm/Vegvesen-Vehicle-Lookup/releases/tag/v1.0.0
