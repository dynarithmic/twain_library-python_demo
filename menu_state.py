import tkinter as tk
from tkinter import messagebox
from ctypes import *
import ctypes as ct
import dtwainapi
from app_constants import ACQUIRE_FILE_SOURCE_FORMATS
from blank_page_threshold_dialog import BlankPageThresholdDialog

def update_source_menu_state(state):
    enabled = state.source is not None
    menu_state = tk.NORMAL if enabled else tk.DISABLED
    state.source_menu.entryconfig(state.source_props_index, state=menu_state)
    state.source_menu.entryconfig(state.close_source_index, state=menu_state)

def update_source_mode_file_menu_state(dtwain_dll, state):
    menu = getattr(state, "source_mode_menu", None)
    items = getattr(state, "source_mode_menu_items", None)

    if not menu or not items:
        return

    # Disable all first
    for cmd, index in items.items():
        menu.entryconfig(index, state=tk.DISABLED)

    if not state.source:
        return

    fmt_array = dtwain_dll.DTWAIN_EnumFileXferFormatsEx(state.source)

    if not fmt_array:
        return

    supported_formats = set()

    try:
        count = dtwain_dll.DTWAIN_ArrayGetCount(fmt_array)

        for i in range(count):
            val = ct.c_long(0)
            ok = dtwain_dll.DTWAIN_ArrayGetAtLong(fmt_array,i,ct.byref(val))
            if ok:
                supported_formats.add(val.value)

    finally:
        dtwain_dll.DTWAIN_ArrayDestroy(fmt_array)

    for cmd, fmt_constant in ACQUIRE_FILE_SOURCE_FORMATS.items():
        index = items.get(cmd)

        if index is not None and fmt_constant in supported_formats:
            menu.entryconfig(index, state=tk.NORMAL)

def update_application_menu_state(dtwain_dll, state):
    has_source = state.source is not None
    menu_state = tk.NORMAL if has_source else tk.DISABLED

    for menu, index in state.source_required_menu_items:
        menu.entryconfig(index, state=menu_state)

    update_source_mode_file_menu_state(dtwain_dll, state)
    update_barcode_menu_state(dtwain_dll, state)


def update_barcode_menu_state(dtwain_dll, state):
    menu = getattr(state, "barcode_menu", None)
    index = getattr(state, "barcode_menu_index", None)

    if menu is None or index is None:
        return

    enabled = False

    if state.source:
        if (dtwain_dll.DTWAIN_IsExtImageInfoSupported(state.source)
            and
            dtwain_dll.DTWAIN_IsBarcodeSupported(state.source,dtwainapi.DTWAIN_ANYSUPPORT)):
            enabled = True

    menu.entryconfig(index,state=tk.NORMAL if enabled else tk.DISABLED)


def on_discard_blank_pages_changed(root, dtwain_dll, state, var):
    checked = var.get()

    if not state.source:
        var.set(False)
        state.discard_blank_pages = False
        messagebox.showwarning("DTWAIN", "No TWAIN source selected.")
        return

    if checked:
        dlg = BlankPageThresholdDialog(root,state.blank_page_threshold if state.blank_page_threshold else 95.0)

        if dlg.result is None:
            var.set(False)
            state.discard_blank_pages = False
            return

        ok = dtwain_dll.DTWAIN_SetBlankPageDetection(state.source,ct.c_double(dlg.result),dtwainapi.DTWAIN_BP_AUTODISCARD_ANY,1)

        if ok:
            state.discard_blank_pages = True
            state.blank_page_threshold = dlg.result
        else:
            var.set(False)
            state.discard_blank_pages = False
            messagebox.showerror("DTWAIN", "Unable to enable blank page detection.")

    else:
        dtwain_dll.DTWAIN_SetBlankPageDetection(state.source,ct.c_double(0.0),dtwainapi.DTWAIN_BP_AUTODISCARD_ANY,0)

        state.discard_blank_pages = False
        state.blank_page_threshold = 0.0

def apply_message_loop_setting(dtwain_dll, state):
    if not state.source:
        return

    # Checked means use GetMessage loop, so disable PeekMessage loop.
    use_peek = 0 if state.use_getmessage_loop else 1

    dtwain_dll.DTWAIN_EnablePeekMessageLoop(state.source,use_peek)
            