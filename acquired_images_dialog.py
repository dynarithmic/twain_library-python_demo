import tkinter as tk
from ctypes import *
from tkinter import ttk
from PIL import ImageTk
from dib_to_pillow_helper import dib_handle_to_pil_image

class AcquiredImagesDialog(tk.Toplevel):
    def __init__(self, parent, dtwain_dll, acquisitions):
        super().__init__(parent)

        self.parent = parent
        self.dtwain_dll = dtwain_dll
        self.acquisitions = acquisitions

        self.current_acq = 0
        self.current_page = 0
        self.photo = None

        self.withdraw()
        self.title("Acquired Images")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._populate_acquisitions()

        self.update_idletasks()
        self.center_over_parent()
        self.deiconify()

        self.show_current_image()

        self.wait_window(self)

    def _build_ui(self):
        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        self.image_frame = ttk.Frame(main, width=384, height=396, relief="solid")
        self.image_frame.grid(row=0, column=0, rowspan=4, padx=(0, 10), pady=4)
        self.image_frame.grid_propagate(False)

        self.image_label = ttk.Label(self.image_frame, anchor="center")
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Button(main, text="OK", command=self.on_close).grid(row=0, column=1, sticky="ew", pady=(4, 4))
        ttk.Button(main, text="Cancel", command=self.on_close).grid(row=1, column=1, sticky="ew", pady=(0, 4))

        nav = ttk.Frame(main)
        nav.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        ttk.Label(nav, text="Acquisition:").pack(side="left")

        self.cmb_acquisition = ttk.Combobox(nav, state="readonly", width=6)
        self.cmb_acquisition.pack(side="left", padx=(4, 12))
        self.cmb_acquisition.bind("<<ComboboxSelected>>", self.on_acquisition_changed)

        self.btn_prev = ttk.Button(nav, text="Previous", command=self.on_prev)
        self.btn_prev.pack(side="left", padx=(0, 4))

        self.btn_next = ttk.Button(nav, text="Next", command=self.on_next)
        self.btn_next.pack(side="left", padx=(0, 12))

        ttk.Label(nav, text="Page").pack(side="left")

        self.cur_page_var = tk.StringVar(value="1")
        ttk.Entry(nav, textvariable=self.cur_page_var, width=4, state="readonly").pack(side="left", padx=(4, 4))

        ttk.Label(nav, text="Of").pack(side="left")

        self.num_pages_var = tk.StringVar(value="0")
        ttk.Entry(nav, textvariable=self.num_pages_var, width=4, state="readonly").pack(side="left", padx=(4, 0))

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _populate_acquisitions(self):
        num_acqs = self.dtwain_dll.DTWAIN_GetNumAcquisitions(self.acquisitions)

        values = [str(i + 1) for i in range(num_acqs)]
        self.cmb_acquisition["values"] = values

        if values:
            self.cmb_acquisition.current(0)

    def get_num_pages_for_current_acq(self):
        return self.dtwain_dll.DTWAIN_GetNumAcquiredImages(
            self.acquisitions,
            self.current_acq
        )

    def show_current_image(self):
        num_pages = self.get_num_pages_for_current_acq()

        self.num_pages_var.set(str(num_pages))

        if num_pages <= 0:
            self.cur_page_var.set("0")
            self.image_label.configure(image="", text="<no images>")
            self.update_nav_buttons()
            return

        if self.current_page < 0:
            self.current_page = 0

        if self.current_page >= num_pages:
            self.current_page = num_pages - 1

        hdib = self.dtwain_dll.DTWAIN_GetAcquiredImage(self.acquisitions,self.current_acq,self.current_page)

        if not hdib:
            self.image_label.configure(image="", text="<unable to retrieve image>")
            self.cur_page_var.set(str(self.current_page + 1))
            self.update_nav_buttons()
            return

        pil_img = dib_handle_to_pil_image(hdib)

        preview = pil_img.copy()
        preview.thumbnail((384, 396))

        self.photo = ImageTk.PhotoImage(preview)
        self.image_label.configure(image=self.photo, text="")

        self.cur_page_var.set(str(self.current_page + 1))
        self.update_nav_buttons()

    def update_nav_buttons(self):
        num_pages = self.get_num_pages_for_current_acq()

        self.btn_prev.configure(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.btn_next.configure(state=tk.NORMAL if self.current_page + 1 < num_pages else tk.DISABLED)

    def on_acquisition_changed(self, event=None):
        sel = self.cmb_acquisition.get()

        if not sel:
            return

        self.current_acq = int(sel) - 1
        self.current_page = 0
        self.show_current_image()

    def on_prev(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_current_image()

    def on_next(self):
        num_pages = self.get_num_pages_for_current_acq()

        if self.current_page + 1 < num_pages:
            self.current_page += 1
            self.show_current_image()

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

    def on_close(self):
        self.destroy()

