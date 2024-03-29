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
from assessment import assess_soil_health, generate_crop_recommendations
from PIL import Image as PILImage, ImageTk
from tkcalendar import Calendar
from database import view_database, save_results
from report import export_to_excel, generate_pdf_report


def create_gui():
    def open_email_link(event):
        webbrowser.open("mailto:mzu22000486@mzu.edu.in")

    window = ThemedTk(theme="ubuntu")
    window.title("Soil Health Diagnostic System (v0.2.404)")

    icon = PILImage.open("main.ico")
    window.iconphoto(True, ImageTk.PhotoImage(icon))

    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)
    window.grid_columnconfigure(2, weight=2)
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
    input_frame.grid_columnconfigure(1, weight=1)

    visualization_frame = ttk.Frame(window)
    visualization_frame.grid(row=0, column=2, sticky='nsew', padx=10, pady=10)
    visualization_frame.grid_rowconfigure(0, weight=1)
    visualization_frame.grid_columnconfigure(0, weight=1)

    visualization_frame.grid_remove()

    # Soil pH input field
    soil_ph_label = ttk.Label(input_frame, text='Soil pH (0-8.5)')
    soil_ph_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
    soil_ph_entry = ttk.Entry(input_frame, validate='key', validatecommand=(input_frame.register(
        lambda P: re.match(r'^\d+(\.\d{0,2})?$', P) is not None and (0 <= float(P) <= 8.50) if P else True), '%P'))
    soil_ph_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

    # Nitrogen input field
    nitrogen_label = ttk.Label(input_frame, text='Nitrogen(10-500)(mg/kg)')
    nitrogen_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)
    nitrogen_entry = ttk.Entry(input_frame, validate='key', validatecommand=(input_frame.register(
        lambda P: re.match(r'^\d+(\.\d{0,2})?$', P) is not None and (0 <= float(P) <= 500.00) if P else True), '%P'))
    nitrogen_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)

    # Phosphorus input field
    phosphorus_label = ttk.Label(input_frame, text='Phosphorus(10-200)(mg/kg)')
    phosphorus_label.grid(row=2, column=0, sticky='w', padx=5, pady=5)
    phosphorus_entry = ttk.Entry(input_frame, validate='key', validatecommand=(input_frame.register(
        lambda P: re.match(r'^\d+(\.\d{0,2})?$', P) is not None and (0 <= float(P) <= 200.00) if P else True), '%P'))
    phosphorus_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)

    # Potassium input field
    potassium_label = ttk.Label(input_frame, text='Potassium(10-400)(mg/kg)')
    potassium_label.grid(row=3, column=0, sticky='w', padx=5, pady=5)
    potassium_entry = ttk.Entry(input_frame, validate='key', validatecommand=(input_frame.register(
        lambda P: re.match(r'^\d+(\.\d{0,2})?$', P) is not None and (0 <= float(P) <= 400.00) if P else True), '%P'))
    potassium_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=5)

    # Electrical Conductivity input field
    electrical_conductivity_label = ttk.Label(input_frame, text='Electrical Conductivity(0-4)(dS/m)')
    electrical_conductivity_label.grid(row=4, column=0, sticky='w', padx=5, pady=5)
    electrical_conductivity_entry = ttk.Entry(input_frame, validate='key', validatecommand=(
        input_frame.register(lambda P: re.match(r'^\d+(\.\d{0,2})?$', P) is not None and (0 <= float(P) <= 4) if P else True),
        '%P'))
    electrical_conductivity_entry.grid(row=4, column=1, sticky='ew', padx=5, pady=5)

    # Temperature input field
    temperature_label = ttk.Label(input_frame, text='Temperature(0-50)(°C)')
    temperature_label.grid(row=5, column=0, sticky='w', padx=5, pady=5)
    temperature_entry = ttk.Entry(input_frame, validate='key', validatecommand=(
        input_frame.register(lambda P: re.match(r'^\d+(\.\d{0,2})?$', P) is not None and (0 <= float(P) <= 50.00) if P else True), '%P'))
    temperature_entry.grid(row=5, column=1, sticky='ew', padx=5, pady=5)

    # Moisture input field
    moisture_label = ttk.Label(input_frame, text='Moisture(0-100)(%)')
    moisture_label.grid(row=6, column=0, sticky='w', padx=5, pady=5)
    moisture_entry = ttk.Entry(input_frame, validate='key', validatecommand=(
        input_frame.register(lambda P: re.match(r'^\d+(\.\d{0,2})?$', P) is not None and (0 <= float(P) <= 100) if P else True), '%P'))
    moisture_entry.grid(row=6, column=1, sticky='ew', padx=5, pady=5)

    # Humidity input field
    humidity_label = ttk.Label(input_frame, text='Humidity(0-100)(%)')
    humidity_label.grid(row=7, column=0, sticky='w', padx=5, pady=5)
    humidity_entry = ttk.Entry(input_frame, validate='key', validatecommand=(
        input_frame.register(lambda P: re.match(r'^\d+(\.\d{0,2})?$', P) is not None and (0 <= float(P) <= 100) if P else True), '%P'))
    humidity_entry.grid(row=7, column=1, sticky='ew', padx=5, pady=5)

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
        save_results(data)

        # Disable and grey out the input fields in the Farmer Information and Soil Health Indicators frame
        disable_input_fields()

        visualize_results(indicator_values, soil_health_score, visualization_frame)

        save_export_button.config(state=tk.NORMAL)
        report_button.config(state=tk.DISABLED)
        clear_button.config(state=tk.NORMAL)

        visualization_frame.grid()

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
            disable_all_elements()
            new_test_button.config(state=tk.NORMAL)

    def save_export_button_clicked():
        test_id = test_id_entry.get()
        file_path = export_to_excel(test_id)
        if file_path:
            tk.messagebox.showinfo("Save Confirmation", "Soil Test Report Saved Successfully")
            report_button.config(state=tk.NORMAL)

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
    button_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="we")

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

    title_label = ttk.Label(bottom_frame, text="SOIL HEALTH DIAGNOSTIC SYSTEM (v0.2.404)", font=("Helvetica", 12, "bold"),
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
    credentials_label = ttk.Label(credentials_frame, text=credentials_text, font=("Helvetica", 10), justify="center")
    credentials_label.pack()

    email_link = tk.Label(credentials_frame, text="Email: mzu22000486@mzu.edu.in", font=("Helvetica", 10), fg="blue",
                          cursor="hand2")
    email_link.pack()
    email_link.bind("<Button-1>", open_email_link)

    department_text = "Department of Mathematics and Computer Science\nMizoram University"
    department_label = ttk.Label(bottom_frame, text=department_text, font=("Helvetica", 10), justify="center")
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
            #save_results(data) # This was triggering  the Save results to the database Twice ;)
        except ValueError as e:
            tk.messagebox.showerror("Invalid Input", str(e))

    return window
def on_sample_date_click(event, info_frame, sample_date_entry):
    def on_select(event=None):
        selected_date = calendar.selection_get()
        sample_date_entry.delete(0, tk.END)
        sample_date_entry.insert(0, selected_date.strftime("%d-%m-%Y"))
        calendar_frame.destroy()

    calendar_frame = ttk.Frame(info_frame)
    calendar_frame.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
    calendar = Calendar(calendar_frame, selectmode='day', date_pattern='dd-mm-y')
    calendar.pack(fill='both', expand=True)

    calendar.bind("<<CalendarSelected>>", lambda event: on_select())

    select_button = ttk.Button(calendar_frame, text="Select", command=on_select)
    select_button.pack(pady=5)
def on_test_id_tab(event, info_frame, sample_date_entry):
    on_sample_date_click(event, info_frame, sample_date_entry)

def on_area_tab(event, gender_dropdown):
    gender_dropdown.focus_set()
    gender_dropdown.event_generate('<Down>')

'''def show_input_range_error(indicator):
    tk.messagebox.showerror("Invalid Input", f"Please enter a value between 10 and {indicator.max_value} for {indicator.name}.")

def check_input_range(entry, indicator_name, min_value, max_value):
    value = entry.get()
    if value:
        if float(value) < min_value or float(value) > max_value:
            show_input_range_error(type('Indicator', (object,), {'name': indicator_name, 'max_value': max_value}))
            entry.delete(0, tk.END)'''
