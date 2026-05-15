from tkinter import messagebox
from enter_custom_language_dialog import EnterCustomLanguageDialog
from app_constants import LANGUAGE_RESOURCE_NAMES

def load_language_resource(root, dtwain_dll, command_id):
    resource_name = LANGUAGE_RESOURCE_NAMES.get(command_id)

    if not resource_name:
        messagebox.showwarning("DTWAIN", f"No language mapping for {command_id}")
        return

    ok = dtwain_dll.DTWAIN_LoadCustomStringResourcesA(resource_name.encode("mbcs"))

    if ok:
        messagebox.showinfo("DTWAIN",f"Loaded language resource: {resource_name}")
    else:
        messagebox.showerror("DTWAIN",f"Unable to load language resource: {resource_name}")

def load_custom_language_resource(root, dtwain_dll):
    dlg = EnterCustomLanguageDialog(root)

    if not dlg.result:
        return

    language_name = dlg.result

    ok = dtwain_dll.DTWAIN_LoadCustomStringResourcesA(language_name.encode("mbcs"))

    if ok:
        messagebox.showinfo("DTWAIN",f"Loaded custom language resource:\n{language_name}")
    else:
        messagebox.showerror("DTWAIN",f"Unable to load custom language resource:\n{language_name}")

