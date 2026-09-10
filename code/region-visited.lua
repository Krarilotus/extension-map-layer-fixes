-- Region IDs belong to the native connectivity layer and are unsigned shorts.
-- The original outer scan reads only a byte, revisiting regions 256, 512, etc.
local M={}
M.profiles={
  SHC={address=0x4996ce,regions=0x1df70d8},
  Extreme={address=0x49983e,regions=0x288a5d8},
}

local function word(bytes,value)
  value=value%4294967296
  for _=1,4 do bytes[#bytes+1]=value%256; value=math.floor(value/256) end
end

function M.original(site)
  local bytes={0x80,0x3c,0x45}; word(bytes,site.regions); bytes[#bytes+1]=0
  return bytes
end

-- Only the operand width changes. The original conditional branch consumes
-- these flags; the flood fill, queue, iteration order and refresh policy stay native.
function M.patch(site,target)
  local body={0x66,0x83,0x3c,0x45}; word(body,site.regions); body[#body+1]=0
  body[#body+1]=0xe9; word(body,site.address+8-target-14)
  local jump={0xe9}; word(jump,target-site.address-5)
  for _=1,3 do jump[#jump+1]=0x90 end
  return jump,body
end

function M.prepare()
  local address=core.AOBScan('80 3C 45 ? ? ? ? 00 0F 85 ? ? ? ? F7 04 85 ? ? ? ? B1 14 50 4A')
  local selected
  for _,site in pairs(M.profiles) do if address==site.address then selected=site end end
  assert(selected,'map-layer-fixes: unsupported connectivity scan')
  require('code/patch-bytes').verify(address,M.original(selected))
  local target=core.allocateCode(14)
  local jump,body=M.patch(selected,target)
  return function()
    core.writeCode(target,body)
    core.writeCode(address,jump)
  end
end
return M
