# Map Layer Fixes

Fixes two errors in Crusader 1.41 and Extreme 1.41: connected ground can be split
into unnecessary pathfinding regions, and moat selection can write outside its array
when no suitable tile exists. The 1,000-region limit and the way troops choose
which side of a moat to approach are unchanged.

Requires UCP3 3.0.7 or later. Enable the module in the launcher and restart the game;
there are no extra settings or buttons. All multiplayer players must use the same
module version and settings. Play replays with the setup used to record them.

Experimental preview: automated checks pass in both game versions; live gameplay,
save/load and multiplayer tests are still pending. It is not a proven fix for every
stalled worker or slow match. Keep a copy of your saves before testing.
