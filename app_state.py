class TwainState:
    def __init__(self):
        self.source = None
        self.source_name = ""
        self.show_preview = True
        self.use_source_ui = True
        self.discard_blank_pages = False
        self.blank_page_threshold = 0.0
        self.use_getmessage_loop = False
        self.source_required_menu_items = []
        self.pdf_text_element = None
        self.pdf_page_count = 1
        self.current_file_type = None
