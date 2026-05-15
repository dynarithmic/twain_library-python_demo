import dtwainapi
from ctypes import *
import ctypes as ct
import tkinter as tk
from tkinter import messagebox
from enum import Enum, auto
from enter_source_name_dialog import EnterSourceNameDialog
from select_source_custom_dialog import SelectSourceCustomDialog
from menu_state import update_source_menu_state
from menu_state import update_source_mode_file_menu_state
from menu_state import update_application_menu_state
from menu_state import update_barcode_menu_state

class SourceSelectMode(Enum):
    DIALOG = auto()
    BY_NAME = auto()
    DEFAULT = auto()
    CUSTOM = auto()

def close_current_source(root, dtwain_dll, state):
    if state.source:
        try:
            dtwain_dll.DTWAIN_CloseSource(state.source)
        finally:
            state.source = None
            state.source_name = ""
            root.title("DTWAIN Demo Program")
            update_source_menu_state(state)
            update_source_mode_file_menu_state(dtwain_dll, state)
            update_application_menu_state(dtwain_dll, state)

def select_source_common(root, dtwain_dll, state, mode):
    selected_name = None

    # Close currently open source first
    close_current_source(root, dtwain_dll, state)

    if mode == SourceSelectMode.DIALOG:
        src = dtwain_dll.DTWAIN_SelectSource2(None,"Python Test",0,0,
                                              dtwainapi.DTWAIN_DLG_CENTER_CURRENT_MONITOR | 
                                              dtwainapi.DTWAIN_DLG_SORTNAMES | dtwainapi.DTWAIN_DLG_HIGHLIGHTFIRST)

    elif mode == SourceSelectMode.BY_NAME:
        dlg = EnterSourceNameDialog(root)
        if not dlg.result:
            return

        selected_name = dlg.result
        src = dtwain_dll.DTWAIN_SelectSourceByNameA(selected_name.encode("mbcs"))

    elif mode == SourceSelectMode.DEFAULT:
        src = dtwain_dll.DTWAIN_SelectDefaultSource()

    elif mode == SourceSelectMode.CUSTOM:
        dlg = SelectSourceCustomDialog(root, dtwain_dll)
        if not dlg.result:
            return

        selected_name = dlg.result
        src = dtwain_dll.DTWAIN_SelectSourceByNameA(selected_name.encode("mbcs"))

    else:
        messagebox.showerror("DTWAIN", "Unknown source selection mode.")
        return

    if not src:
        update_source_menu_state(state)
        update_source_mode_file_menu_state(dtwain_dll, state)
        messagebox.showwarning("DTWAIN", "No source selected.")
        return

    state.source = src

    # Get actual product name from opened source
    buf = ct.create_string_buffer(256)

    if dtwain_dll.DTWAIN_GetSourceProductNameA(src, buf, len(buf)):
        state.source_name = buf.value.decode("mbcs", errors="replace")
    else:
        state.source_name = selected_name or "Selected Source"

    # Enable the barcode detection (only valid if source supports barcode detection)
    dtwain_dll.DTWAIN_EnableBarcodeDetection(state.source, 1)

    root.title(f"DTWAIN Demo Program - {state.source_name}")

    update_source_menu_state(state)
    update_source_mode_file_menu_state(dtwain_dll, state)
    update_barcode_menu_state(dtwain_dll, state)
    update_application_menu_state(dtwain_dll, state)

    messagebox.showinfo("DTWAIN",f"Source selected:\n{state.source_name}")

