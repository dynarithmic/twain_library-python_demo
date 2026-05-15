import tkinter as tk
from tkinter import ttk
import ctypes as ct
import tkinter.font as tkfont
import dtwainapi
from tkinter import messagebox
from test_capability_dialog import TestCapabilityDialog

class SourcePropertiesDialog(tk.Toplevel):
    def __init__(self, parent, dtwain_dll=None, source=None):
        super().__init__(parent)

        self.parent = parent
        self.dtwain_dll = dtwain_dll
        self.source = source

        self.title("Source Properties")
        self.geometry("900x430")
        self.resizable(True, True)
        self.transient(parent)

        self.reset_caps_on_close_var = tk.BooleanVar(value=False)

        self._build_ui()
        self.center_over_parent()
        self.deiconify()
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.close_dialog)

        # Get product name
        buf = ct.create_string_buffer(256)
        if self.dtwain_dll.DTWAIN_GetSourceProductNameA(self.source, buf, len(buf)):
            product_name = buf.value.decode("mbcs", errors="replace")
        self.product_name_var.set(product_name)
        self.fill_json_details(product_name)
        self.fill_custom_ds_data()

        buf = ct.create_string_buffer(256)
        dtwain_dll.DTWAIN_GetSourceProductNameA(source, buf, len(buf))
        self.product_name_var.set(buf.value)

        dtwain_dll.DTWAIN_GetSourceManufacturerA(source, buf, len(buf))
        self.manufacturer_var.set(buf.value)

        dtwain_dll.DTWAIN_GetSourceProductFamilyA(source, buf, len(buf))
        self.family_name_var.set(buf.value)

        dtwain_dll.DTWAIN_GetSourceVersionInfoA(source, buf, len(buf))
        self.version_info_var.set(buf.value)

        long_val1 = ct.c_long(0)
        long_val2 = ct.c_long(0)
        dtwain_dll.DTWAIN_GetSourceVersionNumber(source, ct.byref(long_val1), ct.byref(long_val2))
        self.version_var.set(f"{long_val1.value}.{long_val2.value}")

        dtwain_array = ct.c_void_p(0)
        dtwain_array_extendedcaps = ct.c_void_p(0)
        dtwain_array_customcaps = ct.c_void_p(0)
         
        # fill in the capabilities
        dtwain_dll.DTWAIN_EnumSupportedCaps(source, ct.byref(dtwain_array))
        dtwain_dll.DTWAIN_EnumExtendedCaps(source, ct.byref(dtwain_array_extendedcaps)) 
        dtwain_dll.DTWAIN_EnumCustomCaps(source, ct.byref(dtwain_array_customcaps)) 

        arrcount = dtwain_dll.DTWAIN_ArrayGetCount(dtwain_array)
        arrCountExt = dtwain_dll.DTWAIN_ArrayGetCount(dtwain_array_extendedcaps)
        arrCountCustom = dtwain_dll.DTWAIN_ArrayGetCount(dtwain_array_customcaps)

        self.lst_capabilities.delete(0, tk.END)
        self.total_caps_var.set(str(arrcount))
        self.custom_caps_var.set(str(arrCountCustom))
        self.extended_caps_var.set(str(arrCountExt))

        dtwain_dll.DTWAIN_ArrayDestroy(arrCountExt)
        dtwain_dll.DTWAIN_ArrayDestroy(arrCountCustom)

        items = []

        mystrbuf = ct.create_string_buffer(256)

        for i in range(arrcount):
            long_val = ct.c_long(0)

            dtwain_dll.DTWAIN_ArrayGetAtLong(dtwain_array,i,ct.byref(long_val))
            dtwain_dll.DTWAIN_GetNameFromCapA(long_val.value,mystrbuf,len(mystrbuf))
            cap_name = mystrbuf.value.decode("mbcs", errors="replace")
            items.append((cap_name, long_val.value))

        # Sort alphabetically
        items.sort(key=lambda x: x[0].lower())

        # Store for later use (important!)
        self.cap_items = items

        # Populate listbox (name only)
        self.lst_capabilities.delete(0, tk.END)

        for name, _ in items:
            self.lst_capabilities.insert(tk.END, name)

        if self.lst_capabilities.size() > 0:
            self.lst_capabilities.selection_set(0)
            self.lst_capabilities.activate(0)
            self.lst_capabilities.see(0)

        dtwain_dll.DTWAIN_ArrayDestroy(dtwain_array)
        self.wait_window(self)

    def _readonly_entry(self, parent, row, label_text, var):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="e", padx=6, pady=2)
        entry = ttk.Entry(parent, textvariable=var, state="readonly", width=32)
        entry.grid(row=row, column=1, sticky="ew", padx=6, pady=2)
        return entry

    def close_dialog(self):
        if self.reset_caps_on_close_var.get():
            self.reset_all_capabilities(show_message=False)

        self.destroy()

    def center_over_parent(self):
        self.update_idletasks()

        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()

        dlg_w = self.winfo_width()
        dlg_h = self.winfo_height()

        x = parent_x + (parent_w - dlg_w) // 2
        y = parent_y + (parent_h - dlg_h) // 2

        self.geometry(f"+{x}+{y}")

    def fill_custom_ds_data(self):
        if not self.source:
            return

        actual_size = ct.c_ulong(0)   # DWORD

        # First call: get required size
        ok = self.dtwain_dll.DTWAIN_GetCustomDSData(self.source,None,0,ct.byref(actual_size),dtwainapi.DTWAINGCD_COPYDATA)

        if actual_size.value == 0:
            self.txt_ds_data.config(state=tk.NORMAL)
            self.txt_ds_data.delete("1.0", tk.END)
            self.txt_ds_data.insert(tk.END, "<no custom DS data>")
            self.txt_ds_data.config(state=tk.DISABLED)
            self.txt_ds_data.delete("1.0", tk.END)
            return

        # Second call: get data
        BufferType = ct.c_ubyte * actual_size.value
        buf = BufferType()      
        ok = self.dtwain_dll.DTWAIN_GetCustomDSData(self.source,buf,actual_size.value,ct.byref(actual_size),dtwainapi.DTWAINGCD_COPYDATA)

        if not ok:
            self.txt_ds_data.delete("1.0", tk.END)
            self.txt_ds_data.insert(tk.END, "<unable to retrieve custom DS data>")
            return

        data = bytes(buf[:actual_size.value])
        text = data.decode("mbcs", errors="replace")
        self.txt_ds_data.config(state=tk.NORMAL)
        self.txt_ds_data.delete("1.0", tk.END)
        self.txt_ds_data.insert("1.0", text)
        self.txt_ds_data.config(state=tk.DISABLED)
        self.txt_ds_data.delete("1.0", tk.END)

    def fill_json_details(self, product_name):
        if not product_name:
            return

        # product_name must be a normal Python string:
        # "TWAIN2 Software Scanner"
        product_name_ansi = product_name.encode("mbcs")

        num_chars = self.dtwain_dll.DTWAIN_GetSourceDetailsA(product_name_ansi,None,0,2,True)

        if num_chars <= 0:
            self.txt_json_details.delete("1.0", tk.END)
            self.txt_json_details.insert(tk.END, "Unable to retrieve source details.")
            return

        output_buffer = ct.create_string_buffer(num_chars + 1)

        self.dtwain_dll.DTWAIN_GetSourceDetailsA(product_name_ansi,output_buffer,num_chars + 1,2,True)

        json_text = output_buffer.value.decode("mbcs", errors="replace")

        self.txt_json_details.config(state=tk.NORMAL)
        self.txt_json_details.delete("1.0", tk.END)
        self.txt_json_details.insert(tk.END, json_text)
        self.txt_json_details.config(state=tk.DISABLED)

    def _build_ui(self):
        small_font = tkfont.Font(family="Consolas", size=8)  # or size=8
        main = ttk.Frame(self, padding=8)
        main.pack(fill="both", expand=True)

        main.columnconfigure(0, weight=0)
        main.columnconfigure(1, weight=0)
        main.columnconfigure(2, weight=1)
        main.columnconfigure(3, weight=1)
        main.rowconfigure(0, weight=1)

        # ---------------- General Info + Capability Info ----------------

        left = ttk.Frame(main)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        general = ttk.LabelFrame(left, text="General Info", padding=8)
        general.pack(fill="x", pady=(0, 8))
        general.columnconfigure(1, weight=1)

        self.product_name_var = tk.StringVar()
        self.family_name_var = tk.StringVar()
        self.manufacturer_var = tk.StringVar()
        self.version_info_var = tk.StringVar()
        self.version_var = tk.StringVar()

        self._readonly_entry(general, 0, "Product Name:", self.product_name_var)
        self._readonly_entry(general, 1, "Family Name:", self.family_name_var)
        self._readonly_entry(general, 2, "Manufacturer:", self.manufacturer_var)
        self._readonly_entry(general, 3, "Version Info:", self.version_info_var)
        self._readonly_entry(general, 4, "Version:", self.version_var)

        cap_frame = ttk.LabelFrame(left, text="Capability Info", padding=8)
        cap_frame.pack(fill="both", expand=True)

        cap_frame.columnconfigure(0, weight=1)

        # Listbox
        self.lst_capabilities = tk.Listbox(cap_frame,height=9,width=28,exportselection=False)

        self.lst_capabilities.grid(row=0, column=0, rowspan=4, sticky="nsew")

        # Vertical scrollbar (existing)
        yscroll = ttk.Scrollbar(cap_frame, orient="vertical", command=self.lst_capabilities.yview)
        yscroll.grid(row=0, column=1, rowspan=4, sticky="ns")

        # Horizontal scrollbar
        xscroll = ttk.Scrollbar(cap_frame, orient="horizontal", command=self.lst_capabilities.xview)
        xscroll.grid(row=4, column=0, sticky="ew")

        # Attach scrollbars to listbox
        self.lst_capabilities.configure(yscrollcommand=yscroll.set,xscrollcommand=xscroll.set
                                        )
        self.total_caps_var = tk.StringVar(value="0")
        self.custom_caps_var = tk.StringVar(value="0")
        self.extended_caps_var = tk.StringVar(value="0")

        ttk.Label(cap_frame, text="Total Caps:").grid(row=0, column=2, sticky="e", padx=6)
        ttk.Entry(cap_frame, textvariable=self.total_caps_var, state="readonly", width=8).grid(row=0, column=3)

        ttk.Label(cap_frame, text="Custom Caps:").grid(row=1, column=2, sticky="e", padx=6)
        ttk.Entry(cap_frame, textvariable=self.custom_caps_var, state="readonly", width=8).grid(row=1, column=3)

        ttk.Label(cap_frame, text="Extended Caps:").grid(row=2, column=2, sticky="e", padx=6)
        ttk.Entry(cap_frame, textvariable=self.extended_caps_var, state="readonly", width=8).grid(row=2, column=3)

        ttk.Button(cap_frame, text="Test Capability ...",command=self.on_test_capability).grid(row=3, column=2, columnspan=2, sticky="ew", pady=(12, 2))
        ttk.Button(cap_frame,text="Reset All Capabilities",command=self.on_reset_capabilities).grid(row=4, column=2, columnspan=2, sticky="ew", pady=2)

        ttk.Checkbutton(cap_frame,text="Reset Caps On Exit",variable=self.reset_caps_on_close_var).grid(row=5, column=0, sticky="w", pady=(8, 0))

        # ---------------- Custom DS Data ----------------

        ds_frame = ttk.LabelFrame(main, text="Custom DS Data", padding=8)
        ds_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 8))
        ds_frame.rowconfigure(0, weight=1)
        ds_frame.columnconfigure(0, weight=1)

        self.txt_ds_data = tk.Text(ds_frame, width=28, height=18, wrap="none")
        self.txt_ds_data.grid(row=0, column=0, sticky="nsew")

        ds_y = ttk.Scrollbar(ds_frame, orient="vertical", command=self.txt_ds_data.yview)
        ds_y.grid(row=0, column=1, sticky="ns")
        ds_x = ttk.Scrollbar(ds_frame, orient="horizontal", command=self.txt_ds_data.xview)
        ds_x.grid(row=1, column=0, sticky="ew")

        self.txt_ds_data.configure(yscrollcommand=ds_y.set,xscrollcommand=ds_x.set, font=small_font)

        ds_buttons = ttk.Frame(ds_frame)
        ds_buttons.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0))

        ttk.Button(ds_buttons,text="Show UI Only",command=self.on_show_ui_only).pack(side="left", padx=(0, 6))
        ttk.Button(ds_buttons,text="Refresh",command=self.on_refresh_show_ui_only).pack(side="left")

        # ---------------- JSON Details ----------------

        json_frame = ttk.LabelFrame(main, text="JSON Details", padding=8)
        json_frame.grid(row=0, column=2, sticky="nsew")
        json_frame.rowconfigure(0, weight=1)
        json_frame.columnconfigure(0, weight=1)

        self.txt_json_details = tk.Text(json_frame, width=34, height=20, wrap="none", font=small_font)
        self.txt_json_details.grid(row=0, column=0, sticky="nsew")

        json_y = ttk.Scrollbar(json_frame, orient="vertical", command=self.txt_json_details.yview)
        json_y.grid(row=0, column=1, sticky="ns")
        json_x = ttk.Scrollbar(json_frame, orient="horizontal", command=self.txt_json_details.xview)
        json_x.grid(row=1, column=0, sticky="ew")

        self.txt_json_details.configure(yscrollcommand=json_y.set,xscrollcommand=json_x.set)

        # ---------------- Bottom buttons ----------------

        buttons = ttk.Frame(self, padding=(8, 0, 8, 8))
        buttons.pack(fill="x")

        ttk.Button(buttons, text="OK", command=self.on_ok).pack(side="left", padx=(260, 8))
        ttk.Button(buttons, text="Cancel", command=self.on_cancel).pack(side="left")

    def on_test_capability(self):
        selection = self.lst_capabilities.curselection()
        if not selection:
            return

        index = selection[0]
        cap_name, cap_value = self.cap_items[index]

        TestCapabilityDialog(self,self.dtwain_dll,self.source,cap_name)

    def on_reset_capabilities(self):
        self.reset_all_capabilities(show_message=True)

    def on_show_ui_only(self):
        self.dtwain_dll.DTWAIN_ShowUIOnly(self.source)
        self.on_refresh_show_ui_only()

    def on_refresh_show_ui_only(self):
        self.fill_custom_ds_data()

    def on_ok(self):
        self.close_dialog()

    def on_cancel(self):
        self.close_dialog()

    def reset_all_capabilities(self, show_message=True):
        if not self.source:
            return False

        ok = self.dtwain_dll.DTWAIN_SetAllCapsToDefault(self.source)

        if show_message:
            if ok:
                messagebox.showinfo("DTWAIN", "All capabilities reset to default.")
            else:
                messagebox.showerror("DTWAIN", "Unable to reset capabilities.")

        return bool(ok)


