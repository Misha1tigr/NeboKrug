import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from settings_manager import save_settings, load_settings, save_locations, extract_units
from api import search_location, get_historical_weather_data, get_forecast_data
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
import pandas as pd
from tkcalendar import DateEntry
color_cycle = ["red", "green", "blue", "yellow", "orange", "purple", "cyan", "magenta", "lime", "pink", "teal", "lavender", "brown", "beige", "maroon", "mint", "olive", "coral", "navy", "grey"]

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
        open_history_tab(history_frame)
        open_forecast_tab(forecast_frame)
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


def open_history_tab(master):
    def on_refresh():
        location = location_var.get()
        if not location:
            messagebox.showerror("Error", "Please select a location.")
            return

        start_date = start_date_var.get()
        end_date = end_date_var.get()
        if not start_date or not end_date:
            messagebox.showerror("Error", "Please select a date range.")
            return

        for loc in stored_locations_listbox.locations:
            if f"{loc['name']}, {loc['country']}" == location:
                selected_location = loc
                break
        else:
            selected_location = stored_locations_listbox.locations[0]
        latitude = selected_location['latitude']
        longitude = selected_location['longitude']

        # Extract units from settings
        temperature_unit, wind_speed_unit, precipitation_unit = extract_units()

        # Get historical weather data with units
        data = get_historical_weather_data(latitude, longitude, start_date, end_date, temperature_unit, wind_speed_unit,
                                           precipitation_unit)
        update_graph(data, temperature_unit, wind_speed_unit, precipitation_unit)

    def update_graph(data, temperature_unit, wind_speed_unit, precipitation_unit):
        fig.clear()

        selected_columns = []
        if temperature_max_var.get():
            selected_columns.append('temperature_2m_max')
        if temperature_min_var.get():
            selected_columns.append('temperature_2m_min')
        if temperature_mean_var.get():
            selected_columns.append('temperature_2m_mean')
        if daylight_duration_var.get():
            selected_columns.append('daylight_duration')
        if precipitation_var.get():
            selected_columns.append('precipitation_sum')
        if wind_speed_var.get():
            selected_columns.append('wind_speed_10m_max')

        if not selected_columns:
            messagebox.showerror("Error", "Please select at least one data type to display.")
            return

        # Convert date column to datetime
        data['date'] = pd.to_datetime(data['date'])

        # Adjust data frequency if too many points
        if len(data) > 100:
            data = data.iloc[::len(data) // 100, :]

        # Create the main axis
        ax = fig.add_subplot(111)

        color_index = 0

        ax_temp = None
        ax_precip = None
        ax_daylight = None
        ax_wind = None

        if 'temperature_2m_max' in selected_columns or 'temperature_2m_min' in selected_columns or 'temperature_2m_mean' in selected_columns:
            ax_temp = ax
            color_index += 1

        if 'precipitation_sum' in selected_columns:
            ax_precip = ax.twinx()
            ax_precip.spines['right'].set_position(('outward', 60))
            color_index += 1

        if 'daylight_duration' in selected_columns:
            ax_daylight = ax.twinx()
            ax_daylight.spines['right'].set_position(('outward', 120))
            color_index += 1

        if 'wind_speed_10m_max' in selected_columns:
            ax_wind = ax.twinx()
            ax_wind.spines['left'].set_position(('outward', 60))
            color_index += 1

        # Plot each selected column
        if 'temperature_2m_max' in selected_columns:
            ax_temp.plot(data['date'], data['temperature_2m_max'], label=f'Temperature Max ({temperature_unit})',
                         color=color_cycle[color_index])
            color_index += 1

        if 'temperature_2m_min' in selected_columns:
            ax_temp.plot(data['date'], data['temperature_2m_min'], label=f'Temperature Min ({temperature_unit})',
                         color=color_cycle[color_index])
            color_index += 1

        if 'temperature_2m_mean' in selected_columns:
            ax_temp.plot(data['date'], data['temperature_2m_mean'], label=f'Temperature Mean ({temperature_unit})',
                         color=color_cycle[color_index])
            color_index += 1

        if 'daylight_duration' in selected_columns:
            ax_daylight.plot(data['date'], data['daylight_duration'], label='Daylight Duration (seconds)',
                             color=color_cycle[color_index])
            color_index += 1

        if 'precipitation_sum' in selected_columns:
            ax_precip.bar(data['date'], data['precipitation_sum'], label=f'Precipitation ({precipitation_unit})',
                          color=color_cycle[color_index], alpha=0.5, width=1)
            color_index += 1

        if 'wind_speed_10m_max' in selected_columns:
            ax_wind.plot(data['date'], data['wind_speed_10m_max'], label=f'Wind Speed ({wind_speed_unit})',
                         color=color_cycle[color_index])
            color_index += 1

        # Set labels and legends
        ax.set_xlabel('Date')
        ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(plt.MaxNLocator(len(data['date']) // (len(data['date']) // 10)))

        if ax_temp:
            ax_temp.set_ylabel(f'Temperature ({temperature_unit})')
            ax_temp.legend(loc='upper left')

        if ax_precip:
            ax_precip.set_ylabel(f'Precipitation ({precipitation_unit})')
            ax_precip.legend(loc='upper right')

        if ax_daylight:
            ax_daylight.set_ylabel('Daylight Duration (hours)')
            ax_daylight.legend(loc='center right')

        if ax_wind:
            ax_wind.set_ylabel(f'Wind Speed ({wind_speed_unit})')
            ax_wind.legend(loc='lower right')

        # Remove the left spine if no temperature data is plotted there
        if not (temperature_max_var.get() or temperature_min_var.get() or temperature_mean_var.get()):
            ax.spines['left'].set_color('none')
            ax.tick_params(left=False, labelleft=False)

        fig.tight_layout()
        canvas.draw()

    for widget in master.winfo_children():
        widget.destroy()
    frame = ttk.Frame(master, padding="10")
    frame.pack(fill='both', expand=True)

    # Location selection combobox
    ttk.Label(frame, text="Location").grid(column=0, row=0, padx=5, pady=5)
    location_var = tk.StringVar()
    stored_locations_listbox = tk.Listbox(frame)
    stored_locations_listbox.locations = load_settings().get("locations", [])
    location_combobox = ttk.Combobox(frame, textvariable=location_var, state="readonly",
                                     values=[f"{loc['name']}, {loc['country']}" for loc in
                                             stored_locations_listbox.locations])
    location_combobox.grid(column=1, row=0, padx=5, pady=5)

    # Date selectors with DateEntry widgets from tkcalendar
    ttk.Label(frame, text="Start Date").grid(column=0, row=1, padx=5, pady=5)
    start_date_var = tk.StringVar(value="2024-01-01")
    start_date_entry = DateEntry(frame, textvariable=start_date_var, date_pattern='yyyy-mm-dd')
    start_date_entry.set_date("2024-01-01")
    start_date_entry.grid(column=1, row=1, padx=5, pady=5)

    ttk.Label(frame, text="End Date").grid(column=0, row=2, padx=5, pady=5)
    end_date_var = tk.StringVar(value="2024-02-01")
    end_date_entry = DateEntry(frame, textvariable=end_date_var, date_pattern='yyyy-mm-dd')
    end_date_entry.grid(column=1, row=2, padx=5, pady=5)

    # Checkboxes for data selection
    temperature_max_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Temperature Max", variable=temperature_max_var).grid(column=2, row=0, padx=5, pady=5)

    temperature_min_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Temperature Min", variable=temperature_min_var).grid(column=2, row=1, padx=5, pady=5)

    temperature_mean_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Temperature Mean", variable=temperature_mean_var).grid(column=2, row=2, padx=5, pady=5)

    daylight_duration_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Daylight Duration", variable=daylight_duration_var).grid(column=3, row=0, padx=5,
                                                                                          pady=5)

    precipitation_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Precipitation", variable=precipitation_var).grid(column=3, row=1, padx=5, pady=5)

    wind_speed_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Wind Speed", variable=wind_speed_var).grid(column=3, row=2, padx=5, pady=5)

    # Refresh button
    refresh_button = ttk.Button(frame, text="Refresh", command=on_refresh)
    refresh_button.grid(column=4, row=0, padx=5, pady=5, rowspan=3, sticky=tk.N + tk.S)

    # Canvas for the graph
    fig, ax = plt.subplots(figsize=(10, 5))
    canvas = FigureCanvasTkAgg(fig, master=frame)

    canvas.get_tk_widget().grid(column=0, row=3, columnspan=5, padx=5, pady=5)
    canvas.draw()


def open_forecast_tab(master):
    def on_refresh():
        location = location_var.get()
        if not location:
            messagebox.showerror("Error", "Please select a location.")
            return

        for loc in stored_locations_listbox.locations:
            if f"{loc['name']}, {loc['country']}" == location:
                selected_location = loc
                break
        else:
            selected_location = stored_locations_listbox.locations[0]
        latitude = selected_location['latitude']
        longitude = selected_location['longitude']

        # Extract units from settings
        temperature_unit, wind_speed_unit, precipitation_unit = extract_units()

        # Get forecast weather data with units
        data = get_forecast_data(latitude, longitude, temperature_unit, wind_speed_unit, precipitation_unit)
        update_graph(data, temperature_unit, wind_speed_unit, precipitation_unit)

    def update_graph(data, temperature_unit, wind_speed_unit, precipitation_unit):
        fig.clear()

        selected_columns = []
        if temperature_2m_var.get():
            selected_columns.append('temperature_2m')
        if relative_humidity_var.get():
            selected_columns.append('relative_humidity_2m')
        if apparent_temperature_var.get():
            selected_columns.append('apparent_temperature')
        if precipitation_probability_var.get():
            selected_columns.append('precipitation_probability')
        if precipitation_var.get():
            selected_columns.append('precipitation')
        if surface_pressure_var.get():
            selected_columns.append('surface_pressure')
        if visibility_var.get():
            selected_columns.append('visibility')
        if wind_speed_var.get():
            selected_columns.append('wind_speed_10m')
        if uv_index_var.get():
            selected_columns.append('uv_index')

        if not selected_columns:
            messagebox.showerror("Error", "Please select at least one data type to display.")
            return

        # Convert date column to datetime
        data['date'] = pd.to_datetime(data['date'])

        # Shorten the data according to slider value
        forecast_days = int(forecast_slider.get())
        data = data.iloc[:forecast_days * 24, :]  # 24 hours in a day

        # Adjust data frequency if too many points
        if len(data) > 100:
            data = data.iloc[::len(data) // 100, :]

        # Create the main axis
        ax = fig.add_subplot(111)

        color_index = 0

        ax_temp = None
        ax_precip = None
        ax_visibility = None
        ax_wind = None

        if 'temperature_2m' in selected_columns or 'apparent_temperature' in selected_columns:
            ax_temp = ax
            color_index += 1

        if 'precipitation' in selected_columns or 'precipitation_probability' in selected_columns:
            ax_precip = ax.twinx()
            ax_precip.spines['right'].set_position(('outward', 60))
            color_index += 1

        if 'visibility' in selected_columns:
            ax_visibility = ax.twinx()
            ax_visibility.spines['right'].set_position(('outward', 120))
            color_index += 1

        if 'wind_speed_10m' in selected_columns:
            ax_wind = ax.twinx()
            ax_wind.spines['left'].set_position(('outward', 60))
            color_index += 1

        # Plot each selected column
        for col in selected_columns:
            if col == 'temperature_2m':
                ax_temp.plot(data['date'], data['temperature_2m'], label=f'Temperature 2m ({temperature_unit})',
                             color=color_cycle[color_index])
            elif col == 'relative_humidity_2m':
                ax.plot(data['date'], data['relative_humidity_2m'], label='Relative Humidity 2m (%)',
                        color=color_cycle[color_index])
            elif col == 'apparent_temperature':
                ax_temp.plot(data['date'], data['apparent_temperature'],
                             label=f'Apparent Temperature ({temperature_unit})', color=color_cycle[color_index])
            elif col == 'precipitation_probability':
                ax_precip.plot(data['date'], data['precipitation_probability'], label='Precipitation Probability (%)',
                               color=color_cycle[color_index])
            elif col == 'precipitation':
                ax_precip.bar(data['date'], data['precipitation'], label=f'Precipitation ({precipitation_unit})',
                              color=color_cycle[color_index], alpha=0.5, width=1)
            elif col == 'surface_pressure':
                ax.plot(data['date'], data['surface_pressure'], label='Surface Pressure (hPa)',
                        color=color_cycle[color_index])
            elif col == 'visibility':
                ax_visibility.plot(data['date'], data['visibility'], label='Visibility (km)',
                                   color=color_cycle[color_index])
            elif col == 'wind_speed_10m':
                ax_wind.plot(data['date'], data['wind_speed_10m'], label=f'Wind Speed ({wind_speed_unit})',
                             color=color_cycle[color_index])
            elif col == 'uv_index':
                ax.plot(data['date'], data['uv_index'], label='UV Index', color=color_cycle[color_index])

            color_index += 1

        # Set labels and legends
        ax.set_xlabel('Date')
        ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(plt.MaxNLocator(len(data['date']) // (len(data['date']) // 10)))

        if ax_temp:
            ax_temp.set_ylabel(f'Temperature ({temperature_unit})')
            ax_temp.legend(loc='upper left')

        if ax_precip:
            ax_precip.set_ylabel(f'Precipitation ({precipitation_unit})')
            ax_precip.legend(loc='upper right')

        if ax_visibility:
            ax_visibility.set_ylabel('Visibility (km)')
            ax_visibility.legend(loc='center right')

        if ax_wind:
            ax_wind.set_ylabel(f'Wind Speed ({wind_speed_unit})')
            ax_wind.legend(loc='lower right')

        # Remove the left spine if no temperature data is plotted there
        if not temperature_2m_var.get() and not apparent_temperature_var.get():
            ax.spines['left'].set_color('none')
            ax.tick_params(left=False, labelleft=False)

        fig.tight_layout()
        canvas.draw()

    for widget in master.winfo_children():
        widget.destroy()
    frame = ttk.Frame(master, padding="10")
    frame.pack(fill='both', expand=True)

    # Location selection combobox
    ttk.Label(frame, text="Location").grid(column=0, row=0, padx=5, pady=5)
    location_var = tk.StringVar()
    stored_locations_listbox = tk.Listbox(frame)
    stored_locations_listbox.locations = load_settings().get("locations", [])
    location_combobox = ttk.Combobox(frame, textvariable=location_var, state="readonly",
                                     values=[f"{loc['name']}, {loc['country']}" for loc in
                                             stored_locations_listbox.locations])
    location_combobox.grid(column=1, row=0, padx=5, pady=5)

    # Checkboxes for data selection
    temperature_2m_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Temperature 2m", variable=temperature_2m_var).grid(column=2, row=0, padx=5, pady=5)

    relative_humidity_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Relative Humidity 2m", variable=relative_humidity_var).grid(column=2, row=1, padx=5,
                                                                                             pady=5)

    apparent_temperature_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Apparent Temperature", variable=apparent_temperature_var).grid(column=2, row=2, padx=5,
                                                                                                pady=5)

    precipitation_probability_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Precipitation Probability", variable=precipitation_probability_var).grid(column=3,
                                                                                                          row=0, padx=5,
                                                                                                          pady=5)

    precipitation_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Precipitation", variable=precipitation_var).grid(column=3, row=1, padx=5, pady=5)

    surface_pressure_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Surface Pressure", variable=surface_pressure_var).grid(column=3, row=2, padx=5, pady=5)

    visibility_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Visibility", variable=visibility_var).grid(column=4, row=0, padx=5, pady=5)

    wind_speed_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Wind Speed", variable=wind_speed_var).grid(column=4, row=1, padx=5, pady=5)

    uv_index_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="UV Index", variable=uv_index_var).grid(column=4, row=2, padx=5, pady=5)

    # Refresh button
    refresh_button = ttk.Button(frame, text="Refresh", command=on_refresh)
    refresh_button.grid(column=5, row=0, padx=5, pady=5, rowspan=3, sticky=tk.N + tk.S)

    # Canvas for the graph
    fig, ax = plt.subplots(figsize=(10, 5))
    canvas = FigureCanvasTkAgg(fig, master=frame)

    canvas.get_tk_widget().grid(column=0, row=3, columnspan=6, pady=5)
    canvas.draw()

    # Slider for adjusting forecast days
    ttk.Label(frame, text="Forecast Days").grid(column=0, row=4, padx=5, pady=5)
    forecast_slider = ttk.Scale(frame, from_=1, to=14, orient='horizontal', length=400)
    forecast_slider.set(14)
    forecast_slider.grid(column=1, row=4, columnspan=5, pady=5)


def create_tabs(root):
    global history_frame, forecast_frame
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # Forecast Tab
    forecast_frame = ttk.Frame(notebook, padding="10")
    open_forecast_tab(forecast_frame)
    notebook.add(forecast_frame, text="Forecast")

    # Forecast AI Tab
    forecast_ai_frame = ttk.Frame(notebook, padding="10")
    ttk.Label(forecast_ai_frame, text="Sample text for Forecast AI").pack()
    notebook.add(forecast_ai_frame, text="Forecast AI")

    # History Tab
    history_frame = ttk.Frame(notebook, padding="10")
    open_history_tab(history_frame)
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
