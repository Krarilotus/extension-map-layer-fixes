-- Exact original-byte validation must finish before any executable code changes.
local M={}

function M.verify(address,expected)
  local actual=core.readBytes(address,#expected)
  for i,byte in ipairs(expected) do
    assert(actual[i]==byte,'map-layer-fixes: unsupported or already modified native code')
  end
end

return M
