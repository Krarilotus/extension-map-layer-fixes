"""Portable installation guards; native behavior is verified with original EXEs."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]

class InstallationTests(unittest.TestCase):
    def check(self, variant, failure=None):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.globals().root = ROOT.as_posix()
        lua.globals().variant = variant
        lua.globals().failure = failure
        lua.execute('''
package.path=root..'/?.lua;'..package.path
local region=require('code/region-visited')
local moat=require('code/moat-selection')
local memory,writes={},{}
local function put(a,bytes) for i,v in ipairs(bytes) do memory[a+i-1]=v end end
local site=region.profiles[variant]
put(site.address,region.original(site))
for _,change in ipairs(moat.patches(moat.profiles[variant])) do put(change.address,change.expected) end
if failure=='region-bytes' then memory[site.address]=0 end
if failure=='moat-bytes' then memory[moat.profiles[variant]+0x1fc]=0 end
core={
 AOBScan=function(pattern)
  if pattern:sub(1,2)=='80' then return failure=='unknown-region' and 123 or site.address end
  return failure=='unknown-moat' and 456 or moat.profiles[variant]
 end,
 readBytes=function(a,n) local b={} for i=1,n do b[i]=memory[a+i-1] end return b end,
 allocateCode=function(n) assert(n==14); return 0x3000000 end,
 writeCode=function(a,b) writes[#writes+1]={a,b}; put(a,b) end,
}
local ok,reason=pcall(function() require('init'):enable() end)
if failure then assert(not ok and #writes==0,tostring(reason))
else
 assert(ok,reason); assert(#writes==4)
 assert(writes[1][1]==0x3000000 and #writes[1][2]==14)
 assert(writes[2][1]==site.address and #writes[2][2]==8)
 assert(memory[moat.profiles[variant]+0x1fc]==0x78)
end
''')

    def test_supported_variants(self):
        for variant in ('SHC', 'Extreme'):
            with self.subTest(variant=variant): self.check(variant)

    def test_any_conflict_prevents_all_code_writes(self):
        for variant in ('SHC', 'Extreme'):
            for failure in ('region-bytes','moat-bytes','unknown-region','unknown-moat'):
                with self.subTest(variant=variant,failure=failure): self.check(variant,failure)

if __name__ == '__main__': unittest.main()
