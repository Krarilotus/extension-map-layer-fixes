# Map layer fixes

Repairs native map connectivity without replacing the game's pathfinder.

The first fix makes the region rebuild read complete region IDs. The original
game treats region 256 (and other multiples of 256) as unvisited, which can split
connected ground into falsely separate regions and inflate the region count.
Both Crusader 1.41 and Extreme 1.41 contain the same faulty read.

The moat selector also confuses its -1 failure result with valid index zero.
It writes before the moat array on failure and skips the first moat's reservation
on success. Two native branch corrections prevent both errors. They preserve the
existing candidate scoring and do not change which side troops dig from.

This is an experimental implementation, not yet a released or live-validated
module. Controlled tests execute the original flood fill; the reported saved
match still needs its own causal check.

The bounds correction was reproduced against both original executables with an
empty list, no eligible candidate, and valid first/second candidates. Live match
acceptance and multiplayer compatibility remain pending.

All multiplayer peers must use the same version and settings: connectivity
affects simulation decisions. Replays must retain the recorded module setup.
Install before launching a game; the module does not patch an already running
match or force an extra rebuild. Native load/refresh logic performs rebuilding.

## Scope

- Region identity correctness is owned by this module.
- Refresh frequency remains owned by the game and UCP2 Legacy's existing option.
- Replay capture and playback remain owned by Recorder.
- The current 1,000-entry region size table is unchanged. A proposed 20x increase
  requires auditing its readers, array storage, ID bounds and save/load behavior.
  It is not a substitute for correcting the faulty visited check.

No Lua callbacks, allocations or file work run during pathfinding. The patch
adds a small native trampoline to the rebuild scan; performance still needs
measurement on representative maps before release.

See [the pathfinding audit](docs/pathfinding-audit.md) for the ownership chain,
confirmed findings and remaining acceptance gates.
