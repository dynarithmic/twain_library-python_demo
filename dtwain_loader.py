import dtwainapi
import struct
from pathlib import Path

def initialize_dtwain():
    app_dir = Path(__file__).resolve().parent

    dll_name = "dtwain64u.dll" if struct.calcsize("P") * 8 == 64 else "dtwain32u.dll"
    dll_path = app_dir / dll_name

    dtwain_dll = dtwainapi.load_dtwaindll(str(dll_path))
    dtwain_dll.DTWAIN_SysInitialize()
    return dtwain_dll

