import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from settings_manager import load_settings, extract_units
from api import get_historical_weather_data, get_forecast_data, get_clothing_recommendations, \
    compare_todays_data, get_history_of_date
from settings_windows import settings_units_window, settings_locations_window, settings_misc_window
from info_windows import open_about_window, open_feedback_window, open_help_window
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
import pandas as pd
from tkcalendar import DateEntry
from urllib import request
import sys
import threading
import time
import random
import gettext
import traceback
selected_locale = load_settings().get("locale", "ua")
text_object = gettext.translation('main', localedir='../locales', languages=[selected_locale])
text_object.install()
_ = text_object.gettext

color_cycle = ["red", "green", "blue", "yellow", "orange", "purple", "cyan", "magenta", "lime", "pink", "teal",
               "lavender", "brown", "beige", "maroon", "mint", "olive", "coral", "navy", "grey"]


def create_menu_bar(root):
    """
    Creates the menu bar for the main application window.
    """
    menubar = tk.Menu(root)

    # Units of Measurement
    menubar.add_command(label=_("Units of Measurement"), command=lambda: settings_units_window(root))

    # Your Locations
    # Creates a list of functions to call when the location list is updated
    function_list_with_params = [
        (open_history_tab, (history_frame,)),
        (open_forecast_tab, (forecast_frame,)),
        (open_clothing_recommendations_tab, (forecast_ai_frame,)),
        (open_day_in_history_tab, (this_day_history_frame,))
    ]
    menubar.add_command(label=_("Your Locations"), command=lambda: settings_locations_window(root,
                                                                                             function_list_with_params))

    # Other Settings
    menubar.add_command(label=_("Other Settings"), command=lambda: settings_misc_window(root))

    # Info Menu
    info_menu = tk.Menu(menubar, tearoff=0)
    info_menu.add_command(label=_("Help"), command=lambda: open_help_window())
    info_menu.add_command(label=_("Feedback"), command=lambda: open_feedback_window())
    info_menu.add_command(label=_("About"), command=lambda: open_about_window())
    menubar.add_cascade(label=_("Info"), menu=info_menu)

    # Exit
    menubar.add_command(label=_("Exit"), command=root.quit)

    root.config(menu=menubar)


