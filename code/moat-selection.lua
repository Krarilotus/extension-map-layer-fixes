-- Moat indexes are zero-based. -1 means that no candidate was found.
local M={}
M.profiles={SHC=0x5111d0,Extreme=0x511550}

function M.patches(entry)
  return {
    -- An empty list must return -1 without reserving moats[-1].
    {address=entry+0x5d,expected={0x0f,0x8e,0x9b,0x01,0,0},
      bytes={0x0f,0x8e,0xaf,0x01,0,0}},
    -- Skip negative results, not index zero. Preserve positive candidates.
    {address=entry+0x1fc,expected={0x74,0x14},bytes={0x78,0x14}},
  }
end

function M.prepare()
  local entry=core.AOBScan('83 EC 18 53 8B 5C 24 24 69 DB 90 04 00 00 0F BF 93 ? ? ? ? 55 8B E9')
  assert(entry==M.profiles.SHC or entry==M.profiles.Extreme,
    'map-layer-fixes: unsupported moat selector')
  local changes=M.patches(entry)
  for _,change in ipairs(changes) do
    require('code/patch-bytes').verify(change.address,change.expected)
  end
  return function()
    for _,change in ipairs(changes) do core.writeCode(change.address,change.bytes) end
  end
end

return M
