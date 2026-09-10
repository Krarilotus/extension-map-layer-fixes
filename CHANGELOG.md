# Changelog

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