def open_history_tab(master):
    """
    Opens the History tab in the main application.
    """

    def on_refresh():
        location = location_var.get()
        if not location:
            messagebox.showerror(_("Error"), _("Please select a location."))
            return

        start_date = start_date_var.get()
        end_date = end_date_var.get()
        if not start_date or not end_date:
            messagebox.showerror(_("Error"), _("Please select a date range."))
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
            messagebox.showerror(_("Error"), _("Please select at least one data type to display."))
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

        if ('temperature_2m_max' in selected_columns or 'temperature_2m_min' in selected_columns
                or 'temperature_2m_mean' in selected_columns):
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
            ax_temp.plot(data['date'], data['temperature_2m_max'],
                         label=_("Temperature Max (") + f"{temperature_unit})",
                         color=color_cycle[color_index])
            color_index += 1

        if 'temperature_2m_min' in selected_columns:
            ax_temp.plot(data['date'], data['temperature_2m_min'],
                         label=_("Temperature Min (") + f"{temperature_unit})",
                         color=color_cycle[color_index])
            color_index += 1

        if 'temperature_2m_mean' in selected_columns:
            ax_temp.plot(data['date'], data['temperature_2m_mean'],
                         label=_("Temperature Mean (") + f"{temperature_unit})",
                         color=color_cycle[color_index])
            color_index += 1

        if 'daylight_duration' in selected_columns:
            ax_daylight.plot(data['date'], data['daylight_duration'], label=_("Daylight Duration (seconds)"),
                             color=color_cycle[color_index])
            color_index += 1

        if 'precipitation_sum' in selected_columns:
            ax_precip.bar(data['date'], data['precipitation_sum'],
                          label=_("Precipitation (") + f"{precipitation_unit})",
                          color=color_cycle[color_index], alpha=0.5, width=1)
            color_index += 1

        if 'wind_speed_10m_max' in selected_columns:
            ax_wind.plot(data['date'], data['wind_speed_10m_max'], label=_("Wind Speed (") + f"{wind_speed_unit})",
                         color=color_cycle[color_index])
            color_index += 1

        # Set labels and legends
        ax.set_xlabel(_("Date"))
        ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(plt.MaxNLocator(len(data['date']) // (len(data['date']) // 10)))

        if ax_temp:
            ax_temp.set_ylabel(_("Temperature (") + f"{temperature_unit})")
            ax_temp.legend(loc='upper left')

        if ax_precip:
            ax_precip.set_ylabel(_("Precipitation (") + f"{precipitation_unit})")
            ax_precip.legend(loc='upper right')

        if ax_daylight:
            ax_daylight.set_ylabel(_("Daylight Duration (seconds)"))
            ax_daylight.legend(loc='lower left')

        if ax_wind:
            ax_wind.set_ylabel(_("Wind Speed (") + f"{wind_speed_unit})")
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
    ttk.Label(frame, text=_("Location")).grid(column=0, row=0, padx=5, pady=5)
    location_var = tk.StringVar()
    stored_locations_listbox = tk.Listbox(frame)
    stored_locations_listbox.locations = load_settings().get("locations", [])
    location_combobox = ttk.Combobox(frame, textvariable=location_var, state="readonly",
                                     values=[f"{loc['name']}, {loc['country']}" for loc in
                                             stored_locations_listbox.locations])
    location_combobox.grid(column=1, row=0, padx=5, pady=5)

    if stored_locations_listbox.locations:
        location_combobox.current(0)  # Select the first location by default

    # Date selectors with DateEntry widgets from tkcalendar
    ttk.Label(frame, text=_("Start Date")).grid(column=0, row=1, padx=5, pady=5)
    start_date_var = tk.StringVar(value="2024-01-01")
    start_date_entry = DateEntry(frame, textvariable=start_date_var, date_pattern='yyyy-mm-dd')
    start_date_entry.set_date("2024-01-01")
    start_date_entry.grid(column=1, row=1, padx=5, pady=5)

    ttk.Label(frame, text=_("End Date")).grid(column=0, row=2, padx=5, pady=5)
    end_date_var = tk.StringVar(value="2024-02-01")
    end_date_entry = DateEntry(frame, textvariable=end_date_var, date_pattern='yyyy-mm-dd')
    end_date_entry.grid(column=1, row=2, padx=5, pady=5)

    # Checkboxes for data selection
    temperature_max_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text=_("Temperature Max"), variable=temperature_max_var).grid(column=2, row=0, padx=5,
                                                                                         pady=5)

    temperature_min_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text=_("Temperature Min"), variable=temperature_min_var).grid(column=2, row=1, padx=5,
                                                                                         pady=5)

    temperature_mean_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text=_("Temperature Mean"), variable=temperature_mean_var).grid(column=2, row=2, padx=5,
                                                                                           pady=5)

    daylight_duration_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text=_("Daylight Duration"), variable=daylight_duration_var).grid(column=3, row=0, padx=5,
                                                                                             pady=5)

    precipitation_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text=_("Precipitation"), variable=precipitation_var).grid(column=3, row=1, padx=5, pady=5)

    wind_speed_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text=_("Wind Speed"), variable=wind_speed_var).grid(column=3, row=2, padx=5, pady=5)

    # Refresh button
    refresh_button = ttk.Button(frame, text=_("Refresh"), command=on_refresh)
    refresh_button.grid(column=4, row=0, padx=5, pady=5, rowspan=3, sticky=tk.N + tk.S)

    # Canvas for the graph
    fig, ax = plt.subplots(figsize=(10, 5))
    canvas = FigureCanvasTkAgg(fig, master=frame)

    canvas.get_tk_widget().grid(column=0, row=3, columnspan=5, padx=5, pady=5)
    canvas.draw()


