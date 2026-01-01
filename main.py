import tkinter as tk
from tkinter import messagebox
from database import get_database_config, connect_to_database
from ui_manager import MainApplication

def show_connect_screen():
    """
    Displays the initial screen for the user to enter the database section name
    and connect to the database.
    """
    root = tk.Tk()
    root.title("Connect to Database")
    
    # --- Center The Window ---
    window_width = 300
    window_height = 150
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_x = int((screen_width / 2) - (window_width / 2))
    position_y = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
    root.resizable(False, False)

    def attempt_connect(event=None):
        section_name = section_entry.get()
        if not section_name:
            messagebox.showwarning("Input Error", "Please enter a system name.")
            return

        try:
            db_config = get_database_config(section_name)
            conn = connect_to_database(db_config)
            
            if conn and conn.is_connected():
                root.destroy()  # Close the connection window
                # Launch the main application
                main_app_root = tk.Tk()
                app = MainApplication(main_app_root, conn, section_name)
                main_app_root.mainloop()
            else:
                messagebox.showerror("Connection Failed", "Could not connect to the database. Check config and network.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get database config for '{section_name}'.\n\n{e}")

    # --- Widgets ---
    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True, fill=tk.BOTH)

    tk.Label(main_frame, text="Enter System Name:").pack(pady=(0, 5))

    section_entry = tk.Entry(main_frame, width=30)
    section_entry.pack(pady=5)
    section_entry.bind('<Return>', attempt_connect)

    connect_button = tk.Button(main_frame, text="Connect", command=attempt_connect)
    connect_button.pack(pady=10)
    
    # Set focus to the entry widget
    section_entry.focus_set()

    root.mainloop()

if __name__ == "__main__":
    show_connect_screen()