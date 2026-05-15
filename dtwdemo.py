# This is the Dynarithmic TWAIN Library Full demo program, written in Python.
#
# Note that the DTWDEMO32 and DTWDEMO64 programs that are available in the DTWAIN package
# are written in C using the Windows API.  This python translation mimics as much as those
# demo programs.  This includes opening TWAIN sources in various ways, scanning and saving
# images to files, full Source capability testing, logging, etc.
# 
# To run you must 
# 
# 1) Have python installed along with tkinter and PIL python image processing packages.
# 2) All of the DTWAIN DLL's (dtwain32u.dll and dtwain64u.dll) are available, preferably
#    in the same directory as the .py files
# 3) The text resources (the bare minimum are twaininfo.txt, dtwain32.ini, and dtwain64.ini)
#    are available, again preferably in the same directory as the .py file.
#
# To run:
# python dtwdemo.py
#
# Note that if you are running the 32-bit version of python, dtwdemo.py will only work with 
# 32-bit TWAIN sources.  Similarly, if you are running the 64-bit version of python, dtwdemo.py
# will only with with 64-bit TWAIN sources.
# 
import tkinter as tk
from ctypes import *
import ctypes as ct
import sys
from dtwain_loader import initialize_dtwain
from app_state import TwainState
from source_actions import close_current_source
from dtwain_callback import setup_dtwain_callback
from menu_builder import build_dtwdemo_menu

def on_close():
    try:
        dtwain_dll.DTWAIN_SetCallback(None, 0)
        dtwain_dll.DTWAIN_SetLoggerCallbackA(None, 0)
    except Exception:
        pass

    close_current_source(root, dtwain_dll, twain_state)
    dtwain_dll.DTWAIN_SysDestroy()
    root.destroy()

if __name__ == "__main__":
    kernel32 = ct.windll.kernel32
    kernel32.SetConsoleOutputCP(65001)
    kernel32.SetConsoleCP(65001)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    root = tk.Tk()
    root.title("DTWAIN Demo Program")
    root.geometry("900x600")
    twain_state = TwainState()
    dtwain_dll = initialize_dtwain()
    setup_dtwain_callback(root, dtwain_dll, twain_state)
    build_dtwdemo_menu(root, dtwain_dll, twain_state)
    root.mainloop()
