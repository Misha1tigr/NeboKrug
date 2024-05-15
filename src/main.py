import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from settings_manager import save_settings, load_settings, save_locations
from geocoding import search_location


def create_menu_bar(root):
    menubar = tk.Menu(root)

    # Units of Measurement
    menubar.add_command(label="Units of Measurement", command=lambda: settings_units_window(root))

    # Your Locations
    menubar.add_command(label="Your Locations", command=lambda: settings_locations_window(root))

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
        changed_settings = {
            "temperature_unit": temperature_unit_selected_option.get(),
            "wind_speed_unit": windspeed_unit_selected_option.get(),
            "precipitation_unit": precipitation_unit_selected_option.get(),
        }
        save_settings(changed_settings)  # Save the settings to a JSON file
        settings_window.destroy()

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


def settings_locations_window(root):
    def on_search():
        query = search_var.get()
        if query:
            results = search_location(query)
            search_results_listbox.delete(0, tk.END)
            for result in results:
                name = result.get('name')
                country = result.get('country')
                admin1 = result.get('admin1', 'N/A')
                latitude = result.get('latitude')
                longitude = result.get('longitude')
                full_name = f"{name}, {admin1}, {country} (Lat: {latitude}, Lon: {longitude})"
                search_results_listbox.insert(tk.END, full_name)
                search_results_listbox.results[full_name] = result

    def on_add_location():
        selected = search_results_listbox.curselection()
        if selected:
            location = search_results_listbox.get(selected)
            stored_locations_listbox.insert(tk.END, location)
            stored_locations_listbox.locations.append(search_results_listbox.results[location])

    def on_delete_location():
        selected = stored_locations_listbox.curselection()
        if selected:
            index = selected[0]
            del stored_locations_listbox.locations[index]
            stored_locations_listbox.delete(index)

    def on_save_and_close():
        locations = stored_locations_listbox.locations
        save_locations(locations)  # Save the locations to the JSON file
        locations_window.destroy()

    locations = load_settings().get("locations", [])  # Load locations from the JSON file

    locations_window = tk.Toplevel()
    locations_window.title("Your Locations")
    locations_window.protocol("WM_DELETE_WINDOW", on_save_and_close)

    frame = ttk.Frame(locations_window, padding="10")
    frame.pack(fill='both', expand=True)
    ttk.Label(frame, text="Your saved locations").grid(column=0, row=0, columnspan=2, padx=5, pady=5)
    # Listbox for stored locations
    ttk.Label(frame, text="Stored Locations").grid(column=0, row=1, columnspan=2, padx=5, pady=5)
    stored_locations_listbox = tk.Listbox(frame, height=10, width=80, exportselection=False)
    stored_locations_listbox.locations = []
    for location in locations:
        name = location.get('name')
        country = location.get('country')
        admin1 = location.get('admin1', 'N/A')
        latitude = location.get('latitude')
        longitude = location.get('longitude')
        full_name = f"{name}, {admin1}, {country} (Lat: {latitude}, Lon: {longitude})"
        stored_locations_listbox.insert(tk.END, full_name)
        stored_locations_listbox.locations.append(location)
    stored_locations_listbox.grid(column=0, row=2, columnspan=2, padx=5, pady=5)

    # Control buttons for locations
    add_location_btn = ttk.Button(frame, text="Add", command=on_add_location)
    add_location_btn.grid(column=0, row=3, padx=5, pady=5)

    delete_location_btn = ttk.Button(frame, text="Delete", command=on_delete_location)
    delete_location_btn.grid(column=1, row=3, padx=5, pady=5)

    # Search field for locations
    ttk.Label(frame, text="Search Location").grid(column=0, row=4, columnspan=2, padx=5, pady=5)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(frame, width=50, textvariable=search_var)
    search_entry.grid(column=0, row=5, columnspan=2, pady=5)

    search_btn = ttk.Button(frame, text="Search", command=on_search)
    search_btn.grid(column=0, row=6, columnspan=2, padx=5, pady=5)

    # Listbox for search results
    ttk.Label(frame, text="Search Results").grid(column=0, row=7, columnspan=2, padx=5, pady=5)
    search_results_listbox = tk.Listbox(frame, height=10, width=80, exportselection=False)
    search_results_listbox.results = {}
    search_results_listbox.grid(column=0, row=8, columnspan=2, padx=5, pady=5)

    # Save and Close Button
    save_and_close_btn = ttk.Button(frame, text="Save & Close", command=on_save_and_close)
    save_and_close_btn.grid(column=0, row=9, columnspan=2, pady=10)

    locations_window.transient(root)
    locations_window.grab_set()


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
