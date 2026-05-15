import tkinter as tk
from tkinter import messagebox
from ctypes import *
from tkinter import ttk

class BlankPageThresholdDialog(tk.Toplevel):
    def __init__(self, parent, initial_value=95.0):
        super().__init__(parent)

        self.parent = parent
        self.result = None

        self.withdraw()
        self.title("Blank Page Threshold")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        main = ttk.Frame(self, padding=12)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Threshold Percentage:").grid(row=0, column=0, padx=(0, 8), pady=8)

        self.threshold_var = tk.StringVar(value=str(initial_value))
        self.entry = ttk.Entry(main, textvariable=self.threshold_var, width=8)
        self.entry.grid(row=0, column=1, pady=8)

        ttk.Button(main, text="OK", command=self.on_ok).grid(row=1, column=0, padx=4, pady=(10, 0))
        ttk.Button(main, text="Cancel", command=self.on_cancel).grid(row=1, column=1, padx=4, pady=(10, 0))

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self.update_idletasks()
        self.center_over_parent()
        self.deiconify()

        self.entry.focus_set()
        self.entry.select_range(0, tk.END)
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
        try:
            value = float(self.threshold_var.get())
        except ValueError:
            messagebox.showerror("DTWAIN", "Please enter a valid percentage.")
            return

        if not (0.0 <= value <= 100.0):
            messagebox.showerror("DTWAIN", "Percentage must be between 0 and 100.")
            return

        self.result = value
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()
