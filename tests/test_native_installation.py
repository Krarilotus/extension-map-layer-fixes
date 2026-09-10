import re
from pathlib import Path
import tempfile
import unittest
import zipfile
from lupa.lua51 import LuaRuntime
from native_fixture import Native,GAME_DIR,ROOT
from tools.package import build

@unittest.skipUnless(GAME_DIR,'Set SHC_GAME_DIR to original 1.41 executable directory')
class NativeInstallationTests(unittest.TestCase):
    def test_packaged_module_installs_against_actual_executable_signatures(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination=Path(temporary)
            archive=build(destination)
            with zipfile.ZipFile(archive) as content:
                content.extractall(destination)
            self.check_variants(destination/archive.stem)

    def check_variants(self,root):
        for filename,region,moat in (
            ('Stronghold Crusader.exe',0x4996ce,0x5111d0),
            ('Stronghold_Crusader_Extreme.exe',0x49983e,0x511550)):
            with self.subTest(filename=filename):
                native=Native(filename); lua=LuaRuntime()
                def scan(pattern):
                    pattern=b''.join(b'.' if v=='?' else re.escape(bytes([int(v,16)])) for v in pattern.split())
                    hits=list(re.finditer(pattern,native.image,re.DOTALL))
                    self.assertEqual(len(hits),1)
                    return 0x400000+hits[0].start()
                core=lua.table()
                core.AOBScan=scan
                core.readBytes=lambda a,n:lua.table_from(list(native.uc.mem_read(a,n)))
                core.allocateCode=lambda n:0x3df1000 if n==14 else self.fail('Unexpected allocation')
                core.writeCode=lambda a,b:native.uc.mem_write(a,bytes(b.values()))
                lua.globals().core=core
                lua.globals().root=root.as_posix()
                lua.execute("package.path=root..'/?.lua;'..package.path; require('init'):enable()")
                self.assertEqual(native.uc.mem_read(region,1)[0],0xe9)
                self.assertEqual(native.uc.mem_read(moat+0x1fc,1)[0],0x78)
