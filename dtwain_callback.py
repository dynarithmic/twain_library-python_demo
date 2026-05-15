from tkinter import messagebox
import dtwainapi
from dib_to_pillow_helper import dib_handle_to_pil_image
from keep_acquired_image_dialog import KeepAcquiredImageDialog
from barcodes_dialog import display_barcode_info, should_show_barcode_info

dtwain_callback_proc = None

def setup_dtwain_callback(root, dtwain_dll, state):
    global dtwain_callback_proc

    @dtwain_dll.SETCALLBACK_TYPE
    def twain_callback(wParam, lParam, userData):
        if wParam == dtwainapi.DTWAIN_TN_ACQUIRESTARTED:
            print("DTWAIN notification: DTWAIN_TN_ACQUIRESTARTED")

        if wParam == dtwainapi.DTWAIN_TN_QUERYPAGEDISCARD:
            if not state.show_preview:
                return 1   # keep image automatically, no dialog

            hdib = dtwain_dll.DTWAIN_GetCurrentAcquiredImage(state.source)

            if not hdib:
                return 1

            pil_img = dib_handle_to_pil_image(hdib)

            dlg = KeepAcquiredImageDialog(root, pil_img)
            return dlg.result

        if wParam == dtwainapi.DTWAIN_TN_TRANSFERDONE:
            show_barcodes = should_show_barcode_info(state.barcode_menu,state.barcode_menu_index,state.barcode_var)

            if show_barcodes:
                display_barcode_info(root, dtwain_dll, state)

            return 1

        if wParam == dtwainapi.DTWAIN_TN_BLANKPAGEDISCARDED1:
            messagebox.showwarning("Blank page alert!","Blank page was discarded")

        if wParam == dtwainapi.DTWAIN_TN_BLANKPAGEDISCARDED2:
            messagebox.showwarning("Blank page alert!","Blank page was discarded")

        return 1
    
    state.dtwain_callback_proc = twain_callback
    dtwain_dll.DTWAIN_EnableMsgNotify(1)
    dtwain_dll.DTWAIN_SetCallback(state.dtwain_callback_proc, 0)