def open_forecast_tab(master):
    """
    Opens the Forecast tab in the main application.
    """

    def on_refresh(fetch_new_data=True):
        location = location_var.get()
        if not location:
            messagebox.showerror(_("Error"), _("Please select a location."))
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

        # Get forecast weather data with units only once
        if fetch_new_data:
            global forecast_data  # Store the forecast data globally to avoid repeated API calls
            forecast_data = get_forecast_data(latitude, longitude, temperature_unit, wind_speed_unit,
                                              precipitation_unit)
        else:
            try:
                # noinspection PyUnboundLocalVariable
                forecast_data
            except NameError:
                return
        update_graph(forecast_data, temperature_unit, wind_speed_unit, precipitation_unit)

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
            messagebox.showerror(_("Error"), _("Please select at least one data type to display."))
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
        axis_map = {}
        legend_handles = []

        def get_or_create_axis(key, position, side):
            """
             Function to get or create a new axis for plotting.
             """
            if key not in axis_map:
                new_ax = ax.twinx() if side == 'right' else ax.twinx()
                new_ax.spines[side].set_position(('outward', position))
                axis_map[key] = new_ax
            return axis_map[key]

        # Plot each selected column
        axis_position = 0
        show_primary_axis = False
        for col in selected_columns:
            if col == 'temperature_2m':
                line, = ax.plot(data['date'], data['temperature_2m'], label=_("Temperature"),
                                color=color_cycle[color_index])
                legend_handles.append(line)
                show_primary_axis = True
                ax.set_ylabel(_("Temperature (") + f"{temperature_unit})")
                axis_position -= 60
            elif col == 'relative_humidity_2m':
                rh_ax = get_or_create_axis('Relative Humidity', axis_position, 'left')
                line, = rh_ax.plot(data['date'], data['relative_humidity_2m'], label=_("Relative Humidity"),
                                   color=color_cycle[color_index])
                legend_handles.append(line)
                rh_ax.set_ylabel(_("Relative Humidity (%)"))
            elif col == 'apparent_temperature':
                line, = ax.plot(data['date'], data['apparent_temperature'], label=_("Apparent Temperature"),
                                color=color_cycle[color_index])
                legend_handles.append(line)
                show_primary_axis = True
                ax.set_ylabel(_("Apparent Temperature (") + f"{temperature_unit})")
                axis_position -= 60
            elif col == 'precipitation_probability':
                pp_ax = get_or_create_axis('Precipitation Probability', axis_position, 'right')
                line, = pp_ax.plot(data['date'], data['precipitation_probability'],
                                   label=_("Precipitation Probability"),
                                   color=color_cycle[color_index])
                legend_handles.append(line)
                pp_ax.set_ylabel(_("Precipitation Probability (%)"))
            elif col == 'precipitation':
                precip_ax = get_or_create_axis('Precipitation', axis_position, 'right')
                bar = precip_ax.bar(data['date'], data['precipitation'], label=_("Precipitation"),
                                    color=color_cycle[color_index], alpha=0.5, width=0.13)
                legend_handles.append(bar)
                precip_ax.set_ylabel(_("Precipitation (") + f"{precipitation_unit})")
            elif col == 'surface_pressure':
                sp_ax = get_or_create_axis('Surface Pressure', axis_position, 'right')
                line, = sp_ax.plot(data['date'], data['surface_pressure'], label=_("Surface Pressure"),
                                   color=color_cycle[color_index])
                legend_handles.append(line)
                sp_ax.set_ylabel(_("Surface Pressure (hPa)"))
            elif col == 'visibility':
                vis_ax = get_or_create_axis('Visibility', axis_position, 'right')
                line, = vis_ax.plot(data['date'], data['visibility'], label=_("Visibility"),
                                    color=color_cycle[color_index])
                legend_handles.append(line)
                vis_ax.set_ylabel(_("Visibility (m)"))
            elif col == 'wind_speed_10m':
                ws_ax = get_or_create_axis('Wind Speed', axis_position, 'right')
                line, = ws_ax.plot(data['date'], data['wind_speed_10m'], label=_("Wind Speed"),
                                   color=color_cycle[color_index])
                legend_handles.append(line)
                ws_ax.set_ylabel(_("Wind Speed (") + f"{wind_speed_unit})")
            elif col == 'uv_index':
                uv_ax = get_or_create_axis('UV Index', axis_position, 'right')
                line, = uv_ax.plot(data['date'], data['uv_index'], label=_("UV Index"), color=color_cycle[color_index])
                legend_handles.append(line)
                uv_ax.set_ylabel(_("UV Index"))
            color_index += 1
            axis_position += 60

        # Always set up the x-axis
        ax.set_xlabel(_("Date"))
        ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(plt.MaxNLocator(len(data['date']) // (len(data['date']) // 8)))

        # Set legends
        ax.legend(handles=legend_handles, loc='upper right')
        if not show_primary_axis:
            ax.yaxis.set_visible(False)

        fig.tight_layout()
        canvas.draw()

    # Clear all previous widgets
    for widget in master.winfo_children():
        widget.destroy()
    frame = ttk.Frame(master, padding="10")
    frame.pack(fill='both', expand=True)

    # Location selection combobox
    ttk.Label(frame, text=_("Location")).grid(column=0, row=0, padx=5, pady=5)
    location_var = tk.StringVar()
    stored_locations_listbox = tk.Listbox(frame)
    stored_locations_listbox.locations = load_settings().get("locations", [])
    location_combobox = ttk.Combobox(frame, textvariable=location_var, state="readonly",
                                     values=[f"{loc['name']}, {loc['country']}" for loc in
                                             stored_locations_listbox.locations])
    location_combobox.grid(column=1, row=0, padx=5, pady=5)

    if stored_locations_listbox.locations:
        location_combobox.current(0)  # Select the first location by default

    # Checkboxes for data selection
    temperature_2m_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text=_("Temperature"), variable=temperature_2m_var).grid(column=2, row=0, padx=5, pady=5)

    relative_humidity_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text=_("Relative Humidity"), variable=relative_humidity_var).grid(column=2, row=1, padx=5,
                                                                                             pady=5)

    apparent_temperature_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text=_("Apparent Temperature"), variable=apparent_temperature_var).grid(column=2, row=2,
                                                                                                   padx=5,
                                                                                                   pady=5)

    precipitation_probability_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text=_("Precipitation Probability"), variable=precipitation_probability_var).grid(column=3,
                                                                                                             row=0,
                                                                                                             padx=5,
                                                                                                             pady=5)

    precipitation_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text=_("Precipitation"), variable=precipitation_var).grid(column=3, row=1, padx=5, pady=5)

    surface_pressure_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text=_("Surface Pressure"), variable=surface_pressure_var).grid(column=3, row=2, padx=5,
                                                                                           pady=5)

    visibility_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text=_("Visibility"), variable=visibility_var).grid(column=4, row=0, padx=5, pady=5)

    wind_speed_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text=_("Wind Speed"), variable=wind_speed_var).grid(column=4, row=1, padx=5, pady=5)

    uv_index_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text=_("UV Index"), variable=uv_index_var).grid(column=4, row=2, padx=5, pady=5)

    # Refresh button
    refresh_button = ttk.Button(frame, text=_("Refresh"), command=lambda: on_refresh(fetch_new_data=True))
    refresh_button.grid(column=5, row=0, padx=5, pady=5, rowspan=3, sticky=tk.N + tk.S)

    # Canvas for the graph
    fig, ax = plt.subplots(figsize=(10, 5))
    canvas = FigureCanvasTkAgg(fig, master=frame)

    canvas.get_tk_widget().grid(column=0, row=3, columnspan=6, pady=5)
    canvas.draw()

    # Slider for adjusting forecast days
    ttk.Label(frame, text=_("Forecast Days")).grid(column=0, row=4, padx=5, pady=5)
    forecast_slider = ttk.Scale(frame, from_=1, to=14, value=14, orient='horizontal', length=400,
                                command=lambda a: on_refresh(fetch_new_data=False))
    forecast_slider.grid(column=1, row=4, columnspan=5, pady=5)


