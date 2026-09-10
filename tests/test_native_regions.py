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
    def rebuild(self,variant,fixed,first_region,stale=False):
        profile=PROFILES[variant]
        patch=module('region-visited.lua')
        filename,entry,state,regions,logic,linkage,clear,display,compare=profile
        native=Native(filename); uc=native.uc
        uc.mem_write(logic,struct.pack('<I',1)*80400)
        islands=[5000+i*3 for i in range(first_region-1)]
        chain=list(range(9000,9005))
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
        if stale:
            uc.mem_write(regions,struct.pack('<H',999)*80400)
            native.put(state+0xcc,1000)
        native.call(entry,state,[1],10000000)
        labels=[struct.unpack('<H',uc.mem_read(regions+tile*2,2))[0] for tile in chain]

        return labels,native.get(state+0xcc),native.get(state+0x1080)

    def test_zero_low_byte_region_ids_preserve_connected_ground(self):
        for variant in PROFILES:
            for first in (256,512,768):
                for fixed in (False,True):
                    with self.subTest(variant=variant,first=first,fixed=fixed):
                        labels,next_region,total=self.rebuild(variant,fixed,first)
                        self.assertEqual(labels,[first]*5 if fixed else list(range(first,first+5)))
                        self.assertEqual(next_region,first+1 if fixed else first+5)
                        self.assertEqual(total,first+4 if fixed else first+8)

    def test_forced_rebuild_replaces_old_fragmented_saved_labels(self):
        for variant in PROFILES:
            with self.subTest(variant=variant):
                self.assertEqual(self.rebuild(variant,True,256,stale=True),
                                 self.rebuild(variant,True,256))

    def test_ordinary_regions_and_capacity_boundary_keep_native_behavior(self):
        for variant in PROFILES:
            for first in (1,255,999,1000):
                with self.subTest(variant=variant,first=first):
                    original=self.rebuild(variant,False,first)
                    corrected=self.rebuild(variant,True,first)
                    self.assertEqual(corrected,original)
                    self.assertLessEqual(corrected[1],1000)
