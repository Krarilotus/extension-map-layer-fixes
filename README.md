# Map layer fixes

Repairs native map connectivity without replacing the game's pathfinder.

**Experimental preview for Crusader 1.41 and Extreme 1.41 with UCP3 3.0.7
or later.** Native automated checks pass; live gameplay and multiplayer
validation are still pending.

## Install and try it

1. Download `map-layer-fixes-0.1.3.zip` from the newest
   [PR preview release](https://github.com/Krarilotus/extension-map-layer-fixes/releases).
   Use the module ZIP, not GitHub's source-code archive.
2. Import the ZIP with the UCP launcher’s **+** button, enable **Map Layer Fixes**,
   and save your configuration. Close and relaunch the game to apply it.
3. For multiplayer, install the same version on every PC and use matching settings.
   Record new replays with this setup; keep the original setup for old recordings.

There are no additional options or in-game buttons. The launcher description is
available in English, German, French, Russian, Hungarian, Turkish, Chinese,
Spanish, and Persian. These previews are not yet part of the public extension store.

See [the short test plan](docs/testing.md) before testing an existing save.
See [map/save/replay compatibility](docs/compatibility.md) for what the unchanged
file format means, and why old replays must retain their original module setup.

## What it fixes

The first fix makes the region rebuild read complete region IDs. The original
game treats region 256 (and other multiples of 256) as unvisited, which can split
connected ground into falsely separate regions and inflate the region count.
Both Crusader 1.41 and Extreme 1.41 contain the same faulty read.

The moat selector also confuses its -1 failure result with valid index zero.
It writes before the moat array on failure and skips the first moat's reservation
on success. Two native branch corrections prevent both errors. They preserve the
existing candidate scoring and do not change which side troops dig from.

Controlled tests execute the original flood fill. The reported saved match still
needs its own causal check; this preview does not claim that every stalled worker
or slow match has the same cause.

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
