# Changelog

## 0.1.0 (unreleased)

- Correct the native connectivity rebuild's visited-region check to use the
  full 16-bit region ID in Crusader and Extreme 1.41.
- Stop the moat selector writing outside its array when no candidate exists;
  reserve the first valid moat entry consistently with later entries.
