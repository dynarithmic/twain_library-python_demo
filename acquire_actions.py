import dtwainapi
from tkinter import messagebox
from acquired_images_dialog import AcquiredImagesDialog
from enter_file_name_dialog import EnterFileNameDialog
from app_constants import ACQUIRE_FILE_TYPES, ACQUIRE_FILE_SOURCE_FORMATS
from menu_state import apply_message_loop_setting

def acquire_native_test(root, dtwain_dll, state):
    acquire_test(root,dtwain_dll,state,dtwain_dll.DTWAIN_AcquireNative,"Acquire Native")

def acquire_buffered_test(root, dtwain_dll, state):
    acquire_test(root,dtwain_dll,state,dtwain_dll.DTWAIN_AcquireBuffered,"Acquire Buffered")

def acquire_test(root, dtwain_dll, state, acquire_func, acquire_name):
    if not state.source:
        messagebox.showwarning("DTWAIN", "No TWAIN source selected.")
        return

    show_ui = 1 if state.use_source_ui else 0

    apply_message_loop_setting(dtwain_dll, state)
    acquisitions = acquire_func(state.source,dtwainapi.DTWAIN_PT_DEFAULT,dtwainapi.DTWAIN_MAXACQUIRE,show_ui,1,None)

    if not acquisitions:
        messagebox.showwarning("DTWAIN", f"{acquire_name} returned no acquisitions.")
        return
    try:
        AcquiredImagesDialog(root, dtwain_dll, acquisitions)
    finally:
        dtwain_dll.DTWAIN_DestroyAcquisitionArray(acquisitions, 1)

def create_filename_array(dtwain_dll, filename):
    arr = dtwain_dll.DTWAIN_ArrayCreate(dtwainapi.DTWAIN_ARRAYANSISTRING,0)

    if not arr:
        return None

    ok = dtwain_dll.DTWAIN_ArrayAddANSIString(arr,filename.encode("mbcs"))

    if not ok:
        dtwain_dll.DTWAIN_ArrayDestroy(arr)
        return None

    return arr


def acquire_file_common(root, dtwain_dll, state, command_id, file_type_map, fileflags, title):
    if not state.source:
        messagebox.showwarning("DTWAIN", "No TWAIN source selected.")
        return

    file_type = file_type_map.get(command_id)

    if file_type is None:
        messagebox.showerror("DTWAIN", f"No file type mapping for:\n{command_id}")
        return

    dlg = EnterFileNameDialog(root)
    if not dlg.result:
        return

    filename_array = create_filename_array(dtwain_dll, dlg.result)

    if not filename_array:
        messagebox.showerror("DTWAIN", "Unable to create filename array.")
        return

    apply_message_loop_setting(dtwain_dll, state)

    try:
        ok = dtwain_dll.DTWAIN_AcquireFileEx(state.source,filename_array,file_type,fileflags,
                                             dtwainapi.DTWAIN_PT_DEFAULT,dtwainapi.DTWAIN_MAXACQUIRE,1,1,None)

        if ok:
            messagebox.showinfo("DTWAIN", f"{title} completed.")
        else:
            messagebox.showerror("DTWAIN", f"{title} failed.")

    finally:
        dtwain_dll.DTWAIN_ArrayDestroy(filename_array)

def acquire_file_test(root, dtwain_dll, state, command_id):
    fileflags = (dtwainapi.DTWAIN_USENATIVE |dtwainapi.DTWAIN_CREATE_DIRECTORY | dtwainapi.DTWAIN_USELONGNAME)
    acquire_file_common(root,dtwain_dll,state,command_id,ACQUIRE_FILE_TYPES,fileflags,"Acquire file")

def acquire_file_source_mode_test(root, dtwain_dll, state, command_id):
    fileflags = (dtwainapi.DTWAIN_USESOURCEMODE |dtwainapi.DTWAIN_CREATE_DIRECTORY | dtwainapi.DTWAIN_USELONGNAME)
    acquire_file_common(root,dtwain_dll,state,command_id,ACQUIRE_FILE_SOURCE_FORMATS,fileflags,"Source-mode acquire file")