def loading_animation(flag, loading_label):
    """
    Runs a loading animation within the given label
    """
    flag.clear()
    animation_symbols = ['|', '/', '–', '\\']
    i = 0
    while not flag.is_set():
        loading_label.config(text=_("Loading") + f"{animation_symbols[i % len(animation_symbols)]}")
        i += 1
        time.sleep(0.1)
    loading_label.config(text="")  # Clear the loading text once done


def open_clothing_recommendations_tab(frame, load_default = False):
    """
    Opens the Clothing Recommendations tab in the main application.
    """
    # Clear the parent frame
    for widget in frame.winfo_children():
        widget.destroy()

    # Configure the grid
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)
    frame.grid_columnconfigure(2, weight=1)

    # Add label for the frame
    frame_label = ttk.Label(frame, text=_("Clothing Recommendations"), font=("Helvetica", 16, "bold"))
    frame_label.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky='n')

    def on_refresh():
        location = location_var.get()
        if not location:
            messagebox.showerror(_("Error"), _("Please select a location."))
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

        # Start the loading animation in a separate thread
        loading_thread = threading.Thread(target=loading_animation, args=(stop_loading, loading_label), daemon=True)
        loading_thread.start()

        # Get clothing recommendations in a separate thread
        recommendations_thread = threading.Thread(target=get_recommendations, args=(
            latitude, longitude, temperature_unit, wind_speed_unit, precipitation_unit), daemon=True)
        recommendations_thread.start()

    def get_recommendations(latitude, longitude, temperature_unit, wind_speed_unit, precipitation_unit):
        recommendations = get_clothing_recommendations(latitude, longitude, temperature_unit, wind_speed_unit,
                                                       precipitation_unit)
        recommendation_label.config(text=recommendations, font=("Helvetica", 12))
        stop_loading.set()  # Signal to stop the loading animation

    stop_loading = threading.Event()

    # Location selection combobox
    ttk.Label(frame, text=_("Location")).grid(column=0, row=1, padx=5, pady=5, sticky='e')
    location_var = tk.StringVar()
    stored_locations_listbox = tk.Listbox(frame)
    stored_locations_listbox.locations = load_settings().get("locations", [])
    location_combobox = ttk.Combobox(frame, textvariable=location_var, state="readonly",
                                     values=[f"{loc['name']}, {loc['country']}" for loc in
                                             stored_locations_listbox.locations])
    location_combobox.grid(column=1, row=1, padx=5, pady=5, sticky='ew')

    if stored_locations_listbox.locations:
        location_combobox.current(0)  # Select the first location by default

    # Refresh button
    refresh_button = ttk.Button(frame, text=_("Refresh"), command=on_refresh)
    refresh_button.grid(column=2, row=1, padx=5, pady=5, sticky='w')

    # Label to display the loading animation
    loading_label = ttk.Label(frame, text="", font=("Helvetica", 12))
    loading_label.grid(column=0, row=10, columnspan=3, padx=5, pady=5, sticky='s')

    # Label to display the clothing recommendations
    recommendation_label = ttk.Label(frame, text="", wraplength=400, justify="center")
    recommendation_label.grid(column=0, row=3, columnspan=3, padx=5, pady=20, sticky='n')
    if load_default and location_var.get():
        on_refresh()

