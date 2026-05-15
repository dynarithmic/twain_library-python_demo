import tkinter as tk
from ctypes import *
from tkinter import ttk

class EnterSourceNameDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.result = None

        self.withdraw()
        self.title("Source Name")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Source Name:").grid(row=0, column=0, padx=(0, 8), pady=6)

        self.source_name_var = tk.StringVar()
        self.entry = ttk.Entry(main, textvariable=self.source_name_var, width=28)
        self.entry.grid(row=0, column=1, columnspan=2, pady=6)

        ttk.Button(main, text="OK", command=self.on_ok).grid(row=1, column=1, padx=4, pady=(8, 0))
        ttk.Button(main, text="Cancel", command=self.on_cancel).grid(row=1, column=2, padx=4, pady=(8, 0))

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self.update_idletasks()
        self.center_over_parent()
        self.deiconify()

        self.entry.focus_set()
        self.entry.bind("<Return>", lambda e: self.on_ok())
        self.entry.bind("<Escape>", lambda e: self.on_cancel())

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

    def on_ok(self):
        self.result = self.source_name_var.get().strip()
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

