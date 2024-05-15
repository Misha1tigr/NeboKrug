import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from settings_manager import save_settings, load_settings


def create_menu_bar(root):
    menubar = tk.Menu(root)

    # Units of Measurement
    menubar.add_command(label="Units of Measurement", command=lambda: settings_units_window(root))

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


def settings_units_window(root):
    def on_save_and_close():
        settings = {
            "temperature_unit": temperature_unit_selected_option.get(),
            "wind_speed_unit": windspeed_unit_selected_option.get(),
            "precipitation_unit": precipitation_unit_selected_option.get(),
        }
        save_settings(settings)  # Save the settings to a JSON file
        settings_window.destroy()
        root.attributes("-disabled", 0)  # Re-enable the main window

    settings = load_settings()  # Load settings from the JSON file

    settings_window = tk.Toplevel()
    settings_window.title("Units of Measurement")
    settings_window.protocol("WM_DELETE_WINDOW", on_save_and_close)

    frame = ttk.Frame(settings_window, padding="10")
    frame.pack(fill='both', expand=True)

    # Temperature Units
    ttk.Label(frame, text="Temperature Units").grid(column=0, row=0, padx=5, pady=5)
    temperature_unit_options = ["Celsius °C", "Fahrenheit °F"]
    temperature_unit_selected_option = tk.StringVar()
    temperature_unit_selected_option.set(settings.get("temperature_unit", "Celsius °C"))
    temperature_unit_dropdown = ttk.Combobox(frame, textvariable=temperature_unit_selected_option,
                                             values=temperature_unit_options, state="readonly")
    temperature_unit_dropdown.grid(column=1, row=0, padx=5, pady=5)

    # Wind Speed Units
    ttk.Label(frame, text="Wind Speed Units").grid(column=0, row=1, padx=5, pady=5)
    windspeed_unit_options = ["Km/h", "m/s", "Mph", "Knots"]
    windspeed_unit_selected_option = tk.StringVar()
    windspeed_unit_selected_option.set(settings.get("wind_speed_unit", "Km/h"))
    windspeed_unit_dropdown = ttk.Combobox(frame, textvariable=windspeed_unit_selected_option,
                                           values=windspeed_unit_options, state="readonly")
    windspeed_unit_dropdown.grid(column=1, row=1, padx=5, pady=5)

    # Precipitation Units
    ttk.Label(frame, text="Precipitation Units").grid(column=0, row=2, padx=5, pady=5)
    precipitation_unit_options = ["Millimeter", "Inch"]
    precipitation_unit_selected_option = tk.StringVar()
    precipitation_unit_selected_option.set(settings.get("precipitation_unit", "Millimeter"))
    precipitation_unit_dropdown = ttk.Combobox(frame, textvariable=precipitation_unit_selected_option,
                                               values=precipitation_unit_options, state="readonly")
    precipitation_unit_dropdown.grid(column=1, row=2, padx=5, pady=5)

    # Save and Close Button
    save_and_close_btn = ttk.Button(frame, text="Save & Close", command=on_save_and_close)
    save_and_close_btn.grid(column=0, row=3, columnspan=2, pady=10)

    settings_window.transient(root)
    settings_window.grab_set()


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
