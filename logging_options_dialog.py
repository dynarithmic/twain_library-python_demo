import tkinter as tk
from tkinter import messagebox
from ctypes import *
import dtwainapi
from tkinter import ttk

from logger_callback import enable_logger_callback_console

class LoggingOptionsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.result = None

        self.withdraw()
        self.title("Log File Selection")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.log_mode_var = tk.StringVar(value="none")
        self.log_filename_var = tk.StringVar(value="dtwain.log")

        self._build_ui()

        self.update_idletasks()
        self.center_over_parent()
        self.deiconify()

        self.wait_window(self)

    def _build_ui(self):
        main = ttk.Frame(self, padding=14)
        main.pack(fill="both", expand=True)

        ttk.Radiobutton(main,text="No Logging",variable=self.log_mode_var,value="none",
                        command=self.update_controls).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        ttk.Radiobutton(main,text="Log to File:",variable=self.log_mode_var,value="file",
                        command=self.update_controls).grid(row=1, column=0, sticky="w", pady=(0, 12))

        self.ed_log_filename = ttk.Entry(main,textvariable=self.log_filename_var,width=32)
        self.ed_log_filename.grid(row=1, column=1, sticky="ew", pady=(0, 12))

        ttk.Radiobutton(main,text="Log to Debug Monitor",variable=self.log_mode_var,value="monitor",
                        command=self.update_controls).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 12))

        ttk.Radiobutton(main,text="Log to Console",variable=self.log_mode_var,value="console",
                        command=self.update_controls).grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 18))

        buttons = ttk.Frame(main)
        buttons.grid(row=4, column=0, columnspan=2)

        ttk.Button(buttons, text="OK", command=self.on_ok).pack(side="left", padx=8)
        ttk.Button(buttons, text="Cancel", command=self.on_cancel).pack(side="left", padx=8)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self.update_controls()

    def update_controls(self):
        if self.log_mode_var.get() == "file":
            self.ed_log_filename.configure(state=tk.NORMAL)
        else:
            self.ed_log_filename.configure(state=tk.DISABLED)

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
        self.result = {
            "mode": self.log_mode_var.get(),
            "filename": self.log_filename_var.get().strip()
        }
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()


def show_logging_options(root, dtwain_dll, state):
    dlg = LoggingOptionsDialog(root)

    if dlg.result is None:
        return

    log_mode = dlg.result["mode"]
    log_filename = dlg.result["filename"]

    log_flags = (
        dtwainapi.DTWAIN_LOG_ALL
        & ~dtwainapi.DTWAIN_LOG_ISTWAINMSG
        & ~dtwainapi.DTWAIN_LOG_USEFILE
        & ~dtwainapi.DTWAIN_LOG_DEBUGMONITOR
        & ~dtwainapi.DTWAIN_LOG_CONSOLE
    )

    # Make logging exclusive: turn everything off first
    dtwain_dll.DTWAIN_SetTwainLogA(0, b"")

    if log_mode == "none":
        return

    elif log_mode == "file":
        if not log_filename:
            messagebox.showwarning("DTWAIN", "No log file name was entered.")
            return
        dtwain_dll.DTWAIN_SetTwainLogA(dtwainapi.DTWAIN_LOG_USEFILE | log_flags,log_filename.encode("mbcs"))

    elif log_mode == "monitor":
        dtwain_dll.DTWAIN_SetTwainLogA(dtwainapi.DTWAIN_LOG_DEBUGMONITOR | log_flags,b"")

    elif log_mode == "console":
        enable_logger_callback_console(dtwain_dll, state)
        dtwain_dll.DTWAIN_SetTwainLogA(dtwainapi.DTWAIN_LOG_USECALLBACK | log_flags,b"")
