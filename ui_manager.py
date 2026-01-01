import tkinter as tk
from tkinter import ttk
import app_config
from views import WelcomeView, OCSPView, TMS1View, TMS2View
from functions import setup_logging

# --- Theme Colors and Fonts ---
COLOR_SIDEBAR_BG = '#2c3e50'
COLOR_CONTENT_BG = '#ecf0f1'
COLOR_BUTTON_NORMAL_BG = '#34495e'
COLOR_BUTTON_NORMAL_FG = '#ecf0f1'
COLOR_BUTTON_HOVER_BG = '#4e6d8c'
COLOR_BUTTON_ACTIVE_BG = '#3498db'
COLOR_BUTTON_ACTIVE_FG = 'white'
FONT_BUTTON = ("Roboto", 11)
FONT_TITLE = ("Roboto", 12, "bold")

class MainApplication:
    """
    The main application class that creates and manages the UI.
    """
    def __init__(self, root, db_connection, section_name):
        self.root = root
        self.conn = db_connection
        self.section_name = section_name
        self.logger = setup_logging(section_name)
        self.sidebar_buttons = {}

        self.root.title("CTS Tool v4 Client")
        self.root.configure(bg=COLOR_CONTENT_BG)
        
        # --- Center The Window ---
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        pos_x = int((screen_width / 2) - (app_config.WINDOW_WIDTH / 2))
        pos_y = int((screen_height / 2) - (app_config.WINDOW_HEIGHT / 2))
        self.root.geometry(f"{app_config.WINDOW_WIDTH}x{app_config.WINDOW_HEIGHT}+{pos_x}+{pos_y}")
        
        # --- Main Layout ---
        # The root window will act as the main content area container
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Sidebar Frame
        self.sidebar_frame = tk.Frame(self.root, width=180, bg=COLOR_SIDEBAR_BG)
        self.sidebar_frame.grid(row=0, column=0, sticky='nsw')
        self.sidebar_frame.pack_propagate(False)

        # Content Frame
        self.content_frame = tk.Frame(self.root, bg=COLOR_CONTENT_BG)
        self.content_frame.grid(row=0, column=1, sticky='nsew')

        # Status Bar
        status_bar_frame = tk.Frame(self.root, bg=COLOR_SIDEBAR_BG)
        status_bar_frame.grid(row=1, column=0, columnspan=2, sticky='ew')
        self.status_label = tk.Label(status_bar_frame, text=f"Connected to: {self.section_name}", 
                                     anchor='w', bg=COLOR_SIDEBAR_BG, fg='white', font=("Roboto", 9))
        self.status_label.pack(side=tk.LEFT, padx=10, pady=2)

        self.views = {}
        self._create_sidebar_buttons()
        self._create_views()
        
        # Show the welcome view initially
        self.show_view("welcome")

    def _create_sidebar_buttons(self):
        """Creates the navigation buttons in the sidebar."""
        tk.Label(self.sidebar_frame, text="FEATURES", font=FONT_TITLE, bg=COLOR_SIDEBAR_BG, fg='#95a5a6').pack(pady=(20, 10))

        buttons_config = [
            ("Welcome", "welcome"),
            ("Check OCSP", "ocsp"),
            ("TMS1 Tools", "tms1"),
            ("TMS2 Tools", "tms2")
        ]

        for text, view_name in buttons_config:
            button = tk.Button(
                self.sidebar_frame, 
                text=text, 
                font=FONT_BUTTON,
                bg=COLOR_BUTTON_NORMAL_BG,
                fg=COLOR_BUTTON_NORMAL_FG,
                activebackground=COLOR_BUTTON_HOVER_BG,
                activeforeground=COLOR_BUTTON_NORMAL_FG,
                relief=tk.FLAT,
                anchor='w',
                padx=20,
                command=lambda v=view_name: self.show_view(v)
            )
            button.pack(fill='x', padx=10, pady=4)
            self.sidebar_buttons[view_name] = button

    def _create_views(self):
        """Initializes all the different view frames."""
        self.views = {
            "welcome": WelcomeView(self.content_frame, self.section_name, bg=COLOR_CONTENT_BG),
            "ocsp": OCSPView(self.content_frame, bg=COLOR_CONTENT_BG),
            "tms1": TMS1View(self.content_frame, self.conn, self.logger, bg=COLOR_CONTENT_BG),
            "tms2": TMS2View(self.content_frame, self.conn, self.logger, bg=COLOR_CONTENT_BG)
        }

    def show_view(self, view_name):
        """Hides all other views and shows the requested one."""
        for name, view in self.views.items():
            view.pack_forget()

        for name, btn in self.sidebar_buttons.items():
            if name == view_name:
                btn.config(bg=COLOR_BUTTON_ACTIVE_BG, fg=COLOR_BUTTON_ACTIVE_FG)
            else:
                btn.config(bg=COLOR_BUTTON_NORMAL_BG, fg=COLOR_BUTTON_NORMAL_FG)

        view_to_show = self.views.get(view_name)
        if view_to_show:
            view_to_show.pack(fill='both', expand=True, padx=10, pady=10)