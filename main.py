import tkinter as tk
from tkinter import messagebox
from database import get_database_config, connect_to_database
from ui_manager import MainApplication

def show_connect_screen():
    """
    Displays a professional-looking initial screen for the user to enter their
    credentials and connect to the database.
    """
    root = tk.Tk()
    root.title("CTS Tool Client - Login")

    # --- Window Configuration ---
    window_width = 600
    window_height = 350
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_x = int((screen_width / 2) - (window_width / 2))
    position_y = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
    root.resizable(False, False)
    
    # --- Main Layout ---
    # The main frame holds both the left branding pane and the right form pane
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # --- Left Pane (Branding) ---
    left_pane = tk.Frame(main_frame, bg='#2c3e50', width=220)
    left_pane.pack(side=tk.LEFT, fill=tk.Y)
    left_pane.pack_propagate(False)

    tk.Label(left_pane, text="CTS", font=("Roboto", 38, "bold"), fg='white', bg='#2c3e50').pack(pady=(60, 0))
    tk.Label(left_pane, text="Tool Client", font=("Roboto", 16), fg='#bdc3c7', bg='#2c3e50').pack()

    # --- Right Pane (Login Form) ---
    right_pane = tk.Frame(main_frame, bg='#ecf0f1', padx=40, pady=30)
    right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def attempt_connect(event=None):
        section_name = section_entry.get()
        password = password_entry.get()

        if not section_name:
            messagebox.showwarning("Input Error", "Please enter a System Name.")
            return
        if not password:
            messagebox.showwarning("Input Error", "Please enter the Password.")
            return

        try:
            db_config = get_database_config(section_name, password)
            conn = connect_to_database(db_config)

            if conn and conn.is_connected():
                root.destroy()
                main_app_root = tk.Tk()
                app = MainApplication(main_app_root, conn, section_name)
                main_app_root.mainloop()
            else:
                messagebox.showerror("Connection Failed", "Could not connect to the database. Check config and network.")
        except Exception as e:
            messagebox.showerror("Login Error", str(e))

    # Form Title
    tk.Label(right_pane, text="Secure Login", font=("Roboto", 20, "bold"), bg='#ecf0f1').pack(pady=(0, 30))

    # System Name
    tk.Label(right_pane, text="System Name", font=("Roboto", 10), bg='#ecf0f1', fg='#34495e').pack(anchor='w')
    section_entry = tk.Entry(right_pane, font=("Helvetica", 12), width=35, relief=tk.FLAT)
    section_entry.pack(pady=(5, 15), ipady=5)

    # Password
    tk.Label(right_pane, text="Password", font=("Roboto", 10), bg='#ecf0f1', fg='#34495e').pack(anchor='w')
    password_entry = tk.Entry(right_pane, font=("Helvetica", 12), show='*', width=35, relief=tk.FLAT)
    password_entry.pack(pady=(5, 20), ipady=5)

    # Bind Enter key to the connect function for both entries
    section_entry.bind('<Return>', lambda e: password_entry.focus_set())
    password_entry.bind('<Return>', attempt_connect)

    # Connect Button
    connect_button = tk.Button(right_pane, text="CONNECT", font=("Roboto", 11, "bold"),
                               bg='#3498db', fg='white', command=attempt_connect,
                               relief=tk.FLAT, padx=20, pady=8, activebackground='#2980b9', activeforeground='white')
    connect_button.pack()

    section_entry.focus_set()
    root.mainloop()

if __name__ == "__main__":
    show_connect_screen()