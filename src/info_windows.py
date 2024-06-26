import tkinter as tk
from tkinter import ttk
import webbrowser
from settings_manager import load_settings
import gettext

selected_locale = load_settings().get("locale", "ua")
text_object = gettext.translation('info', localedir='../locales', languages=[selected_locale])
text_object.install()
_ = text_object.gettext


# Application version
version = "0.1.0"


def open_help_window():
    """Opens a help window with contact information and links."""
    window = tk.Toplevel()
    window.title()

    frame = ttk.Frame(window, padding="10")
    frame.pack(fill='both', expand=True)

    sample_text = ttk.Label(
        frame,
        text=(_(
            "Need help? \nWrite an email to korbutmykhailo@gmail.com\n or \n"
            "contact me on GitHub at github.com/Misha1tigr/NeboKrug"
        )),
        justify="center",
        font="bold"
    )
    sample_text.grid(column=0, row=0, padx=5, pady=5)

    # Button to open email client
    email_button = ttk.Button(
        frame,
        text=_("Open Email"),
        command=lambda: webbrowser.open("mailto:korbutmykhailo@gmail.com")
    )
    email_button.grid(column=0, row=1, padx=5, pady=5, sticky='ew')

    # Button to open GitHub page
    github_button = ttk.Button(
        frame,
        text=_("Open GitHub"),
        command=lambda: webbrowser.open("https://github.com/Misha1tigr/NeboKrug")
    )
    github_button.grid(column=0, row=2, padx=5, pady=5, sticky='ew')

    # Button to close the help window
    close_button = ttk.Button(
        frame,
        text=_("Close"),
        command=window.destroy
    )
    close_button.grid(column=0, row=3, padx=5, pady=5, sticky='ew')


def open_feedback_window():
    """Opens a feedback window with a link to GitHub issues page."""
    window = tk.Toplevel()
    window.title(_("Feedback"))

    frame = ttk.Frame(window, padding="10")
    frame.pack(fill='both', expand=True)

    sample_text = ttk.Label(
        frame,
        text=(_(
            "Have feedback to share?\nOpen an issue at GitHub here: "
            "github.com/Misha1tigr/NeboKrug"
        )),
        justify="center",
        font="bold"
    )
    sample_text.grid(column=0, row=0, padx=5, pady=5)

    # Button to open GitHub issues page
    github_button = ttk.Button(
        frame,
        text=_("Open GitHub"),
        command=lambda: webbrowser.open("https://github.com/Misha1tigr/NeboKrug/issues")
    )
    github_button.grid(column=0, row=2, padx=5, pady=5, sticky='ew')

    # Button to close the feedback window
    close_button = ttk.Button(
        frame,
        text=_("Close"),
        command=window.destroy
    )
    close_button.grid(column=0, row=3, padx=5, pady=5, sticky='ew')


def open_about_window():
    """Opens an about window with detailed information about the app."""
    window = tk.Toplevel()
    window.title(_("About"))

    frame = ttk.Frame(window, padding="10 10 10 10")
    frame.grid(row=0, column=0, sticky="nsew")

    content = [
        (_("Weather App"), True),
        (f"Version: {version}", False),
        ("separator", None),
        (_("About:"), True),
        (_(
            "The Weather App is a versatile and user-friendly application designed to "
            "provide comprehensive weather information, historical data, and AI-driven "
            "outfit recommendations. Built using Python and leveraging the Open-Meteo API, "
            "the app offers a wide range of features to keep users informed and prepared for "
            "any weather conditions."),
            False
        ),
        (_("Features:"), True),
        (_(
            "- Current Weather & Forecast: Get up-to-date weather information and a 14-day "
            "forecast for your selected locations."),
            False
        ),
        (_(
            "- Historical Weather Data: Access historical weather data, allowing you to "
            "compare today's weather with past conditions."),
            False
        ),
        (_("- AI Outfit Recommendations: Receive personalized outfit suggestions based on the weather forecast."),
            False
        ),
        (_("- Daily Fun Facts: Learn interesting and fun facts about the weather each day."), False),
        (_("Developed By:"), True),
        (_("Korbut Mykhailo"), False),
        ("separator", None),
        (_("Acknowledgements:"), True),
        (_(
            "This app was developed as part of a coursework project, and I would like to extend "
            "my gratitude to the following resources and libraries that made this possible:"),
            False
        ),
        (_("- Open-Meteo API: For providing reliable weather and geocoding data."), False),
        (_("- Tkinter and Ttk: For the graphical user interface components."), False),
        (_("- Matplotlib: For the plotting and visualization of weather data."), False),
        (_("- Pandas: For data manipulation and analysis."), False),
        ("separator", None),
        (_("Contact Information:"), True),
        (_("For more information, feedback, or support, please contact:"), False),
        (_("- Email: korbutmykhailo@gmail.com"), False),
        (_("- GitHub: github.com/Misha1tigr"), False),
        ("separator", None),
        (_("Thank you for using the Weather App! Stay informed and enjoy the weather!"), False),
    ]

    row = 0
    for text, is_bold in content:
        if text == "separator":
            separator = ttk.Separator(frame, orient='horizontal')
            separator.grid(row=row, column=0, padx=5, pady=10, sticky="we")
        else:
            font = ("TkDefaultFont", 10, "bold") if is_bold else None
            label = ttk.Label(frame, text=text, wraplength=400, font=font)
            label.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
        row += 1

    # Button to close the about window
    close_button = ttk.Button(
        frame,
        text=_("Close"),
        command=window.destroy
    )
    close_button.grid(column=0, row=row, padx=5, pady=5, sticky='ew')
