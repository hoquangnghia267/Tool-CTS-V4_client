import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from functions import (check_certificate_status, get_info_TMS1, note_hotro_tms1, 
                       notifications_tms1, off_notifications_tms1, block_tms1, unblock_tms1, uninitialize_tms1,
                       get_info_TMS2, notifications_tms2, off_notifications_tms2, 
                       block_tms2, unblock_tms2, get_text_single, get_text_data)

class BaseView(tk.Frame):
    """Base class for all views in the application."""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pack(fill='both', expand=True)

class WelcomeView(BaseView):
    """A simple welcome view shown on startup."""
    def __init__(self, parent, section_name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        label = tk.Label(self, text=f"Welcome to CTS Tool v4 Client!", font=("Helvetica", 18, "bold"))
        label.pack(pady=50, padx=20)
        
        info_label = tk.Label(self, text=f"Connected to: {section_name}", font=("Helvetica", 12))
        info_label.pack(pady=10, padx=20)
        
        instructions_label = tk.Label(self, text="Select a feature from the sidebar to begin.", font=("Helvetica", 10))
        instructions_label.pack(pady=5, padx=20)

class OCSPView(BaseView):
    """View for checking OCSP status."""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # --- UI Elements ---
        container = tk.Frame(self)
        container.pack(pady=20, padx=20, fill='x')

        self.cert_path = tk.StringVar()
        self.issuer_path = tk.StringVar()

        # Certificate Path
        tk.Label(container, text="Certificate File:").grid(row=0, column=0, sticky='w', pady=2)
        cert_entry = tk.Entry(container, textvariable=self.cert_path, width=70)
        cert_entry.grid(row=1, column=0, sticky='ew', padx=(0, 5))
        tk.Button(container, text="Browse...", command=self._select_cert_file).grid(row=1, column=1, sticky='w')

        # Issuer Path
        tk.Label(container, text="Issuer File:").grid(row=2, column=0, sticky='w', pady=2)
        issuer_entry = tk.Entry(container, textvariable=self.issuer_path, width=70)
        issuer_entry.grid(row=3, column=0, sticky='ew', padx=(0, 5))
        tk.Button(container, text="Browse...", command=self._select_issuer_file).grid(row=3, column=1, sticky='w')
        
        container.grid_columnconfigure(0, weight=1)
        
        # Check Button
        check_button = tk.Button(self, text="Check OCSP Status", command=self._check_status, font=("Helvetica", 10, "bold"))
        check_button.pack(pady=10)

        # Result Text Area
        result_frame = tk.Frame(self)
        result_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=20, state=tk.DISABLED, font=("Courier New", 10))
        self.result_text.pack(fill='both', expand=True)

    def _select_cert_file(self):
        path = filedialog.askopenfilename(title="Select Certificate File", filetypes=[("Certificate files", "*.cer;*.pem"), ("All files", "*.*")])
        if path:
            self.cert_path.set(path)

    def _select_issuer_file(self):
        path = filedialog.askopenfilename(title="Select Issuer File", filetypes=[("Certificate files", "*.cer;*.pem"), ("All files", "*.*")])
        if path:
            self.issuer_path.set(path)

    def _check_status(self):
        cert_path = self.cert_path.get()
        issuer_path = self.issuer_path.get()
        check_certificate_status(cert_path, issuer_path, self.result_text)

