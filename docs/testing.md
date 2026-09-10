# Testing the preview

## Automated checks

Install the development dependencies with `python -m pip install -r requirements-dev.txt`
and run `python -m unittest discover -s tests -v`.

Set `SHC_GAME_DIR` to a folder containing your original 1.41 executables,
`Stronghold Crusader.exe` and `Stronghold_Crusader_Extreme.exe`, to include native
tests. These execute code from those files in an emulator, without touching a
running game. Without the files, these tests explicitly skip.

The checks cover region 256 retaining its identity across connected tiles, moat
selection with empty/ineligible/first/second candidates, patch conflicts preventing
installation, and startup from the extracted release ZIP in both game variants.
Packaging checks ensure the README and all nine launcher descriptions are present.

## Live acceptance — still pending

Keep the original save and recording. Use a copy for these checks, and record the
game version, module version, other enabled extensions, map and outcome.

1. **Launcher:** import the release ZIP and view its description in each UCP
   language. Enable the module and launch Crusader, then Extreme; confirm there
   is no startup error.
2. **Workers and saves:** start a match with a developed AI castle, place and remove
   walls/buildings, and observe staffing and weapon deliveries. Save, exit, reload,
   and check again. Repeat with the preserved stalled-worker save. A single worker
   moving again is insufficient evidence: the bug previously cleared temporarily.
3. **Moats:** give dig/fill orders with no eligible target and with a small eligible
   moat. Check the first available tile as well as later tiles. Troops may still
   choose the original game's long approach route; this preview does not change it.
4. **Multiplayer and replay:** use identical module versions/settings on both PCs,
   build/remove walls and moats, save on each PC, then play each recording offline
   with its recorded setup. Check completion and determinism diagnostics.
5. **Performance:** compare repeated runs from the same save, with the same settings,
   camera and speed, both with and without the module. Report elapsed time for a
   fixed number of simulation ticks. A speed setting alone is not a measurement.

Do not enable this simulation change midway through a recording or use it to
silently replay a recording made without it. Passing the automated checks does
not replace these live checks or establish support for every extension combination.