def display_weather_facts(frame):
    """
    Displays weather fun facts in the Fun Facts tab.
    """

    def get_random_fact(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            facts = file.readlines()
        return random.choice(facts).strip().replace('\\n', '\n')

    def get_fact_and_title(file_path):
        fact = get_random_fact(file_path)
        title, fact = fact.split('|', 1)
        return title.strip().replace('\\n', '\n'), fact.strip().replace('\\n', '\n')

    def update_button_text(button, file_path, get_title=False):
        if get_title:
            title, fact = get_fact_and_title(file_path)
            button.config(text=f"{title}\n\n{fact}")
        else:
            fact = get_random_fact(file_path)
            button.config(text=fact)

    # Create the container for the tiles
    for i in range(2):
        frame.columnconfigure(i, weight=1, minsize=150)
        frame.rowconfigure(i + 1, weight=1, minsize=100)

    if selected_locale == 'en':
        long_file = './fun_facts/long1_en.txt'
        mid_file = './fun_facts/mid1_en.txt'
        short_file1 = './fun_facts/short1_en.txt'
        short_file2 = './fun_facts/short2_en.txt'
    else:
        long_file = './fun_facts/long1_ua.txt'
        mid_file = './fun_facts/mid1_ua.txt'
        short_file1 = './fun_facts/short1_ua.txt'
        short_file2 = './fun_facts/short2_ua.txt'

    ttk.Label(frame, text=_("Weather fun facts just for you"), font="bold").grid(column=0, row=0, padx=5, pady=5,
                                                                                 columnspan=2)
    # Create buttons and place them in the grid
    long_title, long_fact = get_fact_and_title(long_file)
    button1 = tk.Button(frame, text=f"{long_title}\n\n{long_fact}", wraplength=300, relief="ridge",
                        command=lambda: update_button_text(button1, long_file, get_title=True), takefocus=0)
    button1.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    mid_title, mid_fact = get_fact_and_title(mid_file)
    button2 = tk.Button(frame, text=f"{mid_title}\n\n{mid_fact}", wraplength=300, relief="ridge",
                        command=lambda: update_button_text(button2, mid_file, get_title=True), takefocus=0)
    button2.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

    short_fact1 = get_random_fact(short_file1)
    button3 = tk.Button(frame, text=short_fact1, wraplength=300, relief="ridge",
                        command=lambda: update_button_text(button3, short_file1), takefocus=0)
    button3.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

    short_fact2 = get_random_fact(short_file2)
    button4 = tk.Button(frame, text=short_fact2, wraplength=300, relief="ridge",
                        command=lambda: update_button_text(button4, short_file2), takefocus=0)
    button4.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)