class TMS1View(BaseView):
    """View for TMS1 functionalities."""
    def __init__(self, parent, db_connection, logger, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.conn = db_connection
        self.logger = logger

        # --- Layout ---
        # Main PanedWindow to divide the view
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left side for single token info
        info_frame = ttk.Labelframe(main_pane, text="Single Token Operations", padding=10)
        main_pane.add(info_frame, weight=1)

        # Right side for batch operations
        batch_frame = ttk.Labelframe(main_pane, text="Batch Operations", padding=10)
        main_pane.add(batch_frame, weight=2)
        
        # --- Info Frame Widgets ---
        tk.Label(info_frame, text="Token ID:").pack(anchor='w')
        self.token_id_entry = tk.Entry(info_frame, width=30)
        self.token_id_entry.pack(fill='x', expand=True, pady=5)
        
        # Button container for single operations
        info_button_frame = tk.Frame(info_frame)
        info_button_frame.pack(fill='x', pady=5)
        
        tk.Button(info_button_frame, text="Get Info", command=self._get_info).pack(side='left', expand=True, fill='x', padx=(0,2))
        tk.Button(info_button_frame, text="Uninitialize", command=self._uninitialize).pack(side='left', expand=True, fill='x', padx=(2,0))

        self.info_result_text = scrolledtext.ScrolledText(info_frame, height=15, state=tk.DISABLED)
        self.info_result_text.pack(fill='both', expand=True, pady=5)
        
        # --- Batch Frame Widgets ---
        tk.Label(batch_frame, text="Token ID List (one per line):").pack(anchor='w')
        self.id_list_text = scrolledtext.ScrolledText(batch_frame, height=10)
        self.id_list_text.pack(fill='both', expand=True, pady=5)

        tk.Label(batch_frame, text="Content / Note:").pack(anchor='w', pady=(10,0))
        self.content_text = tk.Text(batch_frame, height=4)
        self.content_text.pack(fill='x', expand=True, pady=5)

        button_container = tk.Frame(batch_frame)
        button_container.pack(fill='x', pady=5)
        
        # Batch buttons
        tk.Button(button_container, text="ON Note (hotro)", command=self._note_hotro).pack(side='left', expand=True, fill='x')
        tk.Button(button_container, text="ON Notifications", command=self._on_notifications).pack(side='left', expand=True, fill='x')
        tk.Button(button_container, text="OFF Notifications", command=self._off_notifications).pack(side='left', expand=True, fill='x')
        tk.Button(button_container, text="Block", command=self._block).pack(side='left', expand=True, fill='x', padx=5)
        tk.Button(button_container, text="Unblock", command=self._unblock).pack(side='left', expand=True, fill='x')

    def _get_info(self):
        token_id = self.token_id_entry.get()
        get_info_TMS1(self.conn, token_id, self.info_result_text)
    
    def _uninitialize(self):
        token_id = self.token_id_entry.get()
        uninitialize_tms1(self.conn, token_id, self.logger)
        
    def _note_hotro(self):
        ids = get_text_data(self.id_list_text)
        content = get_text_single(self.content_text)
        note_hotro_tms1(self.conn, ids, content, self.logger)

    def _on_notifications(self):
        ids = get_text_data(self.id_list_text)
        content = get_text_single(self.content_text)
        notifications_tms1(self.conn, ids, content, self.logger)

    def _off_notifications(self):
        ids = get_text_data(self.id_list_text)
        off_notifications_tms1(self.conn, ids, self.logger)
        
    def _block(self):
        ids = get_text_data(self.id_list_text)
        content = get_text_single(self.content_text)
        block_tms1(self.conn, ids, content, self.logger)

    def _unblock(self):
        ids = get_text_data(self.id_list_text)
        unblock_tms1(self.conn, ids, self.logger)

class TMS2View(BaseView):
    """View for TMS2 functionalities."""
    def __init__(self, parent, db_connection, logger, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.conn = db_connection
        self.logger = logger

        # --- Layout ---
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        info_frame = ttk.Labelframe(main_pane, text="Get Token Information", padding=10)
        main_pane.add(info_frame, weight=1)

        batch_frame = ttk.Labelframe(main_pane, text="Batch Operations", padding=10)
        main_pane.add(batch_frame, weight=2)
        
        # --- Info Frame Widgets ---
        tk.Label(info_frame, text="Token ID:").pack(anchor='w')
        self.token_id_entry = tk.Entry(info_frame, width=30)
        self.token_id_entry.pack(fill='x', expand=True, pady=5)
        tk.Button(info_frame, text="Get Info", command=self._get_info).pack(pady=5)
        self.info_result_text = scrolledtext.ScrolledText(info_frame, height=15, state=tk.DISABLED)
        self.info_result_text.pack(fill='both', expand=True, pady=5)
        
        # --- Batch Frame Widgets ---
        tk.Label(batch_frame, text="Token ID List (one per line):").pack(anchor='w')
        self.id_list_text = scrolledtext.ScrolledText(batch_frame, height=10)
        self.id_list_text.pack(fill='both', expand=True, pady=5)

        tk.Label(batch_frame, text="Title:").pack(anchor='w', pady=(10,0))
        self.title_text = tk.Text(batch_frame, height=1)
        self.title_text.pack(fill='x', expand=True, pady=5)
        
        tk.Label(batch_frame, text="Content / Note:").pack(anchor='w')
        self.content_text = tk.Text(batch_frame, height=3)
        self.content_text.pack(fill='x', expand=True, pady=5)

        button_container = tk.Frame(batch_frame)
        button_container.pack(fill='x', pady=5)
        
        tk.Button(button_container, text="ON Notifications", command=self._on_notifications).pack(side='left', expand=True, fill='x')
        tk.Button(button_container, text="OFF Notifications", command=self._off_notifications).pack(side='left', expand=True, fill='x')
        tk.Button(button_container, text="Block", command=self._block).pack(side='left', expand=True, fill='x', padx=5)
        tk.Button(button_container, text="Unblock", command=self._unblock).pack(side='left', expand=True, fill='x')

    def _get_info(self):
        token_id = self.token_id_entry.get()
        get_info_TMS2(self.conn, token_id, self.info_result_text)
        
    def _on_notifications(self):
        ids = get_text_data(self.id_list_text)
        title = get_text_single(self.title_text)
        content = get_text_single(self.content_text)
        notifications_tms2(self.conn, ids, title, content, self.logger)

    def _off_notifications(self):
        ids = get_text_data(self.id_list_text)
        off_notifications_tms2(self.conn, ids, self.logger)
        
    def _block(self):
        ids = get_text_data(self.id_list_text)
        content = get_text_single(self.content_text)
        block_tms2(self.conn, ids, content, self.logger)

    def _unblock(self):
        ids = get_text_data(self.id_list_text)
        unblock_tms2(self.conn, ids, self.logger)