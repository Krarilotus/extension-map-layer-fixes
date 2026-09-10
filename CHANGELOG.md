# Changelog

## 0.1.3 (preview)

- Trace native map/save preparation and document file compatibility separately
  from replay determinism; no map format or region-capacity change is introduced.
- Exercise region IDs 256/512/768, stale saved labels, ordinary maps and the
  unchanged capacity boundary against both original executable variants.
- Define the runtime file list for the existing UCP store packager. Store builds
  need no Python and exclude development tools and tests.

## 0.1.2 (preview)

- Put definition.yml and init.lua at the ZIP root, as required by UCP discovery.
- Test native startup from that exact root; reject a nested source-archive layout.

## 0.1.1 (preview)

- Add launcher descriptions in all nine UCP languages and include them in the ZIP.
- Document installation, compatibility, and the remaining live test steps.
- Verify documentation and localization in the packaged module, and install the
  extracted release contents against both original executable fixtures.

## 0.1.0 (preview)

- Correct the native connectivity rebuild's visited-region check to use the
  full 16-bit region ID in Crusader and Extreme 1.41.
- Stop the moat selector writing outside its array when no candidate exists;
  reserve the first valid moat entry consistently with later entries.
