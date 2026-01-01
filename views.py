import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from functions import (check_certificate_status, get_info_TMS1, note_hotro_tms1,
                       notifications_tms1, off_notifications_tms1, block_tms1, unblock_tms1, uninitialize_tms1,
                       get_info_TMS2, notifications_tms2, off_notifications_tms2,
                       block_tms2, unblock_tms2, get_text_single, get_text_data)

# --- Theme Definition ---
COLOR_CONTENT_BG = '#ecf0f1'
COLOR_TEXT = '#2c3e50'
COLOR_PRIMARY = '#3498db'
COLOR_SECONDARY = '#95a5a6'
COLOR_LIGHT_GRAY = '#bdc3c7'
COLOR_WHITE = '#ffffff'
COLOR_BUTTON_ACTION = '#2980b9'
COLOR_BUTTON_ACTION_FG = COLOR_WHITE

FONT_NORMAL = ("Roboto", 10)
FONT_BOLD = ("Roboto", 10, "bold")
FONT_TITLE = ("Roboto", 14, "bold")
FONT_H1 = ("Roboto", 22, "bold")
FONT_MONO = ("Courier New", 10)

class ThemedView(tk.Frame):
    """Base class for all views, handles styling."""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg=COLOR_CONTENT_BG)
        
        # Style configuration for ttk widgets
        style = ttk.Style(self)
        style.configure('TPanedwindow', background=COLOR_CONTENT_BG)
        style.configure('TLabel', background=COLOR_CONTENT_BG, foreground=COLOR_TEXT, font=FONT_NORMAL)
        style.configure('TLabelframe', background=COLOR_CONTENT_BG, borderwidth=1, relief=tk.SOLID)
        style.configure('TLabelframe.Label', background=COLOR_CONTENT_BG, foreground=COLOR_TEXT, font=FONT_BOLD)

