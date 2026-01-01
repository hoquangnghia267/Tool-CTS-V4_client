import tkinter as tk
from tkinter import ttk
import app_config
from views import WelcomeView, OCSPView, TMS1View, TMS2View
from functions import setup_logging

class MainApplication:
    """
    The main application class that creates and manages the UI.
    """
    def __init__(self, root, db_connection, section_name):
        self.root = root
        self.conn = db_connection
        self.section_name = section_name
        self.logger = setup_logging(section_name)

        self.root.title("CTS Tool v4 Client")
        
        # --- Center The Window ---
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_x = int((screen_width / 2) - (app_config.WINDOW_WIDTH / 2))
        position_y = int((screen_height / 2) - (app_config.WINDOW_HEIGHT / 2))
        self.root.geometry(f"{app_config.WINDOW_WIDTH}x{app_config.WINDOW_HEIGHT}+{position_x}+{position_y}")
        
        # --- Main Layout ---
        # Use a PanedWindow for resizable sidebar
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # Sidebar Frame
        self.sidebar_frame = tk.Frame(main_pane, width=150, bg='#f0f0f0')
        self.sidebar_frame.pack_propagate(False)
        main_pane.add(self.sidebar_frame, weight=0)

        # Content Frame
        self.content_frame = tk.Frame(main_pane)
        main_pane.add(self.content_frame, weight=1)

        
        # --- Status Bar ---
        status_bar_frame = tk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        status_bar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = tk.Label(status_bar_frame, text=f"Connected to: {self.section_name}", anchor='w')
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.views = {}
        self._create_sidebar_buttons()
        self._create_views()
        
        # Show the welcome view initially
        self.show_view("welcome")

    def _create_sidebar_buttons(self):
        """Creates the navigation buttons in the sidebar."""
        buttons_config = [
            ("Check OCSP", "ocsp"),
            ("TMS1 Tools", "tms1"),
            ("TMS2 Tools", "tms2")
        ]
        
        tk.Label(self.sidebar_frame, text="Features", font=("Helvetica", 12, "bold"), bg='#f0f0f0').pack(pady=10)

        for text, view_name in buttons_config:
            button = tk.Button(
                self.sidebar_frame, 
                text=text, 
                command=lambda v=view_name: self.show_view(v),
                pady=5,
                font=("Helvetica", 10)
            )
            button.pack(fill='x', padx=10, pady=5)

    def _create_views(self):
        """Initializes all the different view frames."""
        
        # Each view is a frame that lives in the content_frame
        self.views = {
            "welcome": WelcomeView(self.content_frame, self.section_name),
            "ocsp": OCSPView(self.content_frame),
            "tms1": TMS1View(self.content_frame, self.conn, self.logger),
            "tms2": TMS2View(self.content_frame, self.conn, self.logger)
        }

    def show_view(self, view_name):
        """Hides all other views and shows the requested one."""
        for name, view in self.views.items():
            view.pack_forget()  # Hide the view

        # Show the selected view
        view_to_show = self.views.get(view_name)
        if view_to_show:
            view_to_show.pack(fill='both', expand=True)