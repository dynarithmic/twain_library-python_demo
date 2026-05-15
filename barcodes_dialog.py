import tkinter as tk
from ctypes import *
import dtwainapi
import ctypes as ct
from tkinter import ttk

class BarCodesDialog(tk.Toplevel):
    def __init__(self, parent, text):
        super().__init__(parent)

        self.parent = parent

        self.withdraw()
        self.title("Bar Codes Found")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        self.txt_barcodes = tk.Text(main,width=80,height=18,wrap="none",font=("Consolas", 9))
        self.txt_barcodes.grid(row=0, column=0, columnspan=2, sticky="nsew")

        yscroll = ttk.Scrollbar(main, orient="vertical", command=self.txt_barcodes.yview)
        yscroll.grid(row=0, column=2, sticky="ns")

        xscroll = ttk.Scrollbar(main, orient="horizontal", command=self.txt_barcodes.xview)
        xscroll.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.txt_barcodes.configure(yscrollcommand=yscroll.set,xscrollcommand=xscroll.set)

        buttons = ttk.Frame(main)
        buttons.grid(row=2, column=0, columnspan=2, sticky="e", pady=(8, 0))

        ttk.Button(buttons, text="OK", command=self.destroy).pack(side="left", padx=4)
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="left", padx=4)

        main.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.txt_barcodes.insert("1.0", text)
        self.txt_barcodes.configure(state="disabled")

        self.update_idletasks()
        self.center_over_parent()
        self.deiconify()

        self.wait_window(self)

    def center_over_parent(self):
        px = self.parent.winfo_rootx()
        py = self.parent.winfo_rooty()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()

        w = self.winfo_width()
        h = self.winfo_height()

        x = px + (pw - w) // 2
        y = py + (ph - h) // 2

        self.geometry(f"+{x}+{y}")


def should_show_barcode_info(menu, index, var):
    try:
        return (var.get() and menu.entrycget(index, "state") != tk.DISABLED)
    except Exception:
        return False

def build_barcode_info_text(dtwain_dll, source):
    lines = []

    if not source:
        return ""

    ok = dtwain_dll.DTWAIN_InitExtImageInfo(source)

    if not ok:
        return ""

    a_count = None
    a_text = None
    a_type = None

    try:
        a_count = dtwain_dll.DTWAIN_GetExtImageInfoDataEx(source,dtwainapi.DTWAIN_EI_BARCODECOUNT)

        if not a_count:
            return ""

        count_items = dtwain_dll.DTWAIN_ArrayGetCount(a_count)

        if count_items <= 0:
            return ""

        bar_count = ct.c_long(0)

        ok = dtwain_dll.DTWAIN_ArrayGetAtLong(a_count,0,ct.byref(bar_count))

        if not ok or bar_count.value <= 0:
            return ""

        lines.append(f"Bar Code Count: {bar_count.value}")
        lines.append("")

        a_text = dtwain_dll.DTWAIN_GetExtImageInfoDataEx(source,dtwainapi.DTWAIN_EI_BARCODETEXT)
        a_type = dtwain_dll.DTWAIN_GetExtImageInfoDataEx(source,dtwainapi.DTWAIN_EI_BARCODETYPE)
        if not a_text or not a_type:
            return "\n".join(lines)

        for i in range(bar_count.value):
            lines.append(f"Bar Code {i + 1}:")
            text_ptr = dtwain_dll.DTWAIN_ArrayGetAtANSIStringPtr(a_text,i)
            if text_ptr:
                text_value = ct.cast(text_ptr, ct.c_char_p).value
                text = text_value.decode("mbcs", errors="replace") if text_value else ""
            else:
                text = ""

            lines.append(f"     Text: {text}")

            n_type = ct.c_long(0)

            ok = dtwain_dll.DTWAIN_ArrayGetAtLong(a_type,i,ct.byref(n_type))

            if ok:
                type_buf = ct.create_string_buffer(100)

                dtwain_dll.DTWAIN_GetTwainNameFromConstantExA(dtwainapi.DTWAIN_CONSTANT_TWBT,n_type.value,type_buf,len(type_buf))
                type_name = type_buf.value.decode("mbcs", errors="replace")
            else:
                type_name = ""

            lines.append(f"     Type: {type_name}")
            lines.append("")

        return "\n".join(lines)

    finally:
        if a_count:
            dtwain_dll.DTWAIN_ArrayDestroy(a_count)

        if a_text:
            dtwain_dll.DTWAIN_ArrayDestroy(a_text)

        if a_type:
            dtwain_dll.DTWAIN_ArrayDestroy(a_type)

        dtwain_dll.DTWAIN_FreeExtImageInfo(source)

def display_barcode_info(root, dtwain_dll, state):
    text = build_barcode_info_text(dtwain_dll, state.source)

    if not text:
        text = "No barcode information found."

    BarCodesDialog(root, text)