def open_day_in_history_tab(frame, load_default = False):
    """
    Generates the "This Day in History" tab in the main application.
    """
    # Clear the parent frame
    for widget in frame.winfo_children():
        widget.destroy()

    # Configure the grid
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)
    frame.grid_columnconfigure(2, weight=1)

    # Add label for the frame
    frame_label = ttk.Label(frame, text=_("What is today like, compared to previous years?"),
                            font=("Helvetica", 16, "bold"))
    frame_label.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky='n')

    def on_refresh():
        location = location_var.get()
        if not location:
            messagebox.showerror(_("Error"), _("Please select a location."))
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

        # Start the loading animation in a separate thread
        loading_thread = threading.Thread(target=loading_animation, args=(stop_loading, loading_label), daemon=True)
        loading_thread.start()

        # Get clothing recommendations in a separate thread
        recommendations_thread = threading.Thread(target=load_data, args=(
            latitude, longitude, temperature_unit, wind_speed_unit, precipitation_unit), daemon=True)
        recommendations_thread.start()

    def load_data(latitude, longitude, temperature_unit, wind_speed_unit, precipitation_unit):
        data_today, data_before = get_history_of_date(latitude, longitude, temperature_unit, wind_speed_unit,
                                                      precipitation_unit)
        text_analisys = compare_todays_data(data_today, data_before)
        recommendation_label.config(text=text_analisys, font=("Helvetica", 12))
        stop_loading.set()  # Signal to stop the loading animation

    stop_loading = threading.Event()

    # Location selection combobox
    ttk.Label(frame, text=_("Location")).grid(column=0, row=1, padx=5, pady=5, sticky='e')
    location_var = tk.StringVar()
    stored_locations_listbox = tk.Listbox(frame)
    stored_locations_listbox.locations = load_settings().get("locations", [])
    location_combobox = ttk.Combobox(frame, textvariable=location_var, state="readonly",
                                     values=[f"{loc['name']}, {loc['country']}" for loc in
                                             stored_locations_listbox.locations])
    location_combobox.grid(column=1, row=1, padx=5, pady=5, sticky='ew')

    if stored_locations_listbox.locations:
        location_combobox.current(0)  # Select the first location by default

    # Refresh button
    refresh_button = ttk.Button(frame, text=_("Refresh"), command=on_refresh)
    refresh_button.grid(column=2, row=1, padx=5, pady=5, sticky='w')

    # Label to display the loading animation
    loading_label = ttk.Label(frame, text="", font=("Helvetica", 12))
    loading_label.grid(column=0, row=10, columnspan=3, padx=5, pady=5, sticky='s')

    # Label to display the clothing recommendations
    recommendation_label = ttk.Label(frame, text="", wraplength=400, justify="center")
    recommendation_label.grid(column=0, row=3, columnspan=3, padx=5, pady=20, sticky='n')

    if load_default and location_var.get():
        on_refresh()

