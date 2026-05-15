import tkinter as tk
from tkinter import messagebox
from ctypes import *
import ctypes as ct
from tkinter import ttk

class AboutDialog(tk.Toplevel):
    def __init__(self, parent, dtwain_dll):
        super().__init__(parent)

        self.parent = parent
        self.dtwain_dll = dtwain_dll

        self.withdraw()
        self.title("About")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self.load_version_info()

        self.update_idletasks()
        self.center_over_parent()
        self.deiconify()
        self.focus_set()
        self.wait_window(self)

    def _build_ui(self):
        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="DTWDEMO Example").grid(row=0, column=0, sticky="w", padx=(30, 8))

        ttk.Button(main, text="OK", command=self.destroy).grid(row=0, column=1, sticky="e", padx=(20, 0))

        self.txt_info = tk.Text(main,width=70,height=10,wrap="none",font=("Consolas", 9))
        self.txt_info.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(6, 0))

        yscroll = ttk.Scrollbar(main, orient="vertical", command=self.txt_info.yview)
        yscroll.grid(row=1, column=2, sticky="ns")

        xscroll = ttk.Scrollbar(main, orient="horizontal", command=self.txt_info.xview)
        xscroll.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.txt_info.configure(yscrollcommand=yscroll.set,xscrollcommand=xscroll.set)

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def load_version_info(self):
        buf = ct.create_string_buffer(1000)

        ok = self.dtwain_dll.DTWAIN_GetVersionInfoA(buf,len(buf))

        text = buf.value.decode("mbcs", errors="replace") if ok else "Unable to retrieve DTWAIN version information."

        self.txt_info.delete("1.0", tk.END)
        self.txt_info.insert(tk.END, text)
        self.txt_info.configure(state="disabled")

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

