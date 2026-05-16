import tkinter as tk
from tkinter import ttk
import ctypes as ct
import dtwainapi

class TestCapabilityDialog(tk.Toplevel):
    def __init__(self, parent, dtwain_dll=None, source=None, cap_name=""):
        super().__init__(parent)

        self.parent = parent
        self.dtwain_dll = dtwain_dll
        self.source = source
        self.cap_name = cap_name
        self.cap_value = self.dtwain_dll.DTWAIN_GetCapFromNameA(cap_name.encode("mbcs"))
        self.withdraw()

        self.title(f"Test Capability ({cap_name})")
        self.geometry("600x530")
        self.resizable(False, False)
        self.transient(parent)

        self._build_ui()

        self.update_idletasks()
        self.center_over_parent()

        self.deiconify()
        self.grab_set()
        self.focus_set()
        if self.can_set:
            self.on_set_operation_changed()

    def populate_dropdowns(self):
        get_types = [
            "MSG_GET",
            "MSG_GETCURRENT",
            "MSG_GETDEFAULT",
        ]

        set_types = [
            "MSG_SET",
            "MSG_RESET",
            "MSG_SETCONSTRAINT",
        ]

        container_types = [
            "TW_ARRAY",
            "TW_ENUMERATION",
            "TW_ONEVALUE",
            "TW_RANGE",
        ]

        data_types = [
            "TWTY_INT8",
            "TWTY_INT16",
            "TWTY_INT32",
            "TWTY_UINT8",
            "TWTY_UINT16",
            "TWTY_UINT32",
            "TWTY_BOOL",
            "TWTY_FIX32",
            "TWTY_FRAME",
            "TWTY_STR32",
            "TWTY_STR64",
            "TWTY_STR128",
            "TWTY_STR255",
            "TWTY_STR1024",
            "TWTY_UNI512",
            "TWTY_HANDLE",
        ]

        self.cmb_get_types["values"] = get_types
        self.cmb_set_types["values"] = set_types

        self.cmb_container["values"] = container_types
        self.cmb_container_set["values"] = container_types

        self.cmb_data_type["values"] = data_types
        self.cmb_data_type_set["values"] = data_types

        self.cmb_get_types.current(0)
        self.cmb_set_types.current(0)

        self.cmb_container.current(0)
        self.cmb_container_set.current(0)

        self.cmb_data_type.current(0)
        self.cmb_data_type_set.current(0)

    def center_over_parent(self):
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()

        dlg_w = self.winfo_width()
        dlg_h = self.winfo_height()

        x = parent_x + (parent_w - dlg_w) // 2
        y = parent_y + (parent_h - dlg_h) // 2

        self.geometry(f"+{x}+{y}")

    def select_combobox_text(self, combo, text):
        values = list(combo["values"])
        try:
            combo.current(values.index(text))
        except ValueError:
            # Leave existing selection unchanged if DTWAIN returns something unexpected
            pass

    def set_best_container_for_operation(self, twain_op, combo):
        best_container = self.dtwain_dll.DTWAIN_GetCapContainer(self.source,self.cap_value,twain_op)

        if best_container <= 0:
            return

        buf = ct.create_string_buffer(100)
        self.dtwain_dll.DTWAIN_GetTwainNameFromConstantA(dtwainapi.DTWAIN_CONSTANT_DTWAINCONT_TWAINCONT,best_container,buf,len(buf))

        container_name = buf.value.decode("mbcs", errors="replace")

        self.select_combobox_text(combo, container_name)

    def set_best_data_type(self, combo):
        best_data_type = self.dtwain_dll.DTWAIN_GetCapDataType(self.source,self.cap_value)

        if best_data_type <= 0:
            return

        buf = ct.create_string_buffer(100)
        self.dtwain_dll.DTWAIN_GetTwainNameFromConstantA(dtwainapi.DTWAIN_CONSTANT_TWTY,best_data_type,buf,len(buf))
        data_type_name = buf.value.decode("mbcs", errors="replace")
        self.select_combobox_text(combo, data_type_name)

    def remember_initial_dropdown_state(self):
        self.initial_get_container = self.cmb_container.get()
        self.initial_get_data_type = self.cmb_data_type.get()

        self.initial_set_container = self.cmb_container_set.get()
        self.initial_set_data_type = self.cmb_data_type_set.get()

    def _build_ui(self):
        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        ttk.Label(main,text="Note: Testing using non-default container or data type may have undesirable results.").grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 12))

        # ---------------- GET section ----------------

        ttk.Label(main, text="Get Operation:").grid(row=1, column=0, sticky="w")
        ttk.Label(main, text="Container:").grid(row=1, column=1, sticky="w")
        ttk.Label(main, text="Data Type:").grid(row=1, column=2, sticky="w")

        self.cmb_get_types = ttk.Combobox(main, state="readonly", width=18)
        self.cmb_get_types.grid(row=2, column=0, sticky="w", padx=(0, 8))
        self.cmb_get_types.bind("<<ComboboxSelected>>", self.on_get_operation_changed)

        self.cmb_container = ttk.Combobox(main, state="readonly", width=24)
        self.cmb_container.grid(row=2, column=1, sticky="w", padx=(0, 8))

        self.cmb_data_type = ttk.Combobox(main, state="readonly", width=16)
        self.cmb_data_type.grid(row=2, column=2, sticky="w", padx=(0, 8))

        ttk.Button(main, text="Test", command=self.on_test_get).grid(row=3, column=1, sticky="w", pady=8)
        ttk.Button(main, text="Revert", command=self.on_revert_get).grid(row=2, column=4, sticky="w")

        self.get_status_var = tk.StringVar(value="")
        self.static_test_get_results = ttk.Label(main,textvariable=self.get_status_var)
        self.static_test_get_results.grid(row=3, column=2, sticky="w")

        ttk.Label(main, text="Results:").grid(row=4, column=0, sticky="w")

        self.lst_results = tk.Listbox(main, height=5, width=72, exportselection=False)
        self.lst_results.grid(row=5, column=0, columnspan=5, sticky="ew", pady=(0, 12))

        results_y = ttk.Scrollbar(main, orient="vertical", command=self.lst_results.yview)
        results_y.grid(row=5, column=5, sticky="ns")
        self.lst_results.configure(yscrollcommand=results_y.set)

        ttk.Separator(main, orient="horizontal").grid(
            row=6, column=0, columnspan=6, sticky="ew", pady=12
        )

        # ---------------- SET section ----------------

        self.lbl_set_operation = ttk.Label(main, text="Set Operation:")
        self.lbl_set_operation.grid(row=7, column=0, sticky="w")

        self.lbl_container_set = ttk.Label(main, text="Container:")
        self.lbl_container_set.grid(row=7, column=1, sticky="w")

        self.lbl_data_type_set = ttk.Label(main, text="Data Type:")
        self.lbl_data_type_set.grid(row=7, column=2, sticky="w")

        self.cmb_set_types = ttk.Combobox(main, state="readonly", width=18)
        self.cmb_set_types.grid(row=8, column=0, sticky="w", padx=(0, 8))
        self.cmb_set_types.bind("<<ComboboxSelected>>", self.on_set_operation_changed)

        self.cmb_container_set = ttk.Combobox(main, state="readonly", width=24)
        self.cmb_container_set.grid(row=8, column=1, sticky="w", padx=(0, 8))

        self.cmb_data_type_set = ttk.Combobox(main, state="readonly", width=16)
        self.cmb_data_type_set.grid(row=8, column=2, sticky="w", padx=(0, 8))

        self.btn_test_set = ttk.Button(main, text="Test", command=self.on_test_set)
        self.btn_test_set.grid(row=9, column=1, sticky="w", pady=8)

        self.btn_revert_set = ttk.Button(main, text="Revert", command=self.on_revert_set)
        self.btn_revert_set.grid(row=8, column=4, sticky="w")

        self.lbl_input_set = ttk.Label(main, text="Input: (One data item per line):")
        self.lbl_input_set.grid(row=10, column=0, sticky="w")

        self.lbl_results_set = ttk.Label(main, text="Results:")
        self.lbl_results_set.grid(row=10, column=2, sticky="w")

        self.ed_set_input = tk.Text(main, width=32, height=5, wrap="none")
        self.ed_set_input.grid(row=11, column=0, columnspan=2, sticky="nsew", padx=(0, 12))

        input_y = ttk.Scrollbar(main, orient="vertical", command=self.ed_set_input.yview)
        input_y.grid(row=11, column=1, sticky="nse")
        self.ed_set_input.configure(yscrollcommand=input_y.set)

        self.lst_results_set = tk.Listbox(main, height=5, width=36, exportselection=False)
        self.lst_results_set.grid(row=11, column=2, columnspan=3, sticky="nsew")

        set_y = ttk.Scrollbar(main, orient="vertical", command=self.lst_results_set.yview)
        set_y.grid(row=11, column=5, sticky="ns")

        set_x = ttk.Scrollbar(main, orient="horizontal", command=self.lst_results_set.xview)
        set_x.grid(row=12, column=2, columnspan=3, sticky="ew")

        self.lst_results_set.configure(yscrollcommand=set_y.set,xscrollcommand=set_x.set)

        # ---------------- Bottom buttons ----------------

        buttons = ttk.Frame(main)
        buttons.grid(row=13, column=0, columnspan=6, pady=(18, 0))

        ttk.Button(buttons, text="OK", command=self.destroy).pack(side="left", padx=6)
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="left", padx=6)

        self.populate_dropdowns()

        self.set_best_container_for_operation(dtwainapi.DTWAIN_CAPGET,self.cmb_container)
        self.set_best_container_for_operation(dtwainapi.DTWAIN_CAPSET,self.cmb_container_set)
        self.set_best_data_type(self.cmb_data_type)
        self.set_best_data_type(self.cmb_data_type_set)
        self.update_set_section_state_from_capability()
        self.remember_initial_dropdown_state()

    def on_get_operation_changed(self, event=None):
        get_op_name = self.cmb_get_types.get()
        get_op = self.dtwain_dll.DTWAIN_GetConstantFromTwainNameA(get_op_name.encode("mbcs"))
        self.set_best_container_for_operation(get_op,self.cmb_container)

    def on_revert_get(self):
        self.select_combobox_text(self.cmb_container, self.initial_get_container)
        self.select_combobox_text(self.cmb_data_type, self.initial_get_data_type)


    def on_revert_set(self):
        self.select_combobox_text(self.cmb_container_set, self.initial_set_container)
        self.select_combobox_text(self.cmb_data_type_set, self.initial_set_data_type)

    def set_set_section_enabled(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED

        widgets = [
            self.lbl_set_operation,
            self.lbl_container_set,
            self.lbl_data_type_set,
            self.lbl_input_set,
            self.lbl_results_set,
            self.cmb_set_types,
            self.cmb_container_set,
            self.cmb_data_type_set,
            self.btn_test_set,
            self.btn_revert_set,
            self.ed_set_input,
            self.lst_results_set,
        ]

        for widget in widgets:
            widget.configure(state=state)

    def update_set_section_state_from_capability(self):
        cap_opts = ct.c_long(0)

        ok = self.dtwain_dll.DTWAIN_GetCapOperations(self.source,self.cap_value,ct.byref(cap_opts))

        if not ok:
            self.set_set_section_enabled(False)
            return

        self.can_set = (cap_opts.value & dtwainapi.DTWAIN_CO_SET) != 0
        self.set_set_section_enabled(self.can_set)

    def on_test_get(self):
        self.lst_results.delete(0, tk.END)
        self.get_status_var.set("")  # clear

        get_type = self.get_selected_get_operation_constant()
        container_type = self.get_selected_container_constant()
        data_type = self.get_selected_data_type_constant()

        cap_values = self.dtwain_dll.DTWAIN_ArrayGetCapValuesEx2(self.source,self.cap_value,get_type,container_type,data_type)

        if not cap_values:
            self.get_status_var.set("Error")
            self.lst_results.insert(tk.END, "<unable to retrieve capability values>")
            return

        try:
            count = self.dtwain_dll.DTWAIN_ArrayGetCount(cap_values)

            if count <= 0:
                self.get_status_var.set("Error")
                self.lst_results.insert(tk.END, "<no values returned>")
                return

            success_count = 0
            raw_values = []

            for i in range(count):
                ok, value = self.read_cap_array_value(cap_values, i)

                if ok:
                    raw_values.append(value)
                    success_count += 1
                else:
                    raw_values.append(None)

            if success_count > 0:
                self.get_status_var.set("Success")
            else:
                self.get_status_var.set("Error")                    

            self.lst_results.delete(0, tk.END)

            if self.cmb_container.get() == "TW_RANGE":
                labels = ["Minimum", "Maximum", "Step", "Current", "Default"]

                for label, value in zip(labels, raw_values):
                    if value is None:
                        display_value = "<unable to read>"
                    else:
                        display_value = self.format_get_result_value(value)

                    self.lst_results.insert(tk.END, f"{label}: {display_value}")

            else:
                results = []

                for i, value in enumerate(raw_values):
                    if value is None:
                        results.append(f"<unable to read item {i}>")
                    else:
                        results.append(self.format_get_result_value(value))

                results.sort(key=lambda x: x.lower())

                for item in results:
                    self.lst_results.insert(tk.END, item)

        finally:
            self.dtwain_dll.DTWAIN_ArrayDestroy(cap_values)    

    def on_test_set(self):
        self.lst_results_set.delete(0, tk.END)

        msg_set = self.dtwain_dll.DTWAIN_GetConstantFromTwainNameA(self.cmb_set_types.get().encode("mbcs"))

        if self.cmb_set_types.get() == "MSG_RESET":
            ok = self.dtwain_dll.DTWAIN_SetCapValuesEx2(self.source,self.cap_value,msg_set,0,0,None)
            self.lst_results_set.insert(tk.END, "Success" if ok else "Error")
            return

        container_type = self.dtwain_dll.DTWAIN_GetConstantFromTwainNameA(self.cmb_container_set.get().encode("mbcs"))
        data_type = self.dtwain_dll.DTWAIN_GetConstantFromTwainNameA(self.cmb_data_type_set.get().encode("mbcs"))

        data_type_name = self.cmb_data_type_set.get()

        string_types = {
            "TWTY_STR32",
            "TWTY_STR64",
            "TWTY_STR128",
            "TWTY_STR255",
            "TWTY_STR1024",
            "TWTY_UNI512",
        }

        if data_type_name == "TWTY_FIX32":
            values = self.parse_float_input_values()
            arr = self.create_float_array_from_values(values)

        elif data_type_name == "TWTY_FRAME":
            values = self.parse_frame_input_values()
            arr = self.create_frame_array_from_values(values)

        elif data_type_name in string_types:
            values = self.parse_string_input_values()
            arr = self.create_string_array_from_values(values)

        else:
            values = self.parse_integer_input_values()
            arr = self.create_long_array_from_values(values)

        if not values:
            self.lst_results_set.insert(tk.END, "<no input values>")
            return

        if not arr:
            self.lst_results_set.insert(tk.END, "<unable to create DTWAIN_ARRAY>")
            return

        try:
            ok = self.dtwain_dll.DTWAIN_SetCapValuesEx2(self.source,self.cap_value,msg_set,container_type, data_type, arr)

            if ok:
                self.lst_results_set.insert(tk.END, "Success")
            else:
                self.lst_results_set.insert(tk.END, "Error")

        finally:
            self.dtwain_dll.DTWAIN_ArrayDestroy(arr)

    def twain_constant_from_name(self, name):
        return self.dtwain_dll.DTWAIN_GetConstantFromTwainNameA(name.encode("mbcs"))

    def get_selected_get_operation_constant(self):
        return self.twain_constant_from_name(self.cmb_get_types.get())

    def get_selected_container_constant(self):
        return self.twain_constant_from_name(self.cmb_container.get())

    def get_selected_data_type_constant(self):
        return self.twain_constant_from_name(self.cmb_data_type.get())


    def get_cap_value_translation_id(self):
        cap_value = self.cap_value

        # If this succeeds, DTWAIN says the cap values do NOT need mnemonic translation
        rc = self.dtwain_dll.DTWAIN_GetTwainNameFromConstantA(dtwainapi.DTWAIN_CONSTANT_CAPCODE_NOMNEMONIC,cap_value,None,0)

        if rc != dtwainapi.DTWAIN_FAILURE1:
            return None

        buf = ct.create_string_buffer(100)

        got_id = self.dtwain_dll.DTWAIN_GetTwainNameFromConstantA(dtwainapi.DTWAIN_CONSTANT_CAPCODE_MAP,cap_value,buf,len(buf))

        if not got_id:
            return None

        try:
            translation_id = int(buf.value.decode("mbcs", errors="replace"))
        except ValueError:
            return None

        if translation_id == cap_value:
            return None

        return translation_id

    def format_mapped_twain_constant(self, value):
        translation_id = self.get_cap_value_translation_id()

        if translation_id is None:
            return None

        buf = ct.create_string_buffer(256)

        self.dtwain_dll.DTWAIN_GetTwainNameFromConstantExA(translation_id,value,buf,len(buf))

        text = buf.value.decode("mbcs", errors="replace")

        data_type_name = self.cmb_data_type.get()

        if data_type_name in ("TWTY_INT16", "TWTY_INT32"):
            numeric_text = str(ct.c_long(value).value)
        else:
            numeric_text = str(ct.c_ulong(value).value)

        # DTWAIN returns the number as text if no mnemonic exists
        if text == numeric_text:
            return None

        return text


    def format_get_result_value(self, value):
        if isinstance(value, tuple) and len(value) == 4:
            left, top, right, bottom = value
            return (
                f"Left: {left:.5f}   "
                f"Top: {top:.5f}   "
                f"Right: {right:.5f}   "
                f"Bottom: {bottom:.5f}"
            )

        if isinstance(value, str):
            return value

        if isinstance(value, float):
            return f"{value:.5f}"

        if self.cmb_data_type.get() == "TWTY_BOOL":
            return "TRUE" if value else "FALSE"

        if self.cap_name in ("CAP_SUPPORTEDCAPS","CAP_EXTENDEDCAPS","CAP_SUPPORTEDCAPSSEGMENTUNIQUE"):
            buf = ct.create_string_buffer(256)

            ok = self.dtwain_dll.DTWAIN_GetNameFromCapA(value,buf,len(buf))

            if ok:
                return buf.value.decode("mbcs", errors="replace")

        if self.cap_name == "CAP_SUPPORTEDDATS":
            hi_word = (value >> 16) & 0xFFFF
            lo_word = value & 0xFFFF

            hi_buf = ct.create_string_buffer(100)
            lo_buf = ct.create_string_buffer(100)

            self.dtwain_dll.DTWAIN_GetTwainNameFromConstantExA(dtwainapi.DTWAIN_CONSTANT_DG,hi_word,hi_buf,len(hi_buf))
            self.dtwain_dll.DTWAIN_GetTwainNameFromConstantExA(dtwainapi.DTWAIN_CONSTANT_DAT,lo_word,lo_buf,len(lo_buf))

            return (
                hi_buf.value.decode("mbcs", errors="replace")
                + " / "
                + lo_buf.value.decode("mbcs", errors="replace")
            )

        mapped_name = self.format_mapped_twain_constant(value)
        if mapped_name:
            return mapped_name

        return str(value)

    def read_cap_array_value(self, cap_values, index):
        array_type = self.dtwain_dll.DTWAIN_ArrayGetType(cap_values)

        if array_type == dtwainapi.DTWAIN_ARRAYFLOAT:
            dval = ct.c_double(0.0)
            ok = self.dtwain_dll.DTWAIN_ArrayGetAtFloat(cap_values, index, ct.byref(dval))
            return ok, dval.value

        elif array_type == dtwainapi.DTWAIN_ARRAYANSISTRING:
            buf = ct.create_string_buffer(256)
            ok = self.dtwain_dll.DTWAIN_ArrayGetAtANSIString(cap_values, index, buf)
            return ok, buf.value.decode("mbcs", errors="replace") if ok else None

        elif array_type == dtwainapi.DTWAIN_ARRAYFRAME:
            left = ct.c_double(0.0)
            top = ct.c_double(0.0)
            right = ct.c_double(0.0)
            bottom = ct.c_double(0.0)

            ok = self.dtwain_dll.DTWAIN_ArrayGetAtFrame(cap_values,index,ct.byref(left),ct.byref(top),ct.byref(right),ct.byref(bottom))

            if ok:
                return True, (left.value, top.value, right.value, bottom.value)

            return False, None

        else:
            lval = ct.c_long(0)
            ok = self.dtwain_dll.DTWAIN_ArrayGetAtLong(cap_values, index, ct.byref(lval))
            return ok, lval.value

##########  Here are the SET operations
    def parse_integer_input_values(self):
        text = self.ed_set_input.get("1.0", tk.END)

        values = []
        INT_MIN = -2147483648

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue

            upper = line.upper()

            is_bool = (self.cmb_data_type_set.get() == "TWTY_BOOL")

            if is_bool:
                if upper == "TRUE":
                    values.append(1)
                    continue
                elif upper == "FALSE":
                    values.append(0)
                    continue

            try:
                values.append(int(line, 0))
                continue
            except ValueError:
                pass

            const_val = self.dtwain_dll.DTWAIN_GetConstantFromTwainNameA(upper.encode("mbcs"))

            if const_val != INT_MIN:
                values.append(const_val)
            else:
                values.append(0)

        return values

    def create_long_array_from_values(self, values):
        arr = self.dtwain_dll.DTWAIN_ArrayCreate(dtwainapi.DTWAIN_ARRAYLONG,len(values))

        if not arr:
            return None

        for i, val in enumerate(values):
            self.dtwain_dll.DTWAIN_ArraySetAtLong(arr,i,ct.c_long(val))

        return arr

    def parse_float_input_values(self):
        text = self.ed_set_input.get("1.0", tk.END)

        values = []

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue

            try:
                values.append(float(line))
            except ValueError:
                values.append(0.0)

        return values

    def create_float_array_from_values(self, values):
        arr = self.dtwain_dll.DTWAIN_ArrayCreate(dtwainapi.DTWAIN_ARRAYFLOAT,0)

        if not arr:
            return None

        for val in values:
            self.dtwain_dll.DTWAIN_ArrayAddFloat(arr,ct.c_double(val))

        return arr

    def parse_string_input_values(self):
        text = self.ed_set_input.get("1.0", tk.END)

        values = []

        for line in text.splitlines():
            # Keep internal spaces, remove only line-ending whitespace
            value = line.rstrip("\r\n")

            # Optional: skip blank lines
            if value == "":
                continue

            values.append(value)

        return values

    def create_string_array_from_values(self, values):
        arr = self.dtwain_dll.DTWAIN_ArrayCreate(dtwainapi.DTWAIN_ARRAYANSISTRING,0)

        if not arr:
            return None

        for value in values:
            self.dtwain_dll.DTWAIN_ArrayAddANSIString(arr,value.encode("mbcs"))

        return arr

    def parse_frame_input_values(self):
        text = self.ed_set_input.get("1.0", tk.END)

        frames = []

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            parts = line.replace(",", " ").split()

            try:
                left = float(parts[0])
                top = float(parts[1])
                right = float(parts[2])
                bottom = float(parts[3])
            except (IndexError, ValueError):
                left = top = right = bottom = 0.0

            frames.append((left, top, right, bottom))

        return frames

    def create_frame_array_from_values(self, frames):
        array_frame = self.dtwain_dll.DTWAIN_ArrayCreate(dtwainapi.DTWAIN_ARRAYFRAME,0)

        if not array_frame:
            return None

        frame = self.dtwain_dll.DTWAIN_FrameCreate(ct.c_double(0.0),ct.c_double(0.0),ct.c_double(0.0),ct.c_double(0.0))

        if not frame:
            self.dtwain_dll.DTWAIN_ArrayDestroy(array_frame)
            return None

        try:
            for left, top, right, bottom in frames:
                self.dtwain_dll.DTWAIN_FrameSetAll(frame,ct.c_double(left),ct.c_double(top),ct.c_double(right),ct.c_double(bottom))

                self.dtwain_dll.DTWAIN_ArrayAddFrame(array_frame,frame)

        finally:
            self.dtwain_dll.DTWAIN_FrameDestroy(frame)

        return array_frame

    def on_set_operation_changed(self, event=None):
        is_reset = self.cmb_set_types.get() == "MSG_RESET"

        state = tk.DISABLED if is_reset else tk.NORMAL

        widgets = [
            self.lbl_container_set,
            self.lbl_data_type_set,
            self.lbl_input_set,
            self.lbl_results_set,
            self.cmb_container_set,
            self.cmb_data_type_set,
            self.ed_set_input,
            self.lst_results_set,
            self.btn_revert_set,
        ]

        for widget in widgets:
            widget.configure(state=state)

        self.cmb_set_types.configure(state="readonly")
        self.btn_test_set.configure(state=tk.NORMAL)

