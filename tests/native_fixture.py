"""Optional original-executable fixture. Never accesses a running game."""
from pathlib import Path
import os
import struct
import pefile
from lupa.lua51 import LuaRuntime
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn import x86_const as registers

ROOT=Path(__file__).resolve().parents[1]
GAME_DIR=os.environ.get('SHC_GAME_DIR')

def module(name):
    lua=LuaRuntime(unpack_returned_tuples=True)
    lua.globals().module_path=(ROOT/'code'/name).as_posix()
    return lua.execute('return dofile(module_path)')

class Native:
    def __init__(self, filename):
        path=Path(GAME_DIR)/filename
        pe=pefile.PE(str(path))
        assert pe.OPTIONAL_HEADER.ImageBase==0x400000
        self.image=pe.get_memory_mapped_image()
        self.uc=Uc(UC_ARCH_X86,UC_MODE_32)
        self.uc.mem_map(0x400000,0x3e00000)
        self.uc.mem_write(0x400000,self.image)

    def put(self,address,value):
        self.uc.mem_write(address,struct.pack('<I',value&0xffffffff))

    def get(self,address):
        return struct.unpack('<I',self.uc.mem_read(address,4))[0]

    def call(self,entry,owner,args,count=100000):
        stack,stop=0x4108000,0x3df0000
        self.uc.mem_write(stack,struct.pack('<'+'I'*(len(args)+1),stop,*args))
        self.uc.reg_write(registers.UC_X86_REG_ESP,stack)
        self.uc.reg_write(registers.UC_X86_REG_ECX,owner)
        self.uc.emu_start(entry,stop,count=count)
        assert self.uc.reg_read(registers.UC_X86_REG_EIP)==stop
        assert self.uc.reg_read(registers.UC_X86_REG_ESP)==stack+4*(len(args)+1)
        return self.uc.reg_read(registers.UC_X86_REG_EAX)
