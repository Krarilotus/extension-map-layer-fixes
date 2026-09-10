import struct
import unittest
from unicorn import UC_HOOK_CODE
from native_fixture import Native,GAME_DIR,module,registers

PROFILES={
 'SHC':('Stronghold Crusader.exe',0x4995e0,0x12bb8c8,0x1df70d8,0x1bf8368,0x1e1e4f8,0x4718c0,0x419910,0x4996ce),
 'Extreme':('Stronghold_Crusader_Extreme.exe',0x499750,0x13903b8,0x288a5d8,0x268b868,0x28b19f8,0x471ae0,0x419970,0x49983e),
}

@unittest.skipUnless(GAME_DIR,'Set SHC_GAME_DIR to original 1.41 executable directory')
class NativeRegionTests(unittest.TestCase):
    def test_connected_region_256_keeps_its_identity_and_tile_count(self):
        patch=module('region-visited.lua')
        for variant,profile in PROFILES.items():
            for fixed in (False,True):
                with self.subTest(variant=variant,fixed=fixed):
                    filename,entry,state,regions,logic,linkage,clear,display,compare=profile
                    native=Native(filename); uc=native.uc
                    uc.mem_write(logic,struct.pack('<I',1)*80400)
                    islands=[5000+i*3 for i in range(255)]
                    chain=list(range(6000,6005))
                    for tile in islands+chain: native.put(logic+tile*4,0)
                    for i,tile in enumerate(chain):
                        uc.mem_write(linkage+tile,bytes([(0x40 if i else 0)|(4 if i+1<len(chain) else 0)]))
                    self.assertEqual(bytes(uc.mem_read(compare,8)),bytes(patch.original(patch.profiles[variant]).values()))
                    if fixed:
                        jump,body=patch.patch(patch.profiles[variant],0x3df1000)
                        uc.mem_write(0x3df1000,bytes(body.values()))
                        uc.mem_write(compare,bytes(jump.values()))
                    # Only memset and loading-display services are stand-ins.
                    uc.mem_write(clear,b'\xc2\x0c\x00')
                    uc.mem_write(display,b'\xc2\x04\x00')
                    def clear_memory(machine,ip,size,_):
                        sp=machine.reg_read(registers.UC_X86_REG_ESP)
                        length,value,destination=(native.get(sp+offset) for offset in (4,8,12))
                        assert length in (160800,4000) and value==0
                        machine.mem_write(destination,bytes(length))
                    uc.hook_add(UC_HOOK_CODE,clear_memory,begin=clear,end=clear)
                    native.call(entry,state,[1],10000000)
                    labels=[struct.unpack('<H',uc.mem_read(regions+tile*2,2))[0] for tile in chain]
                    self.assertEqual(labels,[256]*5 if fixed else [256,257,258,259,260])
                    self.assertEqual(native.get(state+0xcc),257 if fixed else 261)
                    self.assertEqual(native.get(state+0x1080),260 if fixed else 264)
