import dtwainapi
import struct
from pathlib import Path

def initialize_dtwain():
    dll_name = "dtwain64u.dll" if struct.calcsize("P") * 8 == 64 else "dtwain32u.dll"
    dtwain_dll = dtwainapi.load_dtwaindll(dll_name)
    dtwain_dll.DTWAIN_SysInitialize()
    return dtwain_dll

