# Map, save and replay compatibility

## File compatibility is different from identical simulation

The current corrections change three native code sites. They do not add save
sections, change file headers, relocate map arrays, widen stored IDs, or raise
the 1,000-entry region table limit. Region IDs were already stored as 16-bit
values; the faulty read was only eight bits wide.

There is therefore no new map/save format or migration introduced by this module.
Existing map files are expected to remain readable. That expectation is based on
the patch scope and load-path analysis, not completed live testing of every save
type. A file loading successfully does not mean the match will evolve identically.

## What happens to existing region labels?

In Crusader 1.41, the map loader and save/load menu call `TileMapState::prepareMap`
(`0x512450`). That routine updates tile links, forces the region rebuild, updates
building links and climb data, and forces further rebuilds during preparation.
The module changes the visited check in that existing rebuild, rather than
installing its own extra load or per-tick hook.

The forced rebuild clears the old region labels and region-size table before
recomputing them. Native executable tests for Crusader and Extreme confirm that
stale labels and an exhausted saved counter do not survive a forced rebuild, and
that the corrected result matches rebuilding the same topology from clean state.
The complete caller-chain trace above has currently been established for Crusader;
full live save/load acceptance in both variants remains required.

Tests also compare original and patched routines on ordinary maps and at the
capacity boundary. Regions 256, 512 and 768 retain their correct identity after
the fix. The original 1,000-entry cutoff remains; truly excessive region counts
are not solved by increasing storage in this release.

## Compatibility expectations

| Use case | Expected behavior / remaining check |
| --- | --- |
| Load an old map with the fix | Same format. Native preparation rebuilds connectivity; live acceptance pending. |
| Load an old save with the fix | Same format; corrected path decisions can change the continuation. Verify workers, cargo/delivery, walls, moats and save/reload. |
| Save with the fix, then load without it | No format extension prevents reading, but the original buggy behavior returns. Reverse live loading still needs verification. |
| Replay an old recording with the fix newly enabled | Not equivalent. Use its recorded configuration without the new simulation change. |
| Replay a new recording made with the fix | Keep the same module version/configuration and verify full playback. |
| Multiplayer with mixed module setups | Unsupported: different path decisions can desynchronize the game. |

The moat correction also changes simulation state: valid candidate zero now gets
its reservation update, while failure no longer writes before the moat array.
It does not change the moat record layout or choose a new approach direction.

## Release gates

Retain original files and test copies. Complete old-map/old-save loading in both
variants, new save/reload, reverse loading without the module, and the preserved
stalled-worker case. Then run matching multiplayer setups and replay both captures
offline. Include module-off baseline timing and gameplay observations.

Do not advertise general backward compatibility until these live gates pass. Do
not bundle a 20x region-capacity expansion into this correction: that requires a
separate storage, reference and save/load design.
