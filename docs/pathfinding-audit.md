# Pathfinding audit and implementation gates

2026-09-10. Targets: original Crusader and Extreme 1.41. The running user match
has not been modified. Reproductions below execute original instructions in an
isolated emulator; they are not claims of completed live-match acceptance.

## Ownership chain

| Stage | Owner and evidence (SHC addresses) |
|---|---|
| Choose a target | Worker task state, troop orders and AI assignment. Fletcher 0x54d8f0; armory choice 0x422370; moat selector 0x5111d0. |
| Check accessibility | Keep/unit region versus destination region, explicit gate/climb transitions, alternative building entrances. 0x421a40, 0x41ade0, 0x4a5320. |
| Prepare movement | Unit coordinates, movement permissions and transition registration. `setDestinationForUnit`, 0x53d3d0. |
| Find and commit a route | Cheap direct path, bounded searches, fallback searches and unit path plan. 0x4a9b20, 0x4a97d0, 0x4a9dd0. |
| Handle failure | Caller retries; certain blocked units undergo a trapped-area check that may mark them for disappearance. 0x533fc0, 0x49d640. |
| Maintain topology | Local tile linkage, connected-region labels and explicit transitions. Region rebuild 0x4995e0; Extreme 0x499750. |

A destination can be rejected before tile search, or selected poorly before a
correct route search. Changes belong at the earliest demonstrated bad decision.

## Confirmed defects corrected in the experimental module

**Region labels:** the outer rebuild scan reads a byte from a word label. Regions
256/512/768 look empty and are fragmented into new labels. This can prematurely
exhaust the 1,000-entry table. `code/region-visited.lua` corrects the operand width
without replacing the flood fill, its ordering or the refresh policy.

**Moat index:** the selector returns a zero-based index, or -1 for failure. Its
reservation update skips zero but accepts -1; the empty-list branch also enters
that update. Thus failure writes before the array, while the first valid moat
misses its reservation. `code/moat-selection.lua` corrects both branches. The
affected preceding byte is the last cell of a 40x40 mapping buffer; downstream
effects on gameplay have not been traced. Do not call it a proven lag/desync cause.

Both fixes were exercised using the production Lua module's emitted patch bytes
against both original executables. The moat cases cover an empty list, no eligible
candidate and valid first/second entries. Portable installation tests cover both
variants and conflicts: every site must pass preflight before any code is written.
No per-tick Lua callbacks or allocation are introduced by these corrections.

## Moat approach side: confirmed policy, improvement pending

After selecting an enemy moat tile, `setXYBasedOnMoatID` (0x5003d0) takes the first
of eight adjacent positions with a suitable height and matching region. It does
not compare approach distances. Archers, spearmen, pikemen, macemen, engineers
and slaves call this shared function.

A native SHC probe put the unit south of a moat with acceptable north and south
approaches. If both share the unit's region, the farther north approach wins.
If north has a different region, the nearer south approach wins. This demonstrates
the mechanism behind a possible detour, not the user's exact map reproduction.

Improve approach selection here, not independently in every unit updater. Keep
eligibility and deterministic tie order. Comparing eight geometric distances is
cheap but does not guarantee the shortest route around obstacles; compare that
policy with a bounded route-cost query before shipping. Eight full searches per
digger would be excessive, and pathfinding scratch state is shared.

Acceptance: banks connected only via a distant opening; disconnected banks;
blocked near approach; height changes; concurrent diggers; moat removed during
approach. Check human orders separately from AI assault assignment. Never allow
troops to walk over undug moat merely to make routing easier.

## Disappearance: demonstrated dependency, removal policy unchanged

Failed movement calls `despawnUnreachableUnit`. It filters unit state/type and
terrain before searching for an escape in the same region. If none is found,
the caller assigns disappearance state 110.

A native SHC probe retained the blocked worker tile and open neighbour, changing
only the neighbour's region label. Different labels resulted in state 110;
matching labels preserved the worker's state. Region data therefore causally
affects this gate. That does not prove every disappearance comes from the rebuild
bug or that Wolf's normal-ground delivery stalls take this branch.

The preserved Wolf save has a stalled fletcher and ordinary tile connections to
two armories with space, but incorrect region fragmentation. Their existing entry
labels cannot be reached via the saved transition graph. Finish the alternative
entrance fallback before declaring that specific delivery repaired.

UCP2 Legacy's baker/moat-digger disappearance fixes are enabled in the captured
setup. Do not duplicate or disable them. See the separate historical-contribution
audit for overbuilding and siege-engine crew cleanup.

## Performance: measurement before scheduling changes

The native search already tries a direct-route fast path. Its initial heavier
search gets `(distance + 4)^2 * 10` as a budget parameter; fallbacks receive
100,000. These are search budgets, not milliseconds. Unit route storage is 400
bytes. Existing direct/hard counters are at PathFindingState +0xa8/+0xac.

Measure these counters, rebuilds and CPU time before adding tracing. If retries
dominate, investigate repeated work across unchanged topology, target and
occupancy. Caching just source/destination coordinates would be insufficient.

Recorder's per-tick RNG string/resource-table allocations are separate known
costs, not a measured percentage of slowdown. Reusable native boundary storage
is the planned correction there; ending-state checks must remain equivalent.

## Order of delivery

1. Complete the Wolf fallback trace and live-accept the width/bounds corrections.
2. Compare moat approach policies on the small layouts above.
3. Measure failures/rebuilds before changing caching or scheduling.
4. Audit every region-size reader, storage relocation, save/load and signed ID
   bounds before considering 20x capacity. Raising the bound alone corrupts memory.
5. Verify identical peer setups in multiplayer and offline replay. Changes must
   not silently affect recordings made with the old simulation setup.

OpenSHC should faithfully reimplement/document original behavior, including its
defects. Corrective behavior belongs in the UCP module that owns that subsystem.

## Reproduce the checks

Install `requirements-dev.txt`, then run `python -m unittest discover -s tests -v`.
Portable preflight/conflict checks run without the game. To also run the original
algorithms and actual-signature installation checks, set `SHC_GAME_DIR` to a local
directory containing `Stronghold Crusader.exe` and `Stronghold_Crusader_Extreme.exe`
(both original 1.41). The fixture uses Unicorn and PEfile, never a running process.
Without this variable the native cases explicitly skip. No game binary is included.

The saved-match investigation and synthetic moat-side/worker-removal probes remain
separate evidence from release acceptance. Neither correction was installed into
the user's ongoing match. Preview releases are for review and subsequent live tests.
