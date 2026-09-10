---@module 'map-layer-fixes'
local M={}

function M:enable()
  local region=require('code/region-visited').prepare()
  local moat=require('code/moat-selection').prepare()
  region()
  moat()
end

function M:disable()
  error('Restart the game to disable map-layer-fixes')
end

return M
