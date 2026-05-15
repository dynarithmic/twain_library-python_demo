import tkinter as tk
from ctypes import *
import ctypes as ct
from tkinter import ttk

class SelectSourceCustomDialog(tk.Toplevel):
    def __init__(self, parent, dtwain_dll):
        super().__init__(parent)

        self.parent = parent
        self.dtwain_dll = dtwain_dll
        self.result = None

        self.withdraw()
        self.title("Custom Select Source Dialog")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self.populate_sources()

        self.update_idletasks()
        self.center_over_parent()
        self.deiconify()

        self.lst_sources.focus_set()
        self.wait_window(self)

    def _build_ui(self):
        main = ttk.Frame(self, padding=8)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Sorted Source Names:").grid(row=0, column=0, sticky="w")

        self.lst_sources = tk.Listbox(main,width=38,height=8,exportselection=False)
        self.lst_sources.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=(0, 8))

        yscroll = ttk.Scrollbar(main, orient="vertical", command=self.lst_sources.yview)
        yscroll.grid(row=1, column=1, rowspan=2, sticky="ns", padx=(0, 8))
        self.lst_sources.configure(yscrollcommand=yscroll.set)

        ttk.Button(main, text="Select", command=self.on_select).grid(row=1, column=2, sticky="ew", pady=(0, 4))

        ttk.Button(main, text="Cancel", command=self.on_cancel).grid(row=2, column=2, sticky="ew")

        self.num_sources_var = tk.StringVar(value="0")
        self.bottom_text_var = tk.StringVar(value="There are 0 TWAIN Source(s) Available for Selection")
        ttk.Label(main, textvariable=self.bottom_text_var).grid(row=3, column=0, sticky="w", padx=(42, 0), pady=(8, 0))

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.lst_sources.bind("<Double-Button-1>", lambda e: self.on_select())
        self.lst_sources.bind("<Return>", lambda e: self.on_select())
        self.lst_sources.bind("<Escape>", lambda e: self.on_cancel())

    def populate_sources(self):
        self.lst_sources.delete(0, tk.END)

        source_list = self.dtwain_dll.DTWAIN_EnumSourcesEx()

        if not source_list:
            self.num_sources_var.set("0")
            self.bottom_text_var.set("There are 0 TWAIN Source(s) Available for Selection")
            return

        names = []

        try:
            count = self.dtwain_dll.DTWAIN_ArrayGetCount(source_list)

            for i in range(count):
                cur_source = self.dtwain_dll.DTWAIN_ArrayGetAtSourceEx(source_list,i)

                if cur_source:
                    buf = ct.create_string_buffer(256)
                    ok = self.dtwain_dll.DTWAIN_GetSourceProductNameA(cur_source,buf,len(buf))

                    if ok:
                        name = buf.value.decode("mbcs", errors="replace")
                        names.append(name)

        finally:
            self.dtwain_dll.DTWAIN_ArrayDestroy(source_list)

        names.sort(key=lambda s: s.lower())

        for name in names:
            self.lst_sources.insert(tk.END, name)

        total = len(names)
        self.num_sources_var.set(str(total))
        self.bottom_text_var.set(f"There are {total} TWAIN Source(s) Available for Selection")

        if total > 0:
            self.lst_sources.selection_set(0)
            self.lst_sources.activate(0)
            self.lst_sources.see(0)

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

    def on_select(self):
        sel = self.lst_sources.curselection()
        if not sel:
            self.result = None
        else:
            self.result = self.lst_sources.get(sel[0])

        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

