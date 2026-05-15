import tkinter as tk
from ctypes import *
from tkinter import ttk
from PIL import ImageTk

class KeepAcquiredImageDialog(tk.Toplevel):
    def __init__(self, parent, pil_image):
        super().__init__(parent)

        self.parent = parent
        self.result = 0
        self.photo = None

        self.withdraw()
        self.title("Keep Acquired Image?")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui(pil_image)

        self.update_idletasks()
        self.center_over_parent()
        self.deiconify()

        self.wait_window(self)

    def _build_ui(self, pil_image):
        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        image_frame = ttk.Frame(main, width=384, height=396, relief="solid")
        image_frame.grid(row=0, column=0, rowspan=3, padx=(0, 10), pady=4)
        image_frame.grid_propagate(False)

        preview = pil_image.copy()
        preview.thumbnail((384, 396))

        self.photo = ImageTk.PhotoImage(preview)

        image_label = ttk.Label(image_frame, image=self.photo, anchor="center")
        image_label.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Button(main, text="Yes", command=self.on_yes).grid(
            row=0, column=1, sticky="ew", pady=(4, 4)
        )

        ttk.Button(main, text="No", command=self.on_no).grid(
            row=1, column=1, sticky="ew", pady=(0, 4)
        )

        self.protocol("WM_DELETE_WINDOW", self.on_no)

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

    def on_yes(self):
        self.result = 1
        self.destroy()

    def on_no(self):
        self.result = 0
        self.destroy()