class WelcomeView(ThemedView):
    """A simple welcome view shown on startup."""
    def __init__(self, parent, section_name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        container = tk.Frame(self, bg=COLOR_CONTENT_BG)
        container.pack(pady=50, padx=40, fill='both', expand=True)

        tk.Label(container, text="Welcome to CTS Tool Client!", font=FONT_H1, fg=COLOR_TEXT, bg=COLOR_CONTENT_BG).pack()
        tk.Label(container, text=f"Connected to: {section_name}", font=("Roboto", 14), fg=COLOR_PRIMARY, bg=COLOR_CONTENT_BG).pack(pady=10)
        tk.Label(container, text="Select a feature from the sidebar to begin.", font=FONT_NORMAL, fg=COLOR_SECONDARY, bg=COLOR_CONTENT_BG).pack()

class OCSPView(ThemedView):
    """View for checking OCSP status."""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.cert_path = tk.StringVar()
        self.issuer_path = tk.StringVar()

        # Main container with padding
        main_container = tk.Frame(self, bg=COLOR_CONTENT_BG, padx=20, pady=20)
        main_container.pack(fill='both', expand=True)

        # Input Frame
        input_frame = ttk.Labelframe(main_container, text="Input Files")
        input_frame.pack(fill='x', expand=False)
        
        # Certificate Path
        ttk.Label(input_frame, text="Certificate File:").grid(row=0, column=0, sticky='w', pady=(10, 5), padx=10)
        cert_entry = ttk.Entry(input_frame, textvariable=self.cert_path, font=FONT_NORMAL, width=80)
        cert_entry.grid(row=1, column=0, sticky='ew', padx=10)
        self._create_styled_button(input_frame, "Browse...", self._select_cert_file).grid(row=1, column=1, padx=(5, 10), pady=5, ipady=2)

        # Issuer Path
        ttk.Label(input_frame, text="Issuer File:").grid(row=2, column=0, sticky='w', pady=(10, 5), padx=10)
        issuer_entry = ttk.Entry(input_frame, textvariable=self.issuer_path, font=FONT_NORMAL, width=80)
        issuer_entry.grid(row=3, column=0, sticky='ew', padx=10, pady=(0, 10))
        self._create_styled_button(input_frame, "Browse...", self._select_issuer_file).grid(row=3, column=1, padx=(5, 10), pady=5, ipady=2)
        input_frame.grid_columnconfigure(0, weight=1)

        # Check Button
        self._create_styled_button(main_container, "Check OCSP Status", self._check_status, primary=True).pack(pady=20)

        # Result Frame
        result_frame = ttk.Labelframe(main_container, text="Result")
        result_frame.pack(fill='both', expand=True)
        self.result_text = scrolledtext.ScrolledText(result_frame, state=tk.DISABLED, font=FONT_MONO, relief=tk.FLAT, bg=COLOR_WHITE, padx=5, pady=5)
        self.result_text.pack(fill='both', expand=True, padx=10, pady=10)

    def _create_styled_button(self, parent, text, command, primary=False):
        bg = COLOR_PRIMARY if primary else COLOR_SECONDARY
        fg = COLOR_WHITE
        return tk.Button(parent, text=text, command=command, font=FONT_BOLD, bg=bg, fg=fg, relief=tk.FLAT, padx=10, pady=5)

    def _select_cert_file(self):
        path = filedialog.askopenfilename(title="Select Certificate File", filetypes=[("Certificate files", "*.cer;*.pem"), ("All files", "*.*")])
        if path: self.cert_path.set(path)

    def _select_issuer_file(self):
        path = filedialog.askopenfilename(title="Select Issuer File", filetypes=[("Certificate files", "*.cer;*.pem"), ("All files", "*.*")])
        if path: self.issuer_path.set(path)

    def _check_status(self):
        check_certificate_status(self.cert_path.get(), self.issuer_path.get(), self.result_text)

class TMSView(ThemedView):
    """Base class for TMS1 and TMS2 views to share common styling."""
    def __init__(self, parent, db_connection, logger, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.conn = db_connection
        self.logger = logger
        self.configure(padx=10, pady=5)

        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)
        
        self.info_frame = ttk.Labelframe(main_pane, text="Single Token Operations", padding=15)
        main_pane.add(self.info_frame, weight=1)

        self.batch_frame = ttk.Labelframe(main_pane, text="Batch Operations", padding=15)
        main_pane.add(self.batch_frame, weight=2)

        self._create_info_widgets()
        self._create_batch_widgets()

    def _create_styled_button(self, parent, text, command):
        btn = tk.Button(parent, text=text.upper(), command=command, font=("Roboto", 9, "bold"), 
                        bg=COLOR_BUTTON_ACTION, fg=COLOR_BUTTON_ACTION_FG, relief=tk.FLAT, padx=10, pady=8)
        return btn

    def _create_info_widgets(self):
        ttk.Label(self.info_frame, text="Token ID:").pack(anchor='w')
        self.token_id_entry = ttk.Entry(self.info_frame, font=FONT_NORMAL, width=30)
        self.token_id_entry.pack(fill='x', expand=True, pady=(5, 10), ipady=4)
        
        info_button_frame = tk.Frame(self.info_frame, bg=COLOR_CONTENT_BG)
        info_button_frame.pack(fill='x', pady=5)
        
        self._create_styled_button(info_button_frame, "Get Info", self._get_info).pack(side='left', expand=True, fill='x', padx=(0, 5))
        self._create_styled_button(info_button_frame, "Uninitialize", self._uninitialize).pack(side='left', expand=True, fill='x')

        self.info_result_text = scrolledtext.ScrolledText(self.info_frame, state=tk.DISABLED, relief=tk.FLAT, font=FONT_NORMAL, bg=COLOR_WHITE, padx=5, pady=5)
        self.info_result_text.pack(fill='both', expand=True, pady=(10, 0))

    def _create_batch_widgets(self):
        raise NotImplementedError

    def _get_info(self):
        raise NotImplementedError

    def _uninitialize(self):
        uninitialize_tms1(self.conn, self.token_id_entry.get(), self.logger)

class TMS1View(TMSView):
    """View for TMS1 functionalities."""
    def _create_batch_widgets(self):
        ttk.Label(self.batch_frame, text="Token ID List (one per line):").pack(anchor='w')
        self.id_list_text = scrolledtext.ScrolledText(self.batch_frame, height=10, relief=tk.FLAT, font=FONT_NORMAL, bg=COLOR_WHITE, padx=5, pady=5)
        self.id_list_text.pack(fill='both', expand=True, pady=5)

        ttk.Label(self.batch_frame, text="Content / Note:").pack(anchor='w', pady=(10,0))
        self.content_text = tk.Text(self.batch_frame, height=4, relief=tk.FLAT, font=FONT_NORMAL, bg=COLOR_WHITE, padx=5, pady=5)
        self.content_text.pack(fill='x', expand=True, pady=5)

        button_container = tk.Frame(self.batch_frame, bg=COLOR_CONTENT_BG)
        button_container.pack(fill='x', pady=5)
        
        actions = [("ON Note (hotro)", self._note_hotro), ("ON Notifications", self._on_notifications), ("OFF Notifications", self._off_notifications)]
        for text, cmd in actions:
            self._create_styled_button(button_container, text, cmd).pack(side='left', expand=True, fill='x', padx=(0, 5))

        block_unblock_container = tk.Frame(self.batch_frame, bg=COLOR_CONTENT_BG)
        block_unblock_container.pack(fill='x', pady=5)
        self._create_styled_button(block_unblock_container, "Block", self._block).pack(side='left', expand=True, fill='x', padx=(0, 5))
        self._create_styled_button(block_unblock_container, "Unblock", self._unblock).pack(side='left', expand=True, fill='x')

    def _get_info(self):
        get_info_TMS1(self.conn, self.token_id_entry.get(), self.info_result_text)
    def _note_hotro(self):
        note_hotro_tms1(self.conn, get_text_data(self.id_list_text), get_text_single(self.content_text), self.logger)
    def _on_notifications(self):
        notifications_tms1(self.conn, get_text_data(self.id_list_text), get_text_single(self.content_text), self.logger)
    def _off_notifications(self):
        off_notifications_tms1(self.conn, get_text_data(self.id_list_text), self.logger)
    def _block(self):
        block_tms1(self.conn, get_text_data(self.id_list_text), get_text_single(self.content_text), self.logger)
    def _unblock(self):
        unblock_tms1(self.conn, get_text_data(self.id_list_text), self.logger)

class TMS2View(TMSView):
    """View for TMS2 functionalities."""
    def _create_info_widgets(self):
        # Override to remove 'Uninitialize' button which is not applicable for TMS2
        ttk.Label(self.info_frame, text="Token ID:").pack(anchor='w')
        self.token_id_entry = ttk.Entry(self.info_frame, font=FONT_NORMAL, width=30)
        self.token_id_entry.pack(fill='x', expand=True, pady=(5, 10), ipady=4)
        self._create_styled_button(self.info_frame, "Get Info", self._get_info).pack(fill='x')
        self.info_result_text = scrolledtext.ScrolledText(self.info_frame, state=tk.DISABLED, relief=tk.FLAT, font=FONT_NORMAL, bg=COLOR_WHITE, padx=5, pady=5)
        self.info_result_text.pack(fill='both', expand=True, pady=(10, 0))

    def _create_batch_widgets(self):
        ttk.Label(self.batch_frame, text="Token ID List (one per line):").pack(anchor='w')
        self.id_list_text = scrolledtext.ScrolledText(self.batch_frame, height=10, relief=tk.FLAT, font=FONT_NORMAL, bg=COLOR_WHITE, padx=5, pady=5)
        self.id_list_text.pack(fill='both', expand=True, pady=5)

        ttk.Label(self.batch_frame, text="Title:").pack(anchor='w', pady=(10,0))
        self.title_text = tk.Text(self.batch_frame, height=1, relief=tk.FLAT, font=FONT_NORMAL, bg=COLOR_WHITE, padx=5, pady=5)
        self.title_text.pack(fill='x', expand=True, pady=5)
        
        ttk.Label(self.batch_frame, text="Content / Note:").pack(anchor='w')
        self.content_text = tk.Text(self.batch_frame, height=3, relief=tk.FLAT, font=FONT_NORMAL, bg=COLOR_WHITE, padx=5, pady=5)
        self.content_text.pack(fill='x', expand=True, pady=5)

        button_container = tk.Frame(self.batch_frame, bg=COLOR_CONTENT_BG)
        button_container.pack(fill='x', pady=5)
        
        self._create_styled_button(button_container, "ON Notifications", self._on_notifications).pack(side='left', expand=True, fill='x', padx=(0, 5))
        self._create_styled_button(button_container, "OFF Notifications", self._off_notifications).pack(side='left', expand=True, fill='x')
        self._create_styled_button(button_container, "Block", self._block).pack(side='left', expand=True, fill='x', padx=(5, 0))
        self._create_styled_button(button_container, "Unblock", self._unblock).pack(side='left', expand=True, fill='x', padx=5)

    def _get_info(self):
        get_info_TMS2(self.conn, self.token_id_entry.get(), self.info_result_text)
    def _uninitialize(self):
        # This method is not applicable for TMS2 but must be implemented
        # Or the base class could be designed differently. For now, do nothing.
        pass
    def _on_notifications(self):
        notifications_tms2(self.conn, get_text_data(self.id_list_text), get_text_single(self.title_text), get_text_single(self.content_text), self.logger)
    def _off_notifications(self):
        off_notifications_tms2(self.conn, get_text_data(self.id_list_text), self.logger)
    def _block(self):
        block_tms2(self.conn, get_text_data(self.id_list_text), get_text_single(self.content_text), self.logger)
    def _unblock(self):
        unblock_tms2(self.conn, get_text_data(self.id_list_text), self.logger)