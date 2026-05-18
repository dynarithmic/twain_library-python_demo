from tkinter import messagebox
import dtwainapi
from dib_to_pillow_helper import dib_handle_to_pil_image
from keep_acquired_image_dialog import KeepAcquiredImageDialog
from barcodes_dialog import display_barcode_info, should_show_barcode_info
from ctypes import *
import ctypes as ct

dtwain_callback_proc = None

def setup_dtwain_callback(root, dtwain_dll, state):
    global dtwain_callback_proc

    @dtwain_dll.SETCALLBACK_TYPE
    def twain_callback(wParam, lParam, userData):

        if wParam == dtwainapi.DTWAIN_TN_ACQUIRESTARTED:
            state.pdf_page_count = 1
            return 1

        if wParam == dtwainapi.DTWAIN_TN_QUERYPAGEDISCARD:
            if not state.show_preview:
                return 1   # keep image automatically, no dialog

            hdib = dtwain_dll.DTWAIN_GetCurrentAcquiredImage(state.source)
            if not hdib:
                return 1

            # convert DIB to PIL image
            pil_img = dib_handle_to_pil_image(hdib)

            dlg = KeepAcquiredImageDialog(root, pil_img)
            return dlg.result # return 1 if image is kept, 0 if image is to be discarded

        if wParam == dtwainapi.DTWAIN_TN_TRANSFERDONE:
            show_barcodes = should_show_barcode_info(state.barcode_menu,state.barcode_menu_index,state.barcode_var)

            if show_barcodes:
                display_barcode_info(root, dtwain_dll, state)

            return 1

        if wParam == dtwainapi.DTWAIN_TN_FILESAVEOK:
            messagebox.showwarning("Image save ok", "File save successful")
            return 1

        if wParam == dtwainapi.DTWAIN_TN_FILEPAGESAVING:
            if (state.current_file_type == dtwainapi.DTWAIN_PDFMULTI
                and state.pdf_text_element):
                # When the PDF page is written, the page number will be seen in the lower left corner of the page.
                text = f"Page {state.pdf_page_count}"
                dtwain_dll.DTWAIN_SetPDFTextElementStringA(state.pdf_text_element,text.encode("utf-8"),dtwainapi.DTWAIN_PDFTEXTELEMENT_TEXT)

                #increment page number for the next page that will be acquired
                state.pdf_page_count += 1
            return 1

        if wParam == dtwainapi.DTWAIN_TN_FILEPAGESAVEERROR or wParam == dtwainapi.DTWAIN_TN_FILESAVEERROR:
            buf = ct.create_unicode_buffer(100)
            last_error = dtwain_dll.DTWAIN_GetLastError();
            last_error_str = dtwain_dll.DTWAIN_GetErrorString(last_error, buf, 100)
            what_error = "page"
            if wParam == dtwainapi.DTWAIN_TN_FILESAVEERROR:
                what_error = "file"
            text = "Error saving image " + what_error + ": " + str(last_error) + buf.value
            messagebox.showwarning("Image save error!", text)
            return 1

        if wParam == dtwainapi.DTWAIN_TN_BLANKPAGEDISCARDED1 or wParam == dtwainapi.DTWAIN_TN_BLANKPAGEDISCARDED2:
            messagebox.showwarning("Blank page alert!","Blank page was discarded")

        return 1
    
    state.dtwain_callback_proc = twain_callback
    dtwain_dll.DTWAIN_EnableMsgNotify(1)
    dtwain_dll.DTWAIN_SetCallback(state.dtwain_callback_proc, 0)

