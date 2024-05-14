import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def create_menu_bar(root):
    menubar = tk.Menu(root)

    # Units of Measurement
    menubar.add_command(label="Units of Measurement", command=lambda: open_sample_window("Units of Measurement"))

    # Your Locations
    menubar.add_command(label="Your Locations", command=lambda: open_sample_window("Your Locations"))

    # Other Settings
    menubar.add_command(label="Other Settings", command=lambda: open_sample_window("Other Settings"))

    # Info Menu
    info_menu = tk.Menu(menubar, tearoff=0)
    info_menu.add_command(label="Help", command=lambda: open_sample_window("Help"))
    info_menu.add_command(label="Feedback", command=lambda: open_sample_window("Feedback"))
    info_menu.add_command(label="About", command=lambda: open_sample_window("About"))
    menubar.add_cascade(label="Info", menu=info_menu)

    # Exit
    menubar.add_command(label="Exit", command=root.quit)

    root.config(menu=menubar)

def open_sample_window(title):
    window = tk.Toplevel()
    window.title(title)
    frame = ttk.Frame(window, padding="10")
    frame.pack(fill='both', expand=True)
    sample_text = ttk.Label(frame, text=f"Sample text for {title}")
    sample_text.pack()

def create_tabs(root):
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # Forecast Tab
    forecast_frame = ttk.Frame(notebook, padding="10")
    ttk.Label(forecast_frame, text="Sample text for Forecast").pack()
    notebook.add(forecast_frame, text="Forecast")

    # Forecast AI Tab
    forecast_ai_frame = ttk.Frame(notebook, padding="10")
    ttk.Label(forecast_ai_frame, text="Sample text for Forecast AI").pack()
    notebook.add(forecast_ai_frame, text="Forecast AI")

    # History Tab
    history_frame = ttk.Frame(notebook, padding="10")
    ttk.Label(history_frame, text="Sample text for History").pack()
    notebook.add(history_frame, text="History")

    # This day in history Tab
    this_day_history_frame = ttk.Frame(notebook, padding="10")
    ttk.Label(this_day_history_frame, text="Sample text for This day in history").pack()
    notebook.add(this_day_history_frame, text="This day in history")

    # Fun fact Tab
    fun_fact_frame = ttk.Frame(notebook, padding="10")
    ttk.Label(fun_fact_frame, text="Sample text for Fun fact").pack()
    notebook.add(fun_fact_frame, text="Fun fact")

def initialize_main_window():
    root = tk.Tk()
    root.title("Weather App")

    # Create a menu bar
    create_menu_bar(root)

    # Create tabs
    create_tabs(root)

    root.mainloop()

if __name__ == "__main__":
    initialize_main_window()