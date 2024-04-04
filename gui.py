import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from ttkthemes import ThemedTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import re
from indicators import soil_indicators
from fahp import evaluate_soil_health
from assessment import assess_soil_health, generate_rating, generate_crop_recommendations
from PIL import Image as PILImage, ImageTk
from tkcalendar import Calendar
from database import view_database, save_results
from report import export_to_excel, generate_pdf_report
import threading
import time
import os
import subprocess
import io
from PIL import Image, ImageTk
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import win32api
import win32print
import win32ui
import win32con
import openpyxl


def create_gui():
    def open_email_link(event):
        webbrowser.open("mailto:mzu22000486@mzu.edu.in")

    window = ThemedTk(theme="ubuntu")
    window.title("Soil Health Diagnostic System (v0.2.404)")

    icon = PILImage.open("main.ico")
    window.iconphoto(True, ImageTk.PhotoImage(icon))

    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)  # Set the weight of column 1 to 1
    window.grid_columnconfigure(2, weight=0)  # Set the weight of column 2 to 0
    window.grid_rowconfigure(0, weight=1)

    label_image = PILImage.open('shi.png')
    label_image = label_image.resize((30, 30), PILImage.Resampling.LANCZOS)
    label_icon = ImageTk.PhotoImage(label_image)

    farmer_image = PILImage.open('farmer.png')
    farmer_image = farmer_image.resize((30, 30), PILImage.Resampling.LANCZOS)
    farmer_icon = ImageTk.PhotoImage(farmer_image)

    farmer_label = ttk.Label(window, text="Farmer Information", font=("Helvetica", 14, "bold"), image=farmer_icon,
                             compound=tk.LEFT)
    farmer_label.image = farmer_icon

    info_frame = ttk.LabelFrame(window, labelwidget=farmer_label)
    info_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
    info_frame.grid_columnconfigure(1, weight=1)

    # Center the program window on the user's screen
    window.update_idletasks()
    window_width = 1024  # Set your desired window width
    window_height = 600  # Set your desired window height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Test ID input field
    test_id_label = ttk.Label(info_frame, text='Test ID')
    test_id_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
    test_id_entry = ttk.Entry(info_frame, validate='key',
                              validatecommand=(
                                  info_frame.register(lambda P: (P.isdigit() and len(P) <= 4) or P == ''), '%P'))
    test_id_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
    test_id_entry.bind("<Tab>", lambda event: on_test_id_tab(event, info_frame, sample_date_entry))

    # Sample Collection Date input field
    sample_date_label = ttk.Label(info_frame, text='Sample Collection Date')
    sample_date_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)
    sample_date_entry = ttk.Entry(info_frame)
    sample_date_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
    sample_date_entry.bind("<1>", lambda event: on_sample_date_click(event, info_frame, sample_date_entry))

    # GPS Data input fields
    gps_label = ttk.Label(info_frame, text='GPS Data')
    gps_label.grid(row=2, column=0, sticky='w', padx=5, pady=5)
    gps_frame = ttk.Frame(info_frame)
    gps_frame.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
    gps_frame.grid_columnconfigure(0, weight=1)
    gps_frame.grid_columnconfigure(1, weight=1)

    latitude_entry = ttk.Entry(gps_frame, validate='key',
                               validatecommand=(
                                   info_frame.register(lambda P: re.match(r'^-?\d{0,3}(\.\d{0,6})?$', P) is not None),
                                   '%P'))
    latitude_entry.grid(row=0, column=0, sticky='ew', padx=(0, 5))
    latitude_label = ttk.Label(gps_frame, text="° N")
    latitude_label.grid(row=0, column=1, sticky='w')

    longitude_entry = ttk.Entry(gps_frame, validate='key',
                                validatecommand=(
                                    info_frame.register(lambda P: re.match(r'^-?\d{0,3}(\.\d{0,6})?$', P) is not None),
                                    '%P'))
    longitude_entry.grid(row=0, column=2, sticky='ew', padx=(5, 0))
    longitude_label = ttk.Label(gps_frame, text="° E")
    longitude_label.grid(row=0, column=3, sticky='w')

    # Name input field
    name_label = ttk.Label(info_frame, text='Name')
    name_label.grid(row=3, column=0, sticky='w', padx=5, pady=5)
    name_entry = ttk.Entry(info_frame, validate='key', validatecommand=(
        info_frame.register(lambda P: re.match(r'^[A-Za-z.\s]{0,50}$', P) is not None), '%P'))
    name_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=5)

    # Area input field
    area_label = ttk.Label(info_frame, text='Area (ha)')
    area_label.grid(row=4, column=0, sticky='w', padx=5, pady=5)
    area_entry = ttk.Entry(info_frame, validate='key', validatecommand=(
        info_frame.register(lambda P: re.match(r'^\d{0,2}(\.\d{0,2})?$', P) is not None), '%P'))
    area_entry.grid(row=4, column=1, sticky='ew', padx=5, pady=5)
    area_entry.bind("<Tab>", lambda event: on_area_tab(event, gender_dropdown))

    # Gender dropdown field
    gender_label = ttk.Label(info_frame, text='Gender')
    gender_label.grid(row=5, column=0, sticky='w', padx=5, pady=5)
    gender_var = tk.StringVar()
    gender_dropdown = ttk.Combobox(info_frame, textvariable=gender_var, values=['Male', 'Female', 'Others'],
                                   state='readonly')
    gender_dropdown.grid(row=5, column=1, sticky='ew', padx=5, pady=5)

    # Age input field
    age_label = ttk.Label(info_frame, text='Age')
    age_label.grid(row=6, column=0, sticky='w', padx=5, pady=5)
    age_entry = ttk.Entry(info_frame, validate='key',
                          validatecommand=(
                              info_frame.register(lambda P: (P.isdigit() and (1 <= int(P) <= 99)) or P == ''), '%P'))
    age_entry.grid(row=6, column=1, sticky='ew', padx=5, pady=5)

    # Address input field
    address_label = ttk.Label(info_frame, text='Address')
    address_label.grid(row=7, column=0, sticky='w', padx=5, pady=5)
    address_entry = ttk.Entry(info_frame, validate='key',
                              validatecommand=(info_frame.register(lambda P: len(P) <= 60), '%P'))
    address_entry.grid(row=7, column=1, sticky='ew', padx=5, pady=5)

    # Mobile No. input field
    mobile_label = ttk.Label(info_frame, text='Mobile No.')
    mobile_label.grid(row=8, column=0, sticky='w', padx=5, pady=5)
    mobile_entry = ttk.Entry(info_frame, validate='key', validatecommand=(
        info_frame.register(lambda P: (P.isdigit() and len(P) <= 10) or P == ''), '%P'))
    mobile_entry.grid(row=8, column=1, sticky='ew', padx=5, pady=5)

    label = ttk.Label(window, text="Soil Health Indicators", font=("Helvetica", 14, "bold"), image=label_icon,
                      compound=tk.LEFT)
    label.image = label_icon

    input_frame = ttk.LabelFrame(window, labelwidget=label)
    input_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
    input_frame.grid_columnconfigure(0, weight=1)
    input_frame.grid_columnconfigure(1, weight=2)  # Increase the weight of column 1

    visualization_frame = ttk.Frame(window)
    visualization_frame.grid(row=0, column=2, sticky='nsew', padx=10, pady=10)
    visualization_frame.grid_rowconfigure(0, weight=1)
    visualization_frame.grid_columnconfigure(0, weight=1)

    visualization_frame.grid_remove()

    # Create a separate frame for the loading screen
    loading_frame = ttk.Frame(window)
    loading_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
    loading_frame.grid_remove()  # Hide the loading frame initially

    # Create a label and a progress bar inside the loading frame
    loading_label = ttk.Label(loading_frame, text="Assessing Soil Health...", font=("Helvetica", 16))
    loading_label.pack(pady=10)

    progress_bar = ttk.Progressbar(loading_frame, length=200, mode='indeterminate')
    progress_bar.pack(pady=10)

    # Soil pH input field
    soil_ph_label = ttk.Label(input_frame, text='Soil pH (0-8.5)')
    soil_ph_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
    soil_ph_entry = ttk.Entry(input_frame, validate='key', validatecommand=(input_frame.register(
        lambda P: re.match(r'^\d+(\.\d{0,2})?$', P) is not None and (0 <= float(P) <= 8.50) if P else True), '%P'))
    soil_ph_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

    # Nitrogen input field
    nitrogen_label = ttk.Label(input_frame, text='Nitrogen(N)(10-500 mg/kg)')
    nitrogen_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)
    nitrogen_entry = ttk.Entry(input_frame, validate='key', validatecommand=(input_frame.register(
        lambda P: re.match(r'^\d+(\.\d{0,2})?$', P) is not None and (0 <= float(P) <= 500.00) if P else True), '%P'))
    nitrogen_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)

    # Phosphorus input field
    phosphorus_label = ttk.Label(input_frame, text='Phosphorus(P)(10-200 mg/kg)')
    phosphorus_label.grid(row=2, column=0, sticky='w', padx=5, pady=5)
    phosphorus_entry = ttk.Entry(input_frame, validate='key', validatecommand=(input_frame.register(
        lambda P: re.match(r'^\d+(\.\d{0,2})?$', P) is not None and (0 <= float(P) <= 200.00) if P else True), '%P'))
    phosphorus_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)

    # Potassium input field
    potassium_label = ttk.Label(input_frame, text='Potassium(K)(10-400 mg/kg)')
    potassium_label.grid(row=3, column=0, sticky='w', padx=5, pady=5)
    potassium_entry = ttk.Entry(input_frame, validate='key', validatecommand=(input_frame.register(
        lambda P: re.match(r'^\d+(\.\d{0,2})?$', P) is not None and (0 <= float(P) <= 400.00) if P else True), '%P'))
    potassium_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=5)

    # Electrical Conductivity input field
    electrical_conductivity_label = ttk.Label(input_frame, text='Electrical Conductivity(EC)(0-4.00 dS/m)')
    electrical_conductivity_label.grid(row=4, column=0, sticky='w', padx=5, pady=5)
    electrical_conductivity_entry = ttk.Entry(input_frame, validate='key', validatecommand=(
        input_frame.register(lambda P: re.match(r'^\d+(\.\d{0,2})?$', P) is not None and (0<= float(P) <= 4.00) if P else True),
        '%P'))
    electrical_conductivity_entry.grid(row=4, column=1, sticky='ew', padx=5, pady=5)

    # Temperature input field
    temperature_label = ttk.Label(input_frame, text='Temperature(1-50 °C)')
    temperature_label.grid(row=5, column=0, sticky='w', padx=5, pady=5)
    temperature_entry = ttk.Entry(input_frame, validate='key', validatecommand=(
        input_frame.register(lambda P: re.match(r'^\d+(\.\d{0,2})?$', P) is not None and (1 <= float(P) <= 50.00) if P else True), '%P'))
    temperature_entry.grid(row=5, column=1, sticky='ew', padx=5, pady=5)

    # Moisture input field
    moisture_label = ttk.Label(input_frame, text='Moisture(1-100 %)')
    moisture_label.grid(row=6, column=0, sticky='w', padx=5, pady=5)
    moisture_entry = ttk.Entry(input_frame, validate='key', validatecommand=(
        input_frame.register(lambda P: re.match(r'^\d+(\.\d{0,2})?$', P) is not None and (1 <= float(P) <= 100) if P else True), '%P'))
    moisture_entry.grid(row=6, column=1, sticky='ew', padx=5, pady=5)

    # Humidity input field
    humidity_label = ttk.Label(input_frame, text='Humidity(1-100 %)')
    humidity_label.grid(row=7, column=0, sticky='w', padx=5, pady=5)
    humidity_entry = ttk.Entry(input_frame, validate='key', validatecommand=(
        input_frame.register(lambda P: re.match(r'^\d+(\.\d{0,2})?$', P) is not None and (1 <= float(P) <= 100) if P else True), '%P'))
    humidity_entry.grid(row=7, column=1, sticky='ew', padx=5, pady=5)

    # Create a label to display the dynamic message
    assessing_label = ttk.Label(window, text="", font=("Helvetica", 12))
    assessing_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

    def show_loading_window():
        loading_window = tk.Toplevel(window)
        loading_window.overrideredirect(True)  # Remove window decorations
        loading_window.resizable(False, False)

        loading_frame = ttk.Frame(loading_window)
        loading_frame.pack(fill=tk.BOTH, expand=True)

        loading_label = ttk.Label(loading_frame, text="Assessing Soil Health...",
                                  font=("Helvetica", 10, "bold", "italic"))
        loading_label.pack(pady=10)

        progress_bar = ttk.Progressbar(loading_window, length=200, mode='indeterminate')
        progress_bar.pack(pady=10)

        # Center the loading window on the program window
        loading_window.update_idletasks()
        width = loading_window.winfo_width()
        height = loading_window.winfo_height()
        x = window.winfo_x() + (window.winfo_width() // 2) - (width // 2)
        y = window.winfo_y() + (window.winfo_height() // 2) - (height // 2)
        loading_window.geometry(f"{width}x{height}+{x}+{y}")

        progress_bar.start()

        return loading_window, progress_bar

    def assess_button_clicked():
        indicator_ranges = {
            'Nitrogen': (10, 500),
            'Phosphorus': (10, 200),
            'Potassium': (10, 400)
        }

        for indicator, (min_value, max_value) in indicator_ranges.items():
            entry = None
            if indicator == 'Nitrogen':
                entry = nitrogen_entry
            elif indicator == 'Phosphorus':
                entry = phosphorus_entry
            elif indicator == 'Potassium':
                entry = potassium_entry

            if entry:
                value = entry.get()
                if value:
                    if float(value) < min_value or float(value) > max_value:
                        tk.messagebox.showerror("Invalid Input",
                                                f"Please enter a value between {min_value} and {max_value} for {indicator}.")
                        entry.focus_set()
                        return

        # Check the 'Mobile No.' field
        mobile_no = mobile_entry.get()
        if not (mobile_no.isdigit() and len(mobile_no) == 10):
            tk.messagebox.showerror("Invalid Mobile No.", "Please enter a valid 10-digit Mobile No.")
            mobile_entry.focus_set()
            mobile_entry.selection_range(0, tk.END)  # Highlight the text in the entry field
            return

        loading_window, progress_bar = show_loading_window()

        # Disable the Assess Soil Health button
        assess_button.config(state=tk.DISABLED)

        # Start a separate thread to perform the assessment
        threading.Thread(target=perform_assessment, args=(loading_window, progress_bar)).start()

    def perform_assessment(loading_window, progress_bar):
        # Simulating assessment calculation time
        time.sleep(2)  # Adjust the time as needed

        # Perform the assessment calculations
        indicator_values = [
            float(soil_ph_entry.get()) if soil_ph_entry.get() else None,
            float(nitrogen_entry.get()) if nitrogen_entry.get() else None,
            float(phosphorus_entry.get()) if phosphorus_entry.get() else None,
            float(potassium_entry.get()) if potassium_entry.get() else None,
            float(electrical_conductivity_entry.get()) if electrical_conductivity_entry.get() else None,
            float(temperature_entry.get()) if temperature_entry.get() else None,
            float(moisture_entry.get()) if moisture_entry.get() else None,
            float(humidity_entry.get()) if humidity_entry.get() else None
        ]

        latitude = float(latitude_entry.get().strip())
        longitude = float(longitude_entry.get().strip())

        normalized_values = []
        for indicator, value in zip(soil_indicators, indicator_values):
            if value is None:
                normalized_values.append(None)
            else:
                normalized_value = (value - indicator.min_value) / (indicator.max_value - indicator.min_value)
                normalized_values.append(normalized_value)

        soil_health_score = evaluate_soil_health([value for value in normalized_values if value is not None])
        recommendations = generate_crop_recommendations(soil_health_score)

        data = {
            'test_id': test_id_entry.get(),
            'collection_date': sample_date_entry.get(),
            'latitude': latitude,
            'longitude': longitude,
            'name': name_entry.get(),
            'area': float(area_entry.get()) if area_entry.get() else None,
            'gender': gender_var.get(),
            'age': int(age_entry.get()) if age_entry.get() else None,
            'address': address_entry.get(),
            'mobile_no': mobile_entry.get(),
            'soil_ph': indicator_values[0],
            'nitrogen': indicator_values[1],
            'phosphorus': indicator_values[2],
            'potassium': indicator_values[3],
            'electrical_conductivity': indicator_values[4],
            'temperature': indicator_values[5],
            'moisture': indicator_values[6],
            'humidity': indicator_values[7],
            'soil_health_score': soil_health_score,
            'recommendations': recommendations
        }

        # Update the UI with the results
        window.after(0, update_results, loading_window, progress_bar, indicator_values, soil_health_score)

    def update_results(loading_window, progress_bar, indicator_values, soil_health_score):
        # Stop the progress bar animation
        progress_bar.stop()

        # Close the loading window
        loading_window.destroy()

        # Enable the Assess Soil Health button
        assess_button.config(state=tk.NORMAL)

        # Update the UI with the assessment results
        # Disable and grey out the input fields in the Farmer Information and Soil Health Indicators frame
        disable_input_fields()

        visualize_results(indicator_values, soil_health_score, visualization_frame)

        save_export_button.config(state=tk.NORMAL)
        report_button.config(state=tk.DISABLED)
        clear_button.config(state=tk.NORMAL)

        visualization_frame.grid()

        # Disable the 'Assess Soil Health' button immediately
        assess_button.config(state=tk.DISABLED)

        # Re-center the window after displaying the radar chart
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        window.geometry(f"+{x}+{y}")

    # Function to clear all the input fields
    def clear_button_clicked():
        enable_input_fields()
        clear_button.config(state=tk.NORMAL)
        assess_button.config(state=tk.DISABLED)
        save_export_button.config(state=tk.DISABLED)
        report_button.config(state=tk.DISABLED)

        # Clear the radar chart frame
        for widget in visualization_frame.winfo_children():
            widget.destroy()

        # Resize the program window to its normal state
        window.geometry("")  # Set an empty geometry to reset the window size
        window.update()  # Update the window to apply the changes

        # Hide the visualization frame
        visualization_frame.grid_remove()

        test_id_entry.delete(0, tk.END)
        sample_date_entry.delete(0, tk.END)
        latitude_entry.delete(0, tk.END)  # Clear the latitude entry field
        longitude_entry.delete(0, tk.END)  # Clear the longitude entry field
        name_entry.delete(0, tk.END)
        area_entry.delete(0, tk.END)
        gender_var.set('')
        age_entry.delete(0, tk.END)
        address_entry.delete(0, tk.END)
        mobile_entry.delete(0, tk.END)
        soil_ph_entry.delete(0, tk.END)
        nitrogen_entry.delete(0, tk.END)
        phosphorus_entry.delete(0, tk.END)
        potassium_entry.delete(0, tk.END)
        electrical_conductivity_entry.delete(0, tk.END)
        temperature_entry.delete(0, tk.END)
        moisture_entry.delete(0, tk.END)
        humidity_entry.delete(0, tk.END)

    def generate_pdf_report_clicked():
        data = {
            'test_id': test_id_entry.get(),
            'collection_date': sample_date_entry.get(),
            'latitude': float(latitude_entry.get().strip()),
            'longitude': float(longitude_entry.get().strip()),
            'name': name_entry.get(),
            'area': float(area_entry.get()) if area_entry.get() else None,
            'gender': gender_var.get(),
            'age': int(age_entry.get()) if age_entry.get() else None,
            'address': address_entry.get(),
            'mobile_no': mobile_entry.get(),
            'soil_ph': float(soil_ph_entry.get()) if soil_ph_entry.get() else None,
            'nitrogen': float(nitrogen_entry.get()) if nitrogen_entry.get() else None,
            'phosphorus': float(phosphorus_entry.get()) if phosphorus_entry.get() else None,
            'potassium': float(potassium_entry.get()) if potassium_entry.get() else None,
            'electrical_conductivity': float(
                electrical_conductivity_entry.get()) if electrical_conductivity_entry.get() else None,
            'temperature': float(temperature_entry.get()) if temperature_entry.get() else None,
            'moisture': float(moisture_entry.get()) if moisture_entry.get() else None,
            'humidity': float(humidity_entry.get()) if humidity_entry.get() else None,
            'soil_health_score': assess_soil_health([
                float(soil_ph_entry.get()) if soil_ph_entry.get() else None,
                float(nitrogen_entry.get()) if nitrogen_entry.get() else None,
                float(phosphorus_entry.get()) if phosphorus_entry.get() else None,
                float(potassium_entry.get()) if potassium_entry.get() else None,
                float(electrical_conductivity_entry.get()) if electrical_conductivity_entry.get() else None,
                float(temperature_entry.get()) if temperature_entry.get() else None,
                float(moisture_entry.get()) if moisture_entry.get() else None,
                float(humidity_entry.get()) if humidity_entry.get() else None
            ]),
            'rating': generate_rating(assess_soil_health([
                float(soil_ph_entry.get()) if soil_ph_entry.get() else None,
                float(nitrogen_entry.get()) if nitrogen_entry.get() else None,
                float(phosphorus_entry.get()) if phosphorus_entry.get() else None,
                float(potassium_entry.get()) if potassium_entry.get() else None,
                float(electrical_conductivity_entry.get()) if electrical_conductivity_entry.get() else None,
                float(temperature_entry.get()) if temperature_entry.get() else None,
                float(moisture_entry.get()) if moisture_entry.get() else None,
                float(humidity_entry.get()) if humidity_entry.get() else None
            ])),
            'crop_recommendations': generate_crop_recommendations(assess_soil_health([
                float(soil_ph_entry.get()) if soil_ph_entry.get() else None,
                float(nitrogen_entry.get()) if nitrogen_entry.get() else None,
                float(phosphorus_entry.get()) if phosphorus_entry.get() else None,
                float(potassium_entry.get()) if potassium_entry.get() else None,
                float(electrical_conductivity_entry.get()) if electrical_conductivity_entry.get() else None,
                float(temperature_entry.get()) if temperature_entry.get() else None,
                float(moisture_entry.get()) if moisture_entry.get() else None,
                float(humidity_entry.get()) if humidity_entry.get() else None
            ]))
        }
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")],
                                                 initialfile=f"{data['test_id']}_report.pdf")
        if file_path:
            indicator_values = [
                float(soil_ph_entry.get()) if soil_ph_entry.get() else None,
                float(nitrogen_entry.get()) if nitrogen_entry.get() else None,
                float(phosphorus_entry.get()) if phosphorus_entry.get() else None,
                float(potassium_entry.get()) if potassium_entry.get() else None,
                float(electrical_conductivity_entry.get()) if electrical_conductivity_entry.get() else None,
                float(temperature_entry.get()) if temperature_entry.get() else None,
                float(moisture_entry.get()) if moisture_entry.get() else None,
                float(humidity_entry.get()) if humidity_entry.get() else None
            ]
            generate_pdf_report(data, file_path, indicator_values)
            tk.messagebox.showinfo("Report Confirmation", "Soil Health Report Generated Successfully")

            # Disable the 'Generate' button immediately
            report_button.config(state=tk.DISABLED)

            # Open the generated PDF report in a new window
            open_pdf_window(file_path)

            disable_all_elements()
            new_test_button.config(state=tk.NORMAL)

    def save_export_button_clicked():
        data = {
            'test_id': test_id_entry.get(),
            'collection_date': sample_date_entry.get(),
            'latitude': float(latitude_entry.get().strip()) if latitude_entry.get().strip() else None,
            'longitude': float(longitude_entry.get().strip()) if longitude_entry.get().strip() else None,
            'name': name_entry.get(),
            'area': float(area_entry.get()) if area_entry.get() else None,
            'gender': gender_var.get(),
            'age': int(age_entry.get()) if age_entry.get() else None,
            'address': address_entry.get(),
            'mobile_no': mobile_entry.get(),
            'soil_ph': float(soil_ph_entry.get()) if soil_ph_entry.get() else None,
            'nitrogen': float(nitrogen_entry.get()) if nitrogen_entry.get() else None,
            'phosphorus': float(phosphorus_entry.get()) if phosphorus_entry.get() else None,
            'potassium': float(potassium_entry.get()) if potassium_entry.get() else None,
            'electrical_conductivity': float(
                electrical_conductivity_entry.get()) if electrical_conductivity_entry.get() else None,
            'temperature': float(temperature_entry.get()) if temperature_entry.get() else None,
            'moisture': float(moisture_entry.get()) if moisture_entry.get() else None,
            'humidity': float(humidity_entry.get()) if humidity_entry.get() else None,
            'soil_health_score': assess_soil_health([
                float(soil_ph_entry.get()) if soil_ph_entry.get() else None,
                float(nitrogen_entry.get()) if nitrogen_entry.get() else None,
                float(phosphorus_entry.get()) if phosphorus_entry.get() else None,
                float(potassium_entry.get()) if potassium_entry.get() else None,
                float(electrical_conductivity_entry.get()) if electrical_conductivity_entry.get() else None,
                float(temperature_entry.get()) if temperature_entry.get() else None,
                float(moisture_entry.get()) if moisture_entry.get() else None,
                float(humidity_entry.get()) if humidity_entry.get() else None
            ]),
            'recommendations': generate_crop_recommendations(assess_soil_health([
                float(soil_ph_entry.get()) if soil_ph_entry.get() else None,
                float(nitrogen_entry.get()) if nitrogen_entry.get() else None,
                float(phosphorus_entry.get()) if phosphorus_entry.get() else None,
                float(potassium_entry.get()) if potassium_entry.get() else None,
                float(electrical_conductivity_entry.get()) if electrical_conductivity_entry.get() else None,
                float(temperature_entry.get()) if temperature_entry.get() else None,
                float(moisture_entry.get()) if moisture_entry.get() else None,
                float(humidity_entry.get()) if humidity_entry.get() else None
            ]))
        }

        # Save the data to the database
        save_results(data)

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")],
                                                 initialfile=f"{data['test_id']}_test.xlsx")
        if file_path:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            header = ["Test ID", "Collection Date", "Latitude", "Longitude", "Name", "Area (ha)", "Gender", "Age",
                      "Address", "Mobile No.", "Soil pH", "Nitrogen", "Phosphorus", "Potassium",
                      "Electrical Conductivity", "Temperature", "Moisture", "Humidity", "Soil Health Score",
                      "Recommendations"]
            sheet.append(header)

            # Format the values based on their respective data types
            formatted_values = []
            for i, value in enumerate(data.values()):
                if i in [2, 3, 5, 10, 11, 12, 13, 14, 15, 16, 17, 18]:
                    formatted_values.append(float(value) if value else None)
                elif i == 7:
                    formatted_values.append(int(value) if value else None)
                else:
                    formatted_values.append(value)

            sheet.append(formatted_values)
            workbook.save(file_path)
            messagebox.showinfo("Save Confirmation", "Results exported to Excel successfully.")

            # Enable the 'Generate Report' button
            report_button.config(state=tk.NORMAL)

            # Disable the 'Save & Export' button immediately
            save_export_button.config(state=tk.DISABLED)

    def new_test_button_clicked():
        clear_button_clicked()
        enable_input_fields()
        clear_button.config(state=tk.NORMAL)
        assess_button.config(state=tk.DISABLED)
        save_export_button.config(state=tk.DISABLED)
        report_button.config(state=tk.DISABLED)

        for widget in visualization_frame.winfo_children():
            widget.destroy()

        window.geometry("")
        window.update()

        visualization_frame.grid_remove()

    def enable_assess_button():
        if all(entry.get() for entry in [test_id_entry, sample_date_entry, latitude_entry, longitude_entry, name_entry,
                                         area_entry, gender_var, age_entry, address_entry, mobile_entry, soil_ph_entry,
                                         nitrogen_entry, phosphorus_entry, potassium_entry,
                                         electrical_conductivity_entry, temperature_entry, moisture_entry,
                                         humidity_entry]):
            assess_button.config(state=tk.NORMAL)
        else:
            assess_button.config(state=tk.DISABLED)

    def enable_input_fields():
        test_id_entry.config(state=tk.NORMAL)
        sample_date_entry.config(state=tk.NORMAL)
        sample_date_entry.bind("<1>", lambda event: on_sample_date_click(event, info_frame, sample_date_entry))
        latitude_entry.config(state=tk.NORMAL)
        longitude_entry.config(state=tk.NORMAL)
        name_entry.config(state=tk.NORMAL)
        area_entry.config(state=tk.NORMAL)
        gender_dropdown.config(state="readonly")
        age_entry.config(state=tk.NORMAL)
        address_entry.config(state=tk.NORMAL)
        mobile_entry.config(state=tk.NORMAL)
        soil_ph_entry.config(state=tk.NORMAL)
        nitrogen_entry.config(state=tk.NORMAL)
        phosphorus_entry.config(state=tk.NORMAL)
        potassium_entry.config(state=tk.NORMAL)
        electrical_conductivity_entry.config(state=tk.NORMAL)
        temperature_entry.config(state=tk.NORMAL)
        moisture_entry.config(state=tk.NORMAL)
        humidity_entry.config(state=tk.NORMAL)

        # Restore the labels' foreground color
        test_id_label.config(foreground="black")
        sample_date_label.config(foreground="black")
        gps_label.config(foreground="black")
        name_label.config(foreground="black")
        area_label.config(foreground="black")
        gender_label.config(foreground="black")
        age_label.config(foreground="black")
        address_label.config(foreground="black")
        mobile_label.config(foreground="black")
        soil_ph_label.config(foreground="black")
        nitrogen_label.config(foreground="black")
        phosphorus_label.config(foreground="black")
        potassium_label.config(foreground="black")
        electrical_conductivity_label.config(foreground="black")
        temperature_label.config(foreground="black")
        moisture_label.config(foreground="black")
        humidity_label.config(foreground="black")

    def disable_input_fields():
        test_id_entry.config(state=tk.DISABLED)
        sample_date_entry.config(state=tk.DISABLED)
        sample_date_entry.unbind("<1>")
        latitude_entry.config(state=tk.DISABLED)
        longitude_entry.config(state=tk.DISABLED)
        name_entry.config(state=tk.DISABLED)
        area_entry.config(state=tk.DISABLED)
        gender_dropdown.config(state=tk.DISABLED)
        age_entry.config(state=tk.DISABLED)
        address_entry.config(state=tk.DISABLED)
        mobile_entry.config(state=tk.DISABLED)
        soil_ph_entry.config(state=tk.DISABLED)
        nitrogen_entry.config(state=tk.DISABLED)
        phosphorus_entry.config(state=tk.DISABLED)
        potassium_entry.config(state=tk.DISABLED)
        electrical_conductivity_entry.config(state=tk.DISABLED)
        temperature_entry.config(state=tk.DISABLED)
        moisture_entry.config(state=tk.DISABLED)
        humidity_entry.config(state=tk.DISABLED)

        # Grey out the labels
        test_id_label.config(foreground="grey")
        sample_date_label.config(foreground="grey")
        gps_label.config(foreground="grey")
        name_label.config(foreground="grey")
        area_label.config(foreground="grey")
        gender_label.config(foreground="grey")
        age_label.config(foreground="grey")
        address_label.config(foreground="grey")
        mobile_label.config(foreground="grey")
        soil_ph_label.config(foreground="grey")
        nitrogen_label.config(foreground="grey")
        phosphorus_label.config(foreground="grey")
        potassium_label.config(foreground="grey")
        electrical_conductivity_label.config(foreground="grey")
        temperature_label.config(foreground="grey")
        moisture_label.config(foreground="grey")
        humidity_label.config(foreground="grey")

    def disable_all_elements():
        disable_input_fields()
        clear_button.config(state=tk.DISABLED)
        assess_button.config(state=tk.DISABLED)
        save_export_button.config(state=tk.DISABLED)
        report_button.config(state=tk.DISABLED)
        for widget in visualization_frame.winfo_children():
            if isinstance(widget, (ttk.Button, ttk.Entry, ttk.Combobox)):
                widget.configure(state=tk.DISABLED)
            elif isinstance(widget, ttk.Frame):
                for subwidget in widget.winfo_children():
                    if isinstance(subwidget, (ttk.Button, ttk.Entry, ttk.Combobox)):
                        subwidget.configure(state=tk.DISABLED)

    button_frame = ttk.Frame(window)
    button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="we")

    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)
    button_frame.columnconfigure(2, weight=1)
    button_frame.columnconfigure(3, weight=1)
    button_frame.columnconfigure(4, weight=1)
    button_frame.columnconfigure(5, weight=1)

    button_width = 20
    button_height = 20

    new_image = PILImage.open('new.png')
    new_image = new_image.resize((button_width, button_height), PILImage.Resampling.LANCZOS)
    new_icon = ImageTk.PhotoImage(new_image)

    clear_image = PILImage.open('clear.png')
    clear_image = clear_image.resize((button_width, button_height), PILImage.Resampling.LANCZOS)
    clear_icon = ImageTk.PhotoImage(clear_image)

    assess_image = PILImage.open('assess.png')
    assess_image = assess_image.resize((button_width, button_height), PILImage.Resampling.LANCZOS)
    assess_icon = ImageTk.PhotoImage(assess_image)

    export_image = PILImage.open('excel.png')
    export_image = export_image.resize((button_width, button_height), PILImage.Resampling.LANCZOS)
    export_icon = ImageTk.PhotoImage(export_image)

    report_image = PILImage.open('report.png')
    report_image = report_image.resize((button_width, button_height), PILImage.Resampling.LANCZOS)
    report_icon = ImageTk.PhotoImage(report_image)

    database_icon = PILImage.open('database.png')
    database_icon = database_icon.resize((20, 20), PILImage.LANCZOS)
    database_photo = ImageTk.PhotoImage(database_icon)

    new_test_button = ttk.Button(button_frame, text="New Test", command=new_test_button_clicked, image=new_icon,
                                 compound=tk.LEFT)
    new_test_button.image = new_icon
    new_test_button.grid(row=0, column=0, padx=5, sticky="we")

    clear_button = ttk.Button(button_frame, text="Clear", command=clear_button_clicked, image=clear_icon,
                              compound=tk.LEFT)
    clear_button.image = clear_icon
    clear_button.grid(row=0, column=1, padx=5, sticky="we")
    clear_button.config(state=tk.DISABLED)

    assess_button = ttk.Button(button_frame, text="Assess Soil Health", command=assess_button_clicked,
                               image=assess_icon, compound=tk.LEFT)
    assess_button.image = assess_icon
    assess_button.grid(row=0, column=2, padx=5, sticky="we")
    assess_button.config(state=tk.DISABLED)

    save_export_button = ttk.Button(button_frame, text="Save & Export", command=save_export_button_clicked,
                                    image=export_icon, compound=tk.LEFT)
    save_export_button.image = export_icon
    save_export_button.grid(row=0, column=3, padx=5, sticky="we")
    save_export_button.config(state=tk.DISABLED)

    report_button = ttk.Button(button_frame, text="Generate Report", command=generate_pdf_report_clicked,
                               image=report_icon, compound=tk.LEFT)
    report_button.image = report_icon
    report_button.grid(row=0, column=4, padx=5, sticky="we")
    report_button.config(state=tk.DISABLED)

    view_database_button = ttk.Button(button_frame, text="View Database", command=lambda: view_database(window),
                                      image=database_photo, compound=tk.LEFT)
    view_database_button.image = database_photo
    view_database_button.grid(row=0, column=5, padx=5, sticky="we")

    disable_input_fields()

    test_id_entry.bind("<KeyRelease>", lambda event: enable_assess_button())
    sample_date_entry.bind("<KeyRelease>", lambda event: enable_assess_button())
    latitude_entry.bind("<KeyRelease>", lambda event: enable_assess_button())
    longitude_entry.bind("<KeyRelease>", lambda event: enable_assess_button())

    name_entry.bind("<KeyRelease>", lambda event: enable_assess_button())
    area_entry.bind("<KeyRelease>", lambda event: enable_assess_button())
    gender_var.trace("w", lambda *args: enable_assess_button())
    age_entry.bind("<KeyRelease>", lambda event: enable_assess_button())
    address_entry.bind("<KeyRelease>", lambda event: enable_assess_button())
    mobile_entry.bind("<KeyRelease>", lambda event: enable_assess_button())
    soil_ph_entry.bind("<KeyRelease>", lambda event: enable_assess_button())
    nitrogen_entry.bind("<KeyRelease>", lambda event: enable_assess_button())
    phosphorus_entry.bind("<KeyRelease>", lambda event: enable_assess_button())
    potassium_entry.bind("<KeyRelease>", lambda event: enable_assess_button())
    electrical_conductivity_entry.bind("<KeyRelease>", lambda event: enable_assess_button())
    temperature_entry.bind("<KeyRelease>", lambda event: enable_assess_button())
    moisture_entry.bind("<KeyRelease>", lambda event: enable_assess_button())
    humidity_entry.bind("<KeyRelease>", lambda event: enable_assess_button())

    # DEVELOPER INFORMATION
    bottom_frame = ttk.Frame(window)
    bottom_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="we")
    bottom_frame.columnconfigure(0, weight=1)

    title_label = ttk.Label(bottom_frame, text="SOIL HEALTH DIAGNOSTIC SYSTEM (v0.2.404)", font=("Helvetica", 8, "bold"),
                            justify="center")
    title_label.grid(row=0, column=0, padx=5, pady=(0, 5))

    mzu_logo = PILImage.open("mzu.png")
    mzu_logo = mzu_logo.resize((80, 80), PILImage.LANCZOS)
    mzu_photo = ImageTk.PhotoImage(mzu_logo)
    mzu_label = ttk.Label(bottom_frame, image=mzu_photo)
    mzu_label.image = mzu_photo
    mzu_label.grid(row=3, column=0, padx=5, pady=(5, 0))

    credentials_frame = ttk.Frame(bottom_frame)
    credentials_frame.grid(row=1, column=0, padx=5, pady=(0, 5))

    credentials_text = "Designed & Developed by:\nLALDINPUIA\nResearch Scholar"
    credentials_label = ttk.Label(credentials_frame, text=credentials_text, font=("Helvetica", 8), justify="center")
    credentials_label.pack()

    email_link = tk.Label(credentials_frame, text="Email: mzu22000486@mzu.edu.in", font=("Helvetica", 8), fg="green",
                          cursor="hand2")
    email_link.pack()
    email_link.bind("<Button-1>", open_email_link)

    department_text = "Department of Mathematics and Computer Science\nMizoram University"
    department_label = ttk.Label(bottom_frame, text=department_text, font=("Helvetica", 8, "bold"), justify="center")
    department_label.grid(row=2, column=0, padx=5, pady=(5, 5))

    def visualize_results(indicator_values, soil_health_score, visualization_frame):
        for widget in visualization_frame.winfo_children():
            widget.destroy()
        visualization_content_frame = ttk.Frame(visualization_frame)
        visualization_content_frame.pack(fill=tk.BOTH, expand=True)

        radar_chart_frame = ttk.Frame(visualization_content_frame)
        radar_chart_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        fig, ax = plt.subplots(figsize=(4.5, 4.5), subplot_kw={'projection': 'polar'})
        angles = np.linspace(0, 2 * np.pi, len(soil_indicators), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))
        indicator_values = np.concatenate((indicator_values, [indicator_values[0]]))

        ax.plot(angles, indicator_values, 'o-', linewidth=1)
        ax.fill(angles, indicator_values, alpha=0.25)

        labels = [
            'pH',
            'N\n(mg/kg)',
            'P\n(mg/kg)',
            'K\n(mg/kg)',
            'EC\n(dS/m)',
            'Temp\n(°C)',
            'Moist\n(%)',
            'Humid\n(%)'
        ]
        ax.set_thetagrids(angles[:-1] * 180 / np.pi, labels, fontsize=8)

        ax.set_title("Soil Health Indicators", fontsize=12)
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=radar_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        result_frame = ttk.Frame(visualization_content_frame)
        result_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        center_frame = ttk.Frame(result_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        result_label = ttk.Label(result_frame, text=f"Soil Health Score: {soil_health_score:.2f}",
                                 font=("Helvetica", 10, "bold"))
        result_label.pack(side=tk.TOP, padx=10)

        recommendations_text = f"\nCrop Recommendations:\n{generate_crop_recommendations(soil_health_score)}"
        recommendations_label = ttk.Label(result_frame, text=recommendations_text, font=("Helvetica", 10, "bold"),
                                          justify=tk.CENTER, wraplength=400)
        recommendations_label.pack(side=tk.BOTTOM, padx=10)

        try:
            data = {
                'test_id': test_id_entry.get(),
                'collection_date': sample_date_entry.get(),
                'latitude': float(latitude_entry.get().strip()),
                'longitude': float(longitude_entry.get().strip()),
                'name': name_entry.get(),
                'area': float(area_entry.get()) if area_entry.get() else None,
                'gender': gender_var.get(),
                'age': int(age_entry.get()) if age_entry.get() else None,
                'address': address_entry.get(),
                'mobile_no': mobile_entry.get(),
                'soil_ph': indicator_values[0],
                'nitrogen': indicator_values[1],
                'phosphorus': indicator_values[2],
                'potassium': indicator_values[3],
                'electrical_conductivity': indicator_values[4],
                'temperature': indicator_values[5],
                'moisture': indicator_values[6],
                'humidity': indicator_values[7],
                'soil_health_score': soil_health_score,
                'recommendations': generate_crop_recommendations(soil_health_score)
            }

        except ValueError as e:
            tk.messagebox.showerror("Invalid Input", str(e))

    # Open PDF Files
    def open_pdf_window(file_path):
        # Create a new window for the PDF viewer
        pdf_window = tk.Toplevel(window)
        pdf_window.title(f"Soil Health Report of: {os.path.basename(file_path)}")

        # Create a canvas to display the PDF pages
        canvas = tk.Canvas(pdf_window, width=768, height=1024)
        canvas.pack(fill=tk.BOTH, expand=True)

        # Create a scrollbar for the canvas
        scrollbar = ttk.Scrollbar(pdf_window, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Open the PDF file
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            num_pages = len(pdf_reader.pages)

            for page_num in range(num_pages):
                # Render each page as an image using pdf2image
                page_images = convert_from_path(file_path, first_page=page_num + 1, last_page=page_num + 1)

                for img in page_images:
                    img = img.resize((768, 1024), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)

                    # Display the image on the canvas
                    canvas.create_image(0, page_num * 600, anchor=tk.NW, image=photo)
                    canvas.image = photo

        # Configure the canvas scroll region
        canvas.configure(scrollregion=canvas.bbox(tk.ALL))

        # Bind mouse wheel events for zooming in/out
        def zoom(event):
            if event.delta > 0:
                canvas.scale(tk.ALL, event.x, event.y, 1.1, 1.1)
            elif event.delta < 0:
                canvas.scale(tk.ALL, event.x, event.y, 0.9, 0.9)
            canvas.configure(scrollregion=canvas.bbox(tk.ALL))

        canvas.bind("<MouseWheel>", zoom)

        # Create a frame for the buttons
        button_frame = ttk.Frame(pdf_window)
        button_frame.pack(side=tk.BOTTOM, pady=10)

        # Create the Print button
        print_button = ttk.Button(button_frame, text="Print", command=lambda: print_pdf(file_path))
        print_button.pack(side=tk.LEFT, padx=10)

        # Create the Close button
        close_button = ttk.Button(button_frame, text="Close", command=pdf_window.destroy)
        close_button.pack(side=tk.RIGHT, padx=10)

        # Center the PDF viewer window on the screen
        pdf_window.update_idletasks()
        screen_width = pdf_window.winfo_screenwidth()
        screen_height = pdf_window.winfo_screenheight()
        window_width = pdf_window.winfo_width()
        window_height = pdf_window.winfo_height()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        pdf_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    '''# Claude 3 Opus Print PDF
    def print_pdf(file_path):
        try:
            # Create a DC (Device Context) object for the default printer
            printer_name = win32print.GetDefaultPrinter()
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(printer_name)

            # Create a PrintDialog object
            pd = win32ui.CreatePrintDialog(hDC)

            # Initialize the PrintDialog object
            pd.DoModal()

            # Get the selected print settings
            devmode = pd.GetDevMode()

            # Access defaults
            PRINTER_DEFAULTS = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}

            # Open printer to get the handle
            pHandle = win32print.OpenPrinter(printer_name, PRINTER_DEFAULTS)

            # Get the current properties
            properties = win32print.GetPrinter(pHandle, 2)

            # Set the devmode
            properties['pDevMode'] = devmode

            # Save the printer settings
            win32print.SetPrinter(pHandle, 2, properties, 0)

            # Print the PDF file using the selected printer without opening the default PDF reader
            win32api.ShellExecute(0, "printto", file_path, f'"{printer_name}"', ".", 0)

            messagebox.showinfo("Print", f"'{os.path.basename(file_path)}' has been sent to the printer.")

            # Close the printer
            win32print.ClosePrinter(pHandle)
        except Exception as e:
            messagebox.showerror("Print Error", f"An error occurred while printing the file:\n{str(e)}")



    # Print PDF using Github Codepilot

    def print_pdf(file_path):
        try:
            # Get the default printer
            default_printer = win32print.GetDefaultPrinter()

            # Access defaults
            PRINTER_DEFAULTS = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}

            # Open printer to get the handle
            pHandle = win32print.OpenPrinter(default_printer, PRINTER_DEFAULTS)

            # Get the current properties
            properties = win32print.GetPrinter(pHandle, 2)

            # Get the devmode
            pDevModeObj = properties['pDevMode']

            # Open the printer properties and pass the devmode
            result = win32print.DocumentProperties(0, pHandle, default_printer, pDevModeObj, pDevModeObj,
                                                   win32con.DM_PROMPT)

            if result == win32con.IDOK:  # IDOK
                # Reassign the devmode
                properties['pDevMode'] = pDevModeObj

                # Save the printer settings
                win32print.SetPrinter(pHandle, 2, properties, 0)

                # Print the PDF file using the default printer without opening the default PDF reader
                win32api.ShellExecute(0, "printto", file_path, f'"{default_printer}"', ".", 0)

                messagebox.showinfo("Print", f"'{os.path.basename(file_path)}' has been sent to the printer.")
            else:
                messagebox.showinfo("Print", "Printing canceled.")

            # Close the printer
            win32print.ClosePrinter(pHandle)
        except Exception as e:
            messagebox.showerror("Print Error", f"An error occurred while printing the file:\n{str(e)}")

    # Print PDF using Ghostscript
    def print_pdf(file_path):
        try:
            # Get the default printer
            default_printer = win32print.GetDefaultPrinter()

            # Construct the Ghostscript command
            # Note: Adjust the path to gswin64c.exe as needed for your Ghostscript installation
            gs_command = [
                "gswin64c.exe",
                "-dNOPAUSE",
                "-dBATCH",
                "-dQUIET",
                "-dPrinted",
                f'-sDEVICE=mswinpr2',
                f'-sOutputFile=%printer%{default_printer}',
                file_path
            ]

            # Execute the command
            subprocess.run(gs_command, check=True)

            messagebox.showinfo("Print", f"'{os.path.basename(file_path)}' has been sent to the printer.")
        except Exception as e:
            messagebox.showerror("Print Error", f"An error occurred while printing the file:\n{str(e)}")'''

    # Print PDF using win32print
    def print_pdf(file_path):
        # Print the PDF file
        try:
            # Get the default printer
            default_printer = win32print.GetDefaultPrinter()

            # Access defaults
            PRINTER_DEFAULTS = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}

            # Open printer to get the handle
            pHandle = win32print.OpenPrinter(default_printer, PRINTER_DEFAULTS)

            # Get the current properties
            properties = win32print.GetPrinter(pHandle, 2)

            # Get the devmode
            pDevModeObj = properties['pDevMode']

            # Open the printer properties and pass the devmode
            result = win32print.DocumentProperties(0, pHandle, default_printer, pDevModeObj, None, 5)

            if result == 1:  # IDOK
                # Reassign the devmode
                properties['pDevMode'] = pDevModeObj

                # Save the printer settings
                win32print.SetPrinter(pHandle, 2, properties, 0)

                # Print the PDF file using the default printer without opening the default PDF reader
                win32api.ShellExecute(0, "printto", file_path, f'"{default_printer}"', ".", 0)

                messagebox.showinfo("Print", f"'{os.path.basename(file_path)}' has been sent to the printer.")
            else:
                messagebox.showinfo("Print", "Printing canceled.")

            # Close the printer
            win32print.ClosePrinter(pHandle)
        except Exception as e:
            messagebox.showerror("Print Error", f"An error occurred while printing the file:\n{str(e)}")

    return window
def on_sample_date_click(event, info_frame, sample_date_entry):
    def on_date_click(event):
        selected_date = calendar.selection_get()
        calendar.selection_set(selected_date)

    def on_select(event=None):
        selected_date = calendar.selection_get()
        sample_date_entry.delete(0, tk.END)
        sample_date_entry.insert(0, selected_date.strftime("%d-%m-%Y"))
        sample_date_entry.config(state=tk.NORMAL)
        sample_date_entry.unbind("<Key>")
        sample_date_entry.bind("<Key>", lambda e: "break")
        calendar_frame.destroy()
        info_frame.focus_set()

    calendar_frame = ttk.Frame(info_frame)
    calendar_frame.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
    calendar = Calendar(calendar_frame, selectmode='day', date_pattern='dd-mm-y')
    calendar.pack(fill='both', expand=True)

    calendar.bind('<<CalendarSelected>>', on_date_click)
    calendar.bind('<Double-1>', on_select)

    select_button = ttk.Button(calendar_frame, text="Select", command=on_select)
    select_button.pack(pady=5)

    calendar.focus_set()
def on_test_id_tab(event, info_frame, sample_date_entry):
    on_sample_date_click(event, info_frame, sample_date_entry)

def on_area_tab(event, gender_dropdown):
    gender_dropdown.focus_set()
    gender_dropdown.event_generate('<Down>')