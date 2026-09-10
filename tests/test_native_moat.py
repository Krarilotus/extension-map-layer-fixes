import struct
import unittest
from native_fixture import Native,GAME_DIR,module

PROFILES={
 'SHC':('Stronghold Crusader.exe',0x5111d0,0x1a93208,0x1388610,0x2337300),
 'Extreme':('Stronghold_Crusader_Extreme.exe',0x511550,0x2526708,0x145d100,0x2dca800),
}

@unittest.skipUnless(GAME_DIR,'Set SHC_GAME_DIR to original 1.41 executable directory')
class NativeMoatTests(unittest.TestCase):
    def test_failure_does_not_reserve_invalid_index_and_zero_is_valid(self):
        patch=module('moat-selection.lua')
        for variant,profile in PROFILES.items():
            for case in ('empty','no-candidate','first-candidate','second-candidate'):
                for fixed in (False,True):
                    with self.subTest(variant=variant,case=case,fixed=fixed):
                        filename,entry,state,unit_xy,row_add=profile
                        native=Native(filename); uc=native.uc
                        moat=state+0x500870
                        uc.mem_write(moat-1,b'\x07')
                        uc.mem_write(moat,bytes(32))
                        native.put(state+0x53f070,{'empty':0,'no-candidate':1,'first-candidate':1,'second-candidate':2}[case])
                        uc.mem_write(unit_xy+0x490,struct.pack('<hh',10,10))
                        native.put(row_add+10*12,1000)
                        selected=1 if case=='second-candidate' else 0
                        valid=case in ('first-candidate','second-candidate')
                        if valid:
                            record=moat+selected*16
                            native.put(record,1010)
                            uc.mem_write(record+4,struct.pack('<hh',10,10))
                            uc.mem_write(record+12,bytes([1,0,1,7]))
                            native.put(state+0x165160+1010*4,0x4000)
                        if fixed:
                            for change in patch.patches(entry).values():
                                expected=bytes(change.expected.values())
                                self.assertEqual(bytes(uc.mem_read(change.address,len(expected))),expected)
                                uc.mem_write(change.address,bytes(change.bytes.values()))
                        self.assertEqual(native.call(entry,state,[1,1,1]),selected if valid else 0xffffffff)
                        self.assertEqual(uc.mem_read(moat-1,1)[0],7 if fixed or valid else 27)
                        if valid:
                            self.assertEqual(uc.mem_read(moat+selected*16+15,1)[0],27 if fixed or selected else 7)
