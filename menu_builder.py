import tkinter as tk
from source_actions import select_source_common, close_current_source, SourceSelectMode
from about_dialog import AboutDialog
from source_properties_dialog import SourcePropertiesDialog
from menu_state import on_discard_blank_pages_changed, update_source_menu_state, update_source_mode_file_menu_state, update_application_menu_state
from acquire_actions import acquire_buffered_test, acquire_native_test, acquire_file_test, acquire_file_source_mode_test
from language_resource import load_language_resource, load_custom_language_resource
from logging_options_dialog import show_logging_options

def stub(command_id):
    def handler():
        print(f"Menu command: {command_id}")
    return handler

def add_source_required_item(state, menu):
    state.source_required_menu_items.append((menu, menu.index("end")))

def build_dtwdemo_menu(root, dtwain_dll, twain_state):
    menubar = tk.Menu(root)

    # Source Selection Test
    source_menu = tk.Menu(menubar, tearoff=False)
    source_menu.add_command(label="Select Source...",
                            command=lambda: select_source_common(root, dtwain_dll, twain_state, SourceSelectMode.DIALOG))

    source_menu.add_command(label="Select Source By Name...",
                            command=lambda: select_source_common(root, dtwain_dll, twain_state, SourceSelectMode.BY_NAME))

    source_menu.add_command(label="Select Default Source...",
                            command=lambda: select_source_common(root, dtwain_dll, twain_state, SourceSelectMode.DEFAULT))

    source_menu.add_command(label="Select Source Custom...", 
                            command=lambda: select_source_common(root, dtwain_dll, twain_state, SourceSelectMode.CUSTOM))    

    source_menu.add_separator()
    source_menu.add_command(label="Source Properties...",
        command=lambda: SourcePropertiesDialog(root, dtwain_dll, twain_state.source),state=tk.DISABLED)
    add_source_required_item(twain_state, source_menu)    
    source_props_index = source_menu.index("end")

    source_menu.add_separator()

    source_menu.add_command(label="Close Source...",command=lambda: close_current_source(root, dtwain_dll, twain_state),state=tk.DISABLED)
    add_source_required_item(twain_state, source_menu)    
    close_source_index = source_menu.index("end")

    source_menu.add_separator()
    source_menu.add_command(label="Exit Demo", command=root.destroy)
    menubar.add_cascade(label="Source Selection Test", menu=source_menu)

    twain_state.source_menu = source_menu
    twain_state.source_props_index = source_props_index
    twain_state.close_source_index = close_source_index

    # Acquire Test
    acquire_menu = tk.Menu(menubar, tearoff=False)
    acquire_menu.add_command(label="Acquire Native...",command=lambda: acquire_native_test(root, dtwain_dll, twain_state),state=tk.DISABLED)
    add_source_required_item(twain_state, acquire_menu)

    acquire_menu.add_command(label="Acquire Buffered...",command=lambda: acquire_buffered_test(root, dtwain_dll, twain_state),state=tk.DISABLED)
    add_source_required_item(twain_state, acquire_menu)    
    acquire_file = tk.Menu(acquire_menu, tearoff=False)

    bigtiff = tk.Menu(acquire_file, tearoff=False)
    for label, cmd in [
        ("No compression", "IDM_ACQUIREFILE_BIGTIFF_NOCOMPRESSION"),
        ("Group 3", "IDM_ACQUIREFILE_BIGTIFF_GROUP3"),
        ("Group 4", "IDM_ACQUIREFILE_BIGTIFF_GROUP4"),
        ("Flate", "IDM_ACQUIREFILE_BIGTIFF_FLATE"),
        ("JPEG", "IDM_ACQUIREFILE_BIGTIFF_JPEG"),
        ("LZW", "IDM_ACQUIREFILE_BIGTIFF_LZW"),
        ("Packbits", "IDM_ACQUIREFILE_BIGTIFF_PACKBITS"),
    ]:
        bigtiff.add_command(label=label,command=lambda c=cmd: acquire_file_test(root, dtwain_dll, twain_state, c))

    acquire_file.add_cascade(label="BigTIFF", menu=bigtiff)

    for label, cmd in [
        ("BMP", "IDM_ACQUIREFILE_BMP"),
        ("BMP-RLE", "IDM_ACQUIREFILE_BMPRLE"),
        ("DCX", "IDM_ACQUIREFILE_DCX"),
        ("Enhanced Meta File (EMF)", "IDM_ACQUIREFILE_ENHANCEDMETAFILE"),
        ("GIF", "IDM_ACQUIREFILE_GIF"),
        ("ICO", "IDM_ACQUIREFILE_ICO"),
        ("ICO-Vista", "IDM_ACQUIREFILE_ICOVISTA"),
        ("JPEG", "IDM_ACQUIREFILE_JPEG"),
        ("JPEG-2000", "IDM_ACQUIREFILE_JPEG2000"),
        ("JPEG-XR", "IDM_ACQUIREFILE_JPEGXR"),
        ("Paintshop (PSD)", "IDM_ACQUIREFILE_PAINTSHOP"),
        ("PCX", "IDM_ACQUIREFILE_PCX"),
        ("PDF", "IDM_ACQUIREFILE_PDF"),
        ("PNG", "IDM_ACQUIREFILE_PNG"),
        ("PostScript (Level 1)", "IDM_ACQUIREFILE_POSTSCRIPTLEVEL1"),
        ("PostScript (Level 2)", "IDM_ACQUIREFILE_POSTSCRIPTLEVEL2"),
        ("PostScript (Level 3)", "IDM_ACQUIREFILE_POSTSCRIPTLEVEL3"),
        ("SVG", "IDM_ACQUIREFILE_SVG"),
        ("SVGZ", "IDM_ACQUIREFILE_SVGZ"),
        ("Targa (TGA)", "IDM_ACQUIREFILE_TGA"),
        ("Targa-RLE", "IDM_ACQUIREFILE_TGARLE"),
        ("Text (OCR)", "IDM_ACQUIREFILE_TEXT"),
    ]:
        acquire_file.add_command(label=label,command=lambda c=cmd: acquire_file_test(root, dtwain_dll, twain_state, c)) 

    tiff = tk.Menu(acquire_file, tearoff=False)
    for label, cmd in [
        ("No compression", "IDM_ACQUIREFILE_TIFF_NOCOMPRESSION"),
        ("Group 3", "IDM_ACQUIREFILE_TIFF_GROUP3"),
        ("Group 4", "IDM_ACQUIREFILE_TIFF_GROUP4"),
        ("Flate", "IDM_ACQUIREFILE_TIFF_FLATE"),
        ("JPEG", "IDM_ACQUIREFILE_TIFF_JPEG"),
        ("LZW", "IDM_ACQUIREFILE_TIFF_LZW"),
        ("Packbits", "IDM_ACQUIREFILE_TIFF_PACKBITS"),
    ]:
        tiff.add_command(label=label,command=lambda c=cmd: acquire_file_test(root, dtwain_dll, twain_state, c))

    acquire_file.add_cascade(label="TIFF", menu=tiff)

    for label, cmd in [
        ("WEBP", "IDM_ACQUIREFILE_WEBP"),
        ("Windows Meta File (WMF)", "IDM_ACQUIREFILE_WINDOWSMETAFILE"),
        ("Wireless Bitmap (WBMP)", "IDM_ACQUIREFILE_WIRELESSBITMAP"),
    ]:
        acquire_file.add_command(label=label, command=stub(cmd))

    acquire_menu.add_cascade(label="Acquire File ...",menu=acquire_file,state=tk.DISABLED)
    add_source_required_item(twain_state, acquire_menu)

    source_mode = tk.Menu(acquire_menu, tearoff=False)
    twain_state.source_mode_menu = source_mode
    twain_state.source_mode_menu_items = {}

    for label, cmd in [
        ("Windows BMP", "IDM_ACQUIREFILESOURCE_WINDOWSBMP"),
        ("JPEG (JFIF)", "IDM_ACQUIREFILESOURCE_JPEG"),
        ("TIFF", "IDM_ACQUIREFILESOURCE_TIFF"),
        ("TIFF (Multipage)", "IDM_ACQUIREFILESOURCE_TIFFMULTIPAGE"),
        ("PNG", "IDM_ACQUIREFILESOURCE_PNG"),
        ("PDF", "IDM_ACQUIREFILESOURCE_PDF"),
        ("PDF/A", "IDM_ACQUIREFILESOURCE_PDFA"),
        ("PDF/A2", "IDM_ACQUIREFILESOURCE_PDFA2"),
        ("PDFRASTER", "IDM_ACQUIREFILESOURCE_PDFRASTER"),
        ("FlashPix (FPX)", "IDM_ACQUIREFILESOURCE_FLASHPIX"),
        ("EXIF", "IDM_ACQUIREFILESOURCE_EXIF"),
        ("SPIFF", "IDM_ACQUIREFILESOURCE_SPIFF"),
        ("XBM", "IDM_ACQUIREFILESOURCE_XBM"),
        ("Macintosh PICT", "IDM_ACQUIREFILESOURCE_PICT"),
        ("JP2 (JPEG ISO/IEC 15444-1)", "IDM_ACQUIREFILESOURCE_JP2"),
        ("JPX (JPEG ISO/IEC 15444-2)", "IDM_ACQUIREFILESOURCE_JPX"),
        ("DEJAVU", "IDM_ACQUIREFILESOURCE_DEJAVU"),
    ]:
        source_mode.add_command(label=label,command=lambda c=cmd: 
                                acquire_file_source_mode_test(root,dtwain_dll,twain_state,c),state=tk.DISABLED)
        twain_state.source_mode_menu_items[cmd] = source_mode.index("end")

    acquire_menu.add_cascade(label="Acquire File (Source Mode)...",menu=source_mode,state=tk.DISABLED)
    add_source_required_item(twain_state, acquire_menu)    
    acquire_menu.add_separator()

    show_preview_var = tk.BooleanVar(value=True)
    twain_state.show_preview_var = show_preview_var

    def on_show_preview_changed():
        twain_state.show_preview = show_preview_var.get()

    use_source_ui_var = tk.BooleanVar(value=True)

    twain_state.use_source_ui_var = use_source_ui_var
    twain_state.use_source_ui = True
    acquire_menu.add_checkbutton(label="Use Source UI",variable=use_source_ui_var,
                                 command=lambda: setattr(twain_state,"use_source_ui",1 if use_source_ui_var.get() else 0))

    getmessage_var = tk.BooleanVar(value=False)

    acquire_menu.add_checkbutton(label="Show Preview",variable=show_preview_var,command=on_show_preview_changed)

    discard_blank_var = tk.BooleanVar(value=False)
    twain_state.discard_blank_var = discard_blank_var

    acquire_menu.add_checkbutton(label="Discard Blank Pages...",variable=discard_blank_var,state=tk.DISABLED,
                                 command=lambda: on_discard_blank_pages_changed(root, dtwain_dll, twain_state, discard_blank_var))
    add_source_required_item(twain_state, acquire_menu)

    barcode_var = tk.BooleanVar(value=True)

    acquire_menu.add_checkbutton(label="Show Barcode Information",variable=barcode_var,state=tk.DISABLED,
                                 command=lambda: setattr(twain_state,"show_barcode_information",barcode_var.get()))
    add_source_required_item(twain_state, acquire_menu)

    twain_state.barcode_var = barcode_var
    twain_state.show_barcode_information = True
    barcode_menu_index = acquire_menu.index("end")
    twain_state.barcode_menu = acquire_menu
    twain_state.barcode_menu_index = barcode_menu_index

    acquire_menu.add_separator()
    getmessage_var = tk.BooleanVar(value=False)
    twain_state.getmessage_var = getmessage_var
    twain_state.use_getmessage_loop = False

    acquire_menu.add_checkbutton(label="Use GetMessage TWAIN Loop",variable=getmessage_var,state=tk.DISABLED,
                                 command=lambda: setattr(twain_state,"use_getmessage_loop",getmessage_var.get()))
    add_source_required_item(twain_state, acquire_menu)

    menubar.add_cascade(label="Acquire Test", menu=acquire_menu)

    # TWAIN Logging
    logging_menu = tk.Menu(menubar, tearoff=False)
    logging_menu.add_command(label="Logging Options...",command=lambda: show_logging_options(root, dtwain_dll, twain_state))
    menubar.add_cascade(label="TWAIN Logging", menu=logging_menu)

    # Language
    language_menu = tk.Menu(menubar, tearoff=False)

    for label, cmd in [
        ("Dutch", "ID_LANGUAGE_DUTCH"),
        ("English", "ID_LANGUAGE_ENGLISH"),
        ("French", "ID_LANGUAGE_FRENCH"),
        ("German", "ID_LANGUAGE_GERMAN"),
        ("Spanish", "ID_LANGUAGE_SPANISH"),
        ("Greek", "ID_LANGUAGE_GREEK"),
        ("Italian", "ID_LANGUAGE_ITALIAN"),
        ("Japanese", "ID_LANGUAGE_JAPANESE"),
        ("Korean", "ID_LANGUAGE_KOREAN"),
        ("Portuguese", "ID_LANGUAGE_PORTUGUESE"),
        ("Romanian", "ID_LANGUAGE_ROMANIAN"),
        ("Russian", "ID_LANGUAGE_RUSSIAN"),
        ("Turkish", "ID_LANGUAGE_TURKISH"),
        ("Simplified Chinese", "ID_LANGUAGE_SIMPLIFIEDCHINESE"),
        ("Traditional Chinese", "ID_LANGUAGE_TRADITIONALCHINESE"),
    ]:
        language_menu.add_command(label=label,command=lambda c=cmd: load_language_resource(root, dtwain_dll, c))

    language_menu.add_separator()

    language_menu.add_command(label="Custom Language...",command=lambda: load_custom_language_resource(root, dtwain_dll))

    menubar.add_cascade(label="Language", menu=language_menu)

    # Help
    help_menu = tk.Menu(menubar, tearoff=False)
    help_menu.add_command(label="About ...",command=lambda: AboutDialog(root, dtwain_dll))    
    menubar.add_cascade(label="Help", menu=help_menu)

    root.config(menu=menubar)
    update_source_menu_state(twain_state)
    update_source_mode_file_menu_state(dtwain_dll, twain_state)
    update_application_menu_state(dtwain_dll, twain_state)
    return menubar