def update_label(flag, loading_text):
    """
    Updates the loading animation label.
    """
    i = 0
    while flag.is_set():
        loading_text.configure(text=(_("Loading") + "." * i))
        i += 1
        if i >= 10:
            i = 0
        time.sleep(0.1)
    loading_text.master.master.grab_release()
    loading_text.master.master.destroy()

def mainwindow_loading_animation(flag):
    """Opens a loading window."""
    flag.set()
    window = tk.Tk()
    window.title(_("Loading"))
    window.geometry("200x50")
    window.grab_set()
    window.attributes("-toolwindow", True)
    frame = ttk.Frame(window, padding="10")
    frame.pack(fill='both', expand=True)

    loading_text = ttk.Label(frame, text=".", justify="center", font="bold")
    loading_text.grid(column=0, row=0, padx=5, pady=5)

    # Run update_label in a separate thread
    threading.Thread(target=update_label, args=(flag, loading_text), daemon=True).start()

    window.mainloop()

def create_tabs(root):
    """
    Creates tabs and their contents
    """
    global history_frame, forecast_frame, forecast_ai_frame, this_day_history_frame
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # Forecast Tab
    forecast_frame = ttk.Frame(notebook, padding="10")
    open_forecast_tab(forecast_frame)
    notebook.add(forecast_frame, text=_("Forecast"))

    # Clothing recommendations Tab
    forecast_ai_frame = ttk.Frame(notebook, padding="10")
    open_clothing_recommendations_tab(forecast_ai_frame, True)
    notebook.add(forecast_ai_frame, text=_("AI Recommendations"))

    # History Tab
    history_frame = ttk.Frame(notebook, padding="10")
    open_history_tab(history_frame)
    notebook.add(history_frame, text=_("History"))

    # This day in history Tab
    this_day_history_frame = ttk.Frame(notebook, padding="10")
    open_day_in_history_tab(this_day_history_frame, True)
    notebook.add(this_day_history_frame, text=_("This day in history"))

    # Fun fact Tab
    fun_fact_frame = ttk.Frame(notebook, padding="10")
    display_weather_facts(fun_fact_frame)
    notebook.add(fun_fact_frame, text=_("Fun fact"))

def test_connection():
    """
    Checks if the internet connection is working.
    """
    try:
        request.urlopen('https://api.open-meteo.com/v1/forecast?latitude=1&longitude=1&daily=weather_code'
                        '&forecast_days=1', timeout=1)
        return True
    except:
        return False


def custom_tkinter_exception_handler(exc_type, exc_value, exc_traceback):
    """
    This function is called when an uncaught exception occurs.
    """
    error_message = _("Sorry, an exception has occurred.\nPlease report this exception to the developer\n\n")
    error_message += ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    messagebox.showerror(_("Error"), error_message)

def initialize_main_window():
    """
    Initializes the main window.
    """
    root = tk.Tk()
    root.title(_("NeboKrug"))
    root.report_callback_exception = custom_tkinter_exception_handler
    main_loading_flag = threading.Event()
    main_loading_animation_thread = threading.Thread(target=mainwindow_loading_animation, args=(main_loading_flag,), daemon=True)
    main_loading_animation_thread.start()
    if not test_connection() and False:
        main_loading_flag.clear()
        messagebox.showerror(_("Error"), _("Check your internet connection."))
        root.destroy()
        sys.exit(1)
    create_tabs(root)
    create_menu_bar(root)
    main_loading_flag.clear()
    root.focus_force()
    root.mainloop()

if __name__ == "__main__":
    initialize_main_window()