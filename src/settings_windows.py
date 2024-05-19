import tkinter as tk
from tkinter import ttk
from settings_manager import save_settings, load_settings, save_locations
from api import search_location
import os
import sys
import gettext

selected_locale = load_settings().get("locale", "ua")
text_object = gettext.translation('settings', localedir='../locales', languages=[selected_locale])
text_object.install()
_ = text_object.gettext

def settings_misc_window(root):
    """
    Opens the Miscellaneous Settings window.
    """

    def on_save_and_close():
        settings["locale"] = "en" if language_selected_option.get() == "English" else "ua"
        save_settings(settings)  # Save the settings to a JSON file
        settings_window.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv) # Restart the app

    settings = load_settings()  # Load settings from the JSON file

    settings_window = tk.Toplevel()
    settings_window.title(_("Miscellaneous Settings"))
    settings_window.protocol("WM_DELETE_WINDOW", on_save_and_close)

    frame = ttk.Frame(settings_window, padding="10")
    frame.pack(fill='both', expand=True)

    # Language Selection
    ttk.Label(frame, text=_("App Language")).grid(column=0, row=0, padx=5, pady=5)
    language_options = ["English", "Українська"]
    language_selected_option = tk.StringVar()
    language_selected_option.set("English" if settings.get("locale", "en") == "en" else "Українська")
    language_dropdown = ttk.Combobox(frame, textvariable=language_selected_option,
                                     values=language_options, state="readonly")
    language_dropdown.grid(column=1, row=0, padx=5, pady=5)

    # Save and Close Button
    save_and_close_btn = ttk.Button(frame, text=_("Save & Restart"), command=on_save_and_close)
    save_and_close_btn.grid(column=0, row=1, columnspan=2, pady=10)

    settings_window.transient(root)
    settings_window.grab_set()


def settings_units_window(root):
    """
    Opens the Units of Measurement Settings window.
    """

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
    settings_window.title(_("Units of Measurement"))
    settings_window.protocol("WM_DELETE_WINDOW", on_save_and_close)

    frame = ttk.Frame(settings_window, padding="10")
    frame.pack(fill='both', expand=True)

    # Temperature Units
    ttk.Label(frame, text=_("Temperature Units")).grid(column=0, row=0, padx=5, pady=5)
    temperature_unit_options = [_("Celsius °C"), _("Fahrenheit °F")]
    temperature_unit_selected_option = tk.StringVar()
    temperature_unit_selected_option.set(settings.get("temperature_unit", _("Celsius °C")))
    temperature_unit_dropdown = ttk.Combobox(frame, textvariable=temperature_unit_selected_option,
                                             values=temperature_unit_options, state="readonly")
    temperature_unit_dropdown.grid(column=1, row=0, padx=5, pady=5)

    # Wind Speed Units
    ttk.Label(frame, text=_("Wind Speed Units")).grid(column=0, row=1, padx=5, pady=5)
    windspeed_unit_options = [_("Km/h"), _("m/s"), _("Mph"), _("Knots")]
    windspeed_unit_selected_option = tk.StringVar()
    windspeed_unit_selected_option.set(settings.get("wind_speed_unit", _("Km/h")))
    windspeed_unit_dropdown = ttk.Combobox(frame, textvariable=windspeed_unit_selected_option,
                                           values=windspeed_unit_options, state="readonly")
    windspeed_unit_dropdown.grid(column=1, row=1, padx=5, pady=5)

    # Precipitation Units
    ttk.Label(frame, text=_("Precipitation Units")).grid(column=0, row=2, padx=5, pady=5)
    precipitation_unit_options = [_("Millimeter"), _("Inch")]
    precipitation_unit_selected_option = tk.StringVar()
    precipitation_unit_selected_option.set(settings.get("precipitation_unit", _("Millimeter")))
    precipitation_unit_dropdown = ttk.Combobox(frame, textvariable=precipitation_unit_selected_option,
                                               values=precipitation_unit_options, state="readonly")
    precipitation_unit_dropdown.grid(column=1, row=2, padx=5, pady=5)

    # Save and Close Button
    save_and_close_btn = ttk.Button(frame, text=_("Save & Close"), command=on_save_and_close)
    save_and_close_btn.grid(column=0, row=3, columnspan=2, pady=10)

    settings_window.transient(root)
    settings_window.grab_set()


def settings_locations_window(root, updates_to_call):
    """
    Opens the Locations Settings window.
    """

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
        save_locations(locations)
        for func, params in updates_to_call:
            func(*params)
        locations_window.destroy()

    locations = load_settings().get("locations", [])  # Load locations from the JSON file

    locations_window = tk.Toplevel()
    locations_window.title(_("Your Locations"))
    locations_window.protocol("WM_DELETE_WINDOW", on_save_and_close)

    frame = ttk.Frame(locations_window, padding="10")
    frame.pack(fill='both', expand=True)
    ttk.Label(frame, text=_("Your saved locations"), font="bold").grid(column=0, row=0, columnspan=2, padx=5, pady=5)
    # Listbox for stored locations
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
    add_location_btn = ttk.Button(frame, text=_("Add"), command=on_add_location)
    add_location_btn.grid(column=0, row=3, padx=5, pady=5)

    delete_location_btn = ttk.Button(frame, text=_("Delete"), command=on_delete_location)
    delete_location_btn.grid(column=1, row=3, padx=5, pady=5)

    # Search field for locations
    ttk.Label(frame, text=_("Search Location")).grid(column=0, row=4, columnspan=2, padx=5, pady=5)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(frame, width=50, textvariable=search_var)
    search_entry.grid(column=0, row=5, columnspan=2, pady=5)

    search_btn = ttk.Button(frame, text=_("Search"), command=on_search)
    search_btn.grid(column=0, row=6, columnspan=2, padx=5, pady=5)

    # Listbox for search results
    ttk.Label(frame, text=_("Search Results")).grid(column=0, row=7, columnspan=2, padx=5, pady=5)
    search_results_listbox = tk.Listbox(frame, height=10, width=80, exportselection=False)
    search_results_listbox.results = {}
    search_results_listbox.grid(column=0, row=8, columnspan=2, padx=5, pady=5)

    # Save and Close Button
    save_and_close_btn = ttk.Button(frame, text=_("Save & Close"), command=on_save_and_close)
    save_and_close_btn.grid(column=0, row=9, columnspan=2, pady=10)

    locations_window.transient(root)
    locations_window.grab_set()
