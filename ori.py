import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import sqlite3
import csv
import io
import os
import re
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, Table, TableStyle, Paragraph, Spacer, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from indicators import soil_indicators
from fahp import fuzzy_comparison_matrix, consistency_ratio, fahp_weights
from assessment import assess_soil_health, generate_rating, generate_crop_recommendations
from PIL import Image as Image, ImageTk
from tkcalendar import Calendar
from pdf2image import convert_from_path
from PIL import UnidentifiedImageError
import win32api
import win32print
from reportlab.lib.enums import TA_CENTER


def create_database():
    conn = sqlite3.connect('soil_health.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS soil_tests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  test_id TEXT,
                  collection_date TEXT,
                  latitude REAL,
                  longitude REAL,
                  name TEXT,
                  area REAL,
                  gender TEXT,
                  age INTEGER,
                  address TEXT,
                  mobile_no TEXT,
                  soil_ph REAL,
                  nitrogen REAL,
                  phosphorus REAL,
                  potassium REAL,
                  electrical_conductivity REAL,
                  temperature REAL,
                  moisture REAL,
                  humidity REAL,
                  soil_health_score REAL,
                  recommendations TEXT)''')
    conn.commit()
    conn.close()


def generate_pdf_report(data, file_path):
    report = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()

    # Modify the title style to use a smaller font size and center alignment
    styles["Title"].fontSize = 16
    styles["Title"].alignment = TA_CENTER

    report_elements = [Paragraph("Soil Health Report", styles["Title"]), Spacer(1, 0.2 * inch)]

    # Farmer Information
    farmer_info = [
        ['Name', data['name']],
        ['Area (ha)', data['area']],
        ['Gender', data['gender']],
        ['Age', data['age']],
        ['Address', data['address']],
        ['Mobile No.', data['mobile_no']]
    ]
    farmer_table = Table(farmer_info)
    farmer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
    ]))

    # Soil Sample Details
    sample_details = [
        ['Test ID', data['test_id']],
        ['Sample Collection Date', data['collection_date']],
        ['GPS Data', f"Latitude: {data['latitude']}, Longitude: {data['longitude']}"]
    ]
    sample_details_table = Table(sample_details)
    sample_details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
    ]))

    # Create a table to hold both farmer information and sample details tables
    info_table = Table([[farmer_table, sample_details_table]])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    farmer_info_heading = Paragraph("Farmer Information", styles["Heading3"])
    sample_details_heading = Paragraph("Soil Sample Details", styles["Heading3"])

    report_elements.append(Table([[farmer_info_heading, sample_details_heading]]))
    report_elements.append(info_table)
    report_elements.append(Spacer(1, 0.3 * inch))

    # Soil Health Indicators
    table_data = [['Soil Health Indicators', 'Values', 'Normal Values']]
    for indicator in soil_indicators:
        indicator_name = indicator.name.lower().replace(' ', '_').replace('(', '').replace(')', '')
        value = data.get(indicator_name, 'N/A')
        normal_value = indicator.optimal_range
        table_data.append([str(indicator), value, f"{normal_value[0]} to {normal_value[1]} {indicator.unit}"])
    table_data.append(['Soil Health Score', f"{data['soil_health_score']:.2f}", '0 to 1'])
    table_data.append(['Rating', generate_rating(data['soil_health_score']), ''])
    table_data.append(['Crop Recommendations', generate_crop_recommendations(data['soil_health_score']), ''])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
    ]))

    report_elements.append(Paragraph("Soil Health Indicators", styles["Heading3"]))
    report_elements.append(table)
    report_elements.append(Spacer(1, 0.3 * inch))

    # Create the radar chart
    fig, ax = plt.subplots(figsize=(3, 3), subplot_kw={'projection': 'polar'})
    angles = np.linspace(0, 2 * np.pi, len(soil_indicators), endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))
    indicator_values = np.concatenate(([data.get(indicator.name.lower().replace(' ', '_').replace('(', '').replace(')', ''), 0) for indicator in soil_indicators], [data.get(soil_indicators[0].name.lower().replace(' ', '_').replace('(', '').replace(')', ''), 0)]))

    ax.plot(angles, indicator_values, 'o-', linewidth=1)
    ax.fill(angles, indicator_values, alpha=0.25)
    labels = [
        'pH',
        'N',
        'P',
        'K',
        'EC',
        'Temp',
        'Moist',
        'Humid'
    ]
    ax.set_thetagrids(angles[:-1] * 180 / np.pi, labels)
    ax.set_title("Soil Health Indicators", fontsize=8, pad=20)
    ax.grid(True)

    # Save the radar chart as an image in memory
    chart_buffer = io.BytesIO()
    plt.savefig(chart_buffer, format='png', dpi=300, bbox_inches='tight')
    chart_buffer.seek(0)
    chart_img = Image(chart_buffer, width=3*inch, height=3*inch)
    report_elements.append(chart_img)

    report.build(report_elements)


def save_results(data):
    conn = sqlite3.connect('soil_health.db')
    c = conn.cursor()
    c.execute('''INSERT INTO soil_tests
                 (test_id, collection_date, latitude, longitude, name, area, gender, age, address, mobile_no,
                  soil_ph, nitrogen, phosphorus, potassium, electrical_conductivity, temperature, moisture, humidity,
                  soil_health_score, recommendations)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (
                  data['test_id'], data['collection_date'], data['latitude'], data['longitude'], data['name'],
                  data['area'],
                  data['gender'], data['age'], data['address'], data['mobile_no'], data['soil_ph'], data['nitrogen'],
                  data['phosphorus'], data['potassium'], data['electrical_conductivity'], data['temperature'],
                  data['moisture'],
                  data['humidity'], data['soil_health_score'], data['recommendations']))
    conn.commit()
    conn.close()


def export_to_csv(test_id):
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], initialfile=f"{test_id}_test.csv")
    if file_path:
        conn = sqlite3.connect('soil_health.db')
        c = conn.cursor()
        c.execute("SELECT * FROM soil_tests WHERE test_id = ?", (test_id,))
        data = c.fetchall()
        conn.close()

        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(
                ['ID', 'Test ID', 'Sample Collection Date', 'Latitude', 'Longitude', 'Name', 'Area (ha)', 'Gender',
                 'Age', 'Address', 'Mobile No.', 'Soil pH', 'Nitrogen', 'Phosphorus', 'Potassium',
                 'Electrical Conductivity', 'Temperature', 'Moisture', 'Humidity', 'Soil Health Score',
                 'Crop Recommendations'])
            writer.writerows(data)
    return file_path


def on_sample_date_click(event, info_frame, sample_date_entry):
    def on_select(sample_date_entry):
        selected_date = calendar.selection_get()
        sample_date_entry.delete(0, tk.END)
        sample_date_entry.insert(0, selected_date.strftime("%d-%m-%Y"))
        calendar_frame.destroy()

    calendar_frame = ttk.Frame(info_frame)
    calendar_frame.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
    calendar = Calendar(calendar_frame, selectmode='day', date_pattern='dd-mm-y')
    calendar.pack(fill='both', expand=True)
    ttk.Button(calendar_frame, text="Select", command=lambda: on_select(sample_date_entry)).pack(pady=5)


def on_test_id_tab(event, info_frame, sample_date_entry):
    on_sample_date_click(event, info_frame, sample_date_entry)


def on_area_tab(event, gender_dropdown):
    gender_dropdown.focus_set()
    gender_dropdown.event_generate('<Down>')


def validate_gps_entry(event, entry):
    value = entry.get()
    if value:
        try:
            float_value = float(value)
            if len(value) > 10:
                entry.delete(10, tk.END)
            if float_value < -180 or float_value > 180:
                entry.delete(0, tk.END)
                entry.insert(0, "")
        except ValueError:
            entry.delete(0, tk.END)
            entry.insert(0, "")


def close_pdf_report():
    # Clear the PDF display
    for widget in pdf_display_frame.winfo_children():
        widget.destroy()

    # Clear the radar chart canvas
    for widget in visualization_frame.winfo_children():
        widget.destroy()

    # Clear the display fields
    result_label.config(text="")
    recommendations_label.config(text="")

    # Enable input fields and buttons
    enable_input_fields()
    clear_button.config(state=tk.NORMAL)
    assess_button.config(state=tk.DISABLED)
    save_export_button.config(state=tk.DISABLED)
    report_button.config(state=tk.DISABLED)


def display_pdf_report(file_path, pdf_display_frame):
    try:
        # Clear the existing PDF display
        for widget in pdf_display_frame.winfo_children():
            widget.destroy()

        # Create a frame to hold the PDF content
        pdf_content_frame = ttk.Frame(pdf_display_frame)
        pdf_content_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas to display the PDF
        pdf_canvas = tk.Canvas(pdf_content_frame)
        pdf_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a scrollbar for the canvas
        pdf_scrollbar = ttk.Scrollbar(pdf_content_frame, orient=tk.VERTICAL, command=pdf_canvas.yview)
        pdf_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        pdf_canvas.configure(yscrollcommand=pdf_scrollbar.set)

        # Convert the PDF to images
        pdf_images = convert_from_path(file_path)

        if len(pdf_images) > 0:
            # Use the first page of the PDF
            pdf_data = pdf_images[0]

            # Calculate the scaling factor to fit the PDF within the available space
            pdf_width, pdf_height = pdf_data.size
            canvas_width = pdf_display_frame.winfo_width() - 20
            canvas_height = pdf_display_frame.winfo_height() - 60

            if canvas_width > 0 and canvas_height > 0:
                scale = min(canvas_width / pdf_width, canvas_height / pdf_height)

                # Resize the PDF image
                pdf_width = int(pdf_width * scale)
                pdf_height = int(pdf_height * scale)
                pdf_data = pdf_data.resize((pdf_width, pdf_height), Image.Resampling.LANCZOS)

                # Display the PDF image on the canvas
                pdf_photo = ImageTk.PhotoImage(pdf_data)
                pdf_canvas.create_image(0, 0, anchor=tk.NW, image=pdf_photo)
                pdf_canvas.image = pdf_photo

                # Configure the scroll region of the canvas
                pdf_canvas.configure(scrollregion=pdf_canvas.bbox(tk.ALL))
            else:
                # Display a message if the available space is too small
                pdf_canvas.create_text(0, 0, anchor=tk.NW, text="Insufficient space to display the PDF.")

        # Create a frame for the buttons
        button_frame = ttk.Frame(pdf_display_frame)
        button_frame.pack(side=tk.BOTTOM, pady=10)

        # Create a 'Print' button
        print_button = ttk.Button(button_frame, text="Print", command=lambda: print_pdf_report(file_path))
        print_button.pack(side=tk.LEFT, padx=10)

        # Create a 'Close' button
        close_button = ttk.Button(button_frame, text="Close", command=close_pdf_report)
        close_button.pack(side=tk.LEFT, padx=10)

    except UnidentifiedImageError as e:
        tk.messagebox.showerror("Error", f"Failed to display the PDF report:\n{str(e)}")
        close_pdf_report()


def print_pdf_report(file_path):
    try:
        # Open the print dialog box
        win32api.ShellExecute(0, "print", file_path, None, ".", 0)
    except Exception as e:
        tk.messagebox.showerror("Error", f"Failed to print the PDF report:\n{str(e)}")


def create_gui():
    window = ThemedTk(theme="ubuntu")  # Use the "ubuntu" theme
    window.title("Soil Health Diagnostic System")

    # Set the main icon of the program
    icon = Image.open("shds.ico")
    window.iconphoto(True, ImageTk.PhotoImage(icon))

    # Configure the weights for the rows and columns
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)
    window.grid_columnconfigure(2, weight=1)  # Add this line to configure the weight for the third column
    window.grid_rowconfigure(0, weight=1)
    window.grid_rowconfigure(5, weight=1)  # Add this line to configure the weight for the PDF display row

    # Load the image for the farmer information label
    farmer_image = Image.open('farmer.png')
    farmer_image = farmer_image.resize((30, 30), Image.Resampling.LANCZOS)
    farmer_icon = ImageTk.PhotoImage(farmer_image)

    # Create a label with the image and text for farmer information
    farmer_label = ttk.Label(window, text="Farmer Information", font=("Helvetica", 14, "bold"), image=farmer_icon,
                                compound=tk.LEFT)
    farmer_label.image = farmer_icon  # Keep a reference to the image to prevent garbage collection

    # Use the label as the labelwidget for the LabelFrame
    info_frame = ttk.LabelFrame(window, labelwidget=farmer_label)
    info_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
    info_frame.grid_columnconfigure(1, weight=1)  # Make the entry fields expand

    # Create labels and entry fields for farmer information
    info_labels = ['Test ID', 'Sample Collection Date', 'GPS Data (Lat, Long)', 'Name', 'Area (ha)', 'Gender',
                       'Age',
                       'Address', 'Mobile No.']
    info_entries = []

    # Test ID field
    test_id_label = ttk.Label(info_frame, text='Test ID')
    test_id_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
    test_id_entry = ttk.Entry(info_frame)
    test_id_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
    test_id_entry.config(validate='key',
                             validatecommand=(
                             info_frame.register(lambda P: (P.isdigit() and len(P) <= 4) or P == ''), '%P'))
    test_id_entry.bind("<Tab>",
                           lambda event, entry=test_id_entry: on_test_id_tab(event, info_frame, sample_date_entry))
    info_entries.append(test_id_entry)

    # Sample Collection Date field
    sample_date_label = ttk.Label(info_frame, text='Sample Collection Date')
    sample_date_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)
    sample_date_entry = ttk.Entry(info_frame)
    sample_date_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
    sample_date_entry.bind("<1>",
                               lambda event, entry=sample_date_entry: on_sample_date_click(event, info_frame, entry))
    info_entries.append(sample_date_entry)

    # GPS Data fields
    gps_label = ttk.Label(info_frame, text='GPS Data')
    gps_label.grid(row=2, column=0, sticky='w', padx=5, pady=5)
    gps_frame = ttk.Frame(info_frame)
    gps_frame.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
    gps_frame.grid_columnconfigure(0, weight=1)
    gps_frame.grid_columnconfigure(1, weight=1)

    latitude_entry = ttk.Entry(gps_frame)
    latitude_entry.grid(row=0, column=0, sticky='ew', padx=(0, 5))
    latitude_entry.bind("<KeyRelease>", lambda event: validate_gps_entry(event, latitude_entry))
    latitude_label = ttk.Label(gps_frame, text="° N")
    latitude_label.grid(row=0, column=1, sticky='w')

    longitude_entry = ttk.Entry(gps_frame)
    longitude_entry.grid(row=0, column=2, sticky='ew', padx=(5, 0))
    longitude_entry.bind("<KeyRelease>", lambda event: validate_gps_entry(event, longitude_entry))
    longitude_label = ttk.Label(gps_frame, text="° E")
    longitude_label.grid(row=0, column=3, sticky='w')

    info_entries.extend([latitude_entry, longitude_entry])

    # Name field
    name_label = ttk.Label(info_frame, text='Name')
    name_label.grid(row=3, column=0, sticky='w', padx=5, pady=5)
    name_entry = ttk.Entry(info_frame, validate='key',
                               validatecommand=(info_frame.register(lambda P: len(P) <= 35), '%P'))
    name_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
    info_entries.append(name_entry)

    # Area (ha) field
    area_label = ttk.Label(info_frame, text='Area (ha)')
    area_label.grid(row=4, column=0, sticky='w', padx=5, pady=5)
    area_entry = ttk.Entry(info_frame, validate='key',
                               validatecommand=(
                               info_frame.register(lambda P: P == "" or P.replace(".", "", 1).isdigit()), '%P'))
    area_entry.grid(row=4, column=1, sticky='ew', padx=5, pady=5)
    area_entry.bind("<Tab>", lambda event, entry=area_entry: on_area_tab(event, gender_dropdown))
    info_entries.append(area_entry)

    # Gender field
    gender_label = ttk.Label(info_frame, text='Gender')
    gender_label.grid(row=5, column=0, sticky='w', padx=5, pady=5)
    gender_var = tk.StringVar()
    gender_dropdown = ttk.Combobox(info_frame, textvariable=gender_var, values=['Male', 'Female', 'Others'],
                                       state='readonly')
    gender_dropdown.grid(row=5, column=1, sticky='ew', padx=5, pady=5)
    info_entries.append(gender_var)

    # Age field
    age_label = ttk.Label(info_frame, text='Age')
    age_label.grid(row=6, column=0, sticky='w', padx=5, pady=5)
    age_entry = ttk.Entry(info_frame)
    age_entry.grid(row=6, column=1, sticky='ew', padx=5, pady=5)
    age_entry.config(validate='key',
                         validatecommand=(
                         info_frame.register(lambda P: (P.isdigit() and len(P) <= 3) or P == ''), '%P'))
    info_entries.append(age_entry)

    # Address field
    address_label = ttk.Label(info_frame, text='Address')
    address_label.grid(row=7, column=0, sticky='w', padx=5, pady=5)
    address_entry = ttk.Entry(info_frame, validate='key',
                                  validatecommand=(info_frame.register(lambda P: len(P) <= 60), '%P'))
    address_entry.grid(row=7, column=1, sticky='ew', padx=5, pady=5)
    info_entries.append(address_entry)

    # Mobile No. field
    mobile_label = ttk.Label(info_frame, text='Mobile No.')
    mobile_label.grid(row=8, column=0, sticky='w', padx=5, pady=5)
    mobile_entry = ttk.Entry(info_frame)
    mobile_entry.grid(row=8, column=1, sticky='ew', padx=5, pady=5)
    mobile_entry.config(validate='key', validatecommand=(
            info_frame.register(lambda P: (P.isdigit() and len(P) <= 10) or P == ''), '%P'))
    info_entries.append(mobile_entry)

    # Load the image for the soil health indicators label
    label_image = Image.open('soil_health.png')
    label_image = label_image.resize((30, 30), Image.Resampling.LANCZOS)
    label_icon = ImageTk.PhotoImage(label_image)

    # Create a label with the image and text for soil health indicators
    label = ttk.Label(window, text="Soil Health Indicators", font=("Helvetica", 14, "bold"), image=label_icon,
                          compound=tk.LEFT)
    label.image = label_icon  # Keep a reference to the image to prevent garbage collection

    # Use the label as the labelwidget for the LabelFrame
    input_frame = ttk.LabelFrame(window, labelwidget=label)
    input_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
    input_frame.grid_columnconfigure(1, weight=1)  # Make the entry fields expand

    # Create a frame to hold the visualization (radar chart)
    visualization_frame = ttk.Frame(window)
    visualization_frame.grid(row=0, column=2, sticky='nsew', padx=10, pady=10)
    visualization_frame.grid_rowconfigure(0, weight=1)
    visualization_frame.grid_columnconfigure(0, weight=1)

    # Create labels and entry fields for each soil indicator
    labels = []
    entries = []
    for i, indicator in enumerate(soil_indicators):
        label = ttk.Label(input_frame, text=str(indicator))
        label.grid(row=i, column=0, sticky='w', padx=5, pady=5)
        entry = ttk.Entry(input_frame)
        entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
        labels.append(label)
        entries.append(entry)

    # Create a button to trigger the soil health assessment

    def assess_button_clicked():
        # Validate the input fields
        try:
            indicator_values = []
            for entry in entries:
                value = entry.get().strip()
                if value == "":
                    raise ValueError("Empty input")
                indicator_values.append(float(value))

            latitude = float(latitude_entry.get().strip())
            longitude = float(longitude_entry.get().strip())

            if gender_var.get() == "":
                raise ValueError("Please select a gender")

            soil_health_score = assess_soil_health(indicator_values)
            recommendations = generate_crop_recommendations(soil_health_score)

            data = {
                'test_id': test_id_entry.get(),
                'collection_date': sample_date_entry.get(),
                'latitude': latitude,
                'longitude': longitude,
                'name': name_entry.get(),
                'area': float(area_entry.get()),
                'gender': gender_var.get(),
                'age': int(age_entry.get()),
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

            result_label.config(text=f"Soil Health Score: {soil_health_score:.2f}", font=("Helvetica", 10, "bold"))
            recommendations_text = f"Crop Recommendations:\n{recommendations}"
            recommendations_label.config(text=recommendations_text, font=("Helvetica", 10, "bold"), justify=tk.CENTER)
            visualize_results(indicator_values, soil_health_score, visualization_frame)
            save_results(data)

            save_export_button.config(state=tk.NORMAL)

        except ValueError as e:
            tk.messagebox.showerror("Invalid Input", str(e))

    # Create a function to clear all the input fields
    def clear_button_clicked():
        for entry in info_entries:
            if isinstance(entry, tk.Entry):
                entry.delete(0, 'end')
            elif isinstance(entry, tk.StringVar):
                entry.set('')
        for entry in entries:
            entry.delete(0, 'end')
        result_label.config(text="")
        recommendations_label.config(text="")
        for widget in visualization_frame.winfo_children():
            widget.destroy()
        for widget in pdf_display_frame.winfo_children():
            widget.destroy()

    def generate_pdf_report_clicked():
        data = {
            'test_id': test_id_entry.get(),
            'collection_date': sample_date_entry.get(),
            'latitude': float(latitude_entry.get().strip()),
            'longitude': float(longitude_entry.get().strip()),
            'name': name_entry.get(),
            'area': float(area_entry.get()),
            'gender': gender_var.get(),
            'age': int(age_entry.get()),
            'address': address_entry.get(),
            'mobile_no': mobile_entry.get(),
            'soil_ph': float(entries[0].get()),
            'nitrogen': float(entries[1].get()),
            'phosphorus': float(entries[2].get()),
            'potassium': float(entries[3].get()),
            'electrical_conductivity': float(entries[4].get()),
            'temperature': float(entries[5].get()),
            'moisture': float(entries[6].get()),
            'humidity': float(entries[7].get()),
            'soil_health_score': assess_soil_health([float(entry.get()) for entry in entries]),
            'recommendations': generate_crop_recommendations(
                assess_soil_health([float(entry.get()) for entry in entries]))
        }
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")],
                                                 initialfile=f"{data['test_id']}_report.pdf")
        if file_path:
            generate_pdf_report(data, file_path)
            tk.messagebox.showinfo("Report Confirmation", "Soil Health Report Generated Successfully")
            display_pdf_report(file_path, pdf_display_frame)
            disable_input_fields()
            clear_button.config(state=tk.DISABLED)
            assess_button.config(state=tk.DISABLED)
            save_export_button.config(state=tk.DISABLED)
            report_button.config(state=tk.DISABLED)
            new_test_button.config(state=tk.NORMAL)

    def save_export_button_clicked():
        test_id = test_id_entry.get()
        file_path = export_to_csv(test_id)
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
        close_pdf_report()

    def enable_assess_button():
        if all(entry.get() for entry in info_entries) and all(entry.get() for entry in entries):
            assess_button.config(state=tk.NORMAL)
        else:
            assess_button.config(state=tk.DISABLED)

    def enable_input_fields():
        test_id_label.config(foreground="black")
        test_id_entry.config(state=tk.NORMAL)
        sample_date_label.config(foreground="black")
        sample_date_entry.config(state=tk.NORMAL)
        sample_date_entry.bind("<1>",
                               lambda event: on_sample_date_click(event, info_frame))  # Enable the click event binding
        gps_label.config(foreground="black")
        latitude_entry.config(state=tk.NORMAL)
        longitude_entry.config(state=tk.NORMAL)
        name_label.config(foreground="black")
        name_entry.config(state=tk.NORMAL)
        area_label.config(foreground="black")
        area_entry.config(state=tk.NORMAL)
        gender_label.config(foreground="black")
        gender_dropdown.config(state="readonly")
        age_label.config(foreground="black")
        age_entry.config(state=tk.NORMAL)
        address_label.config(foreground="black")
        address_entry.config(state=tk.NORMAL)
        mobile_label.config(foreground="black")
        mobile_entry.config(state=tk.NORMAL)
        for label, entry in zip(labels, entries):
            label.config(foreground="black")
            entry.config(state=tk.NORMAL)

    def disable_input_fields():
        test_id_label.config(foreground="gray")
        test_id_entry.config(state=tk.DISABLED)
        sample_date_label.config(foreground="gray")
        sample_date_entry.config(state=tk.DISABLED)
        sample_date_entry.unbind("<1>")  # Remove the click event binding
        gps_label.config(foreground="gray")
        latitude_entry.config(state=tk.DISABLED)
        longitude_entry.config(state=tk.DISABLED)
        name_label.config(foreground="gray")
        name_entry.config(state=tk.DISABLED)
        area_label.config(foreground="gray")
        area_entry.config(state=tk.DISABLED)
        gender_label.config(foreground="gray")
        gender_dropdown.config(state=tk.DISABLED)
        age_label.config(foreground="gray")
        age_entry.config(state=tk.DISABLED)
        address_label.config(foreground="gray")
        address_entry.config(state=tk.DISABLED)
        mobile_label.config(foreground="gray")
        mobile_entry.config(state=tk.DISABLED)
        for label, entry in zip(labels, entries):
            label.config(foreground="gray")
            entry.config(state=tk.DISABLED)

    # Create a frame for the buttons
    button_frame = ttk.Frame(window)
    button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)  # Use grid instead of pack

    # Resize the images to fit the buttons
    button_width = 20
    button_height = 20

    new_image = Image.open('new.png')
    new_image = new_image.resize((button_width, button_height), Image.LANCZOS)
    new_icon = ImageTk.PhotoImage(new_image)

    clear_image = Image.open('clear.png')
    clear_image = clear_image.resize((button_width, button_height), Image.LANCZOS)
    clear_icon = ImageTk.PhotoImage(clear_image)

    assess_image = Image.open('assess.png')
    assess_image = assess_image.resize((button_width, button_height), Image.LANCZOS)
    assess_icon = ImageTk.PhotoImage(assess_image)

    export_image = Image.open('export.png')
    export_image = export_image.resize((button_width, button_height), Image.LANCZOS)
    export_icon = ImageTk.PhotoImage(export_image)

    report_image = Image.open('report.png')
    report_image = report_image.resize((button_width, button_height), Image.LANCZOS)
    report_icon = ImageTk.PhotoImage(report_image)

    # Create the 'New Test' button with the resized image
    new_test_button = ttk.Button(button_frame, text="New Test", command=new_test_button_clicked, image=new_icon,
                                 compound=tk.LEFT)
    new_test_button.image = new_icon
    new_test_button.pack(side='left', padx=5)

    # Create the 'Clear' button with the resized image
    clear_button = ttk.Button(button_frame, text="Clear", command=clear_button_clicked, image=clear_icon,
                              compound=tk.LEFT)
    clear_button.image = clear_icon
    clear_button.pack(side='left', padx=5)
    clear_button.config(state=tk.DISABLED)

    # Create the 'Assess Soil Health' button with the resized image
    assess_button = ttk.Button(button_frame, text="Assess Soil Health", command=assess_button_clicked,
                               image=assess_icon, compound=tk.LEFT)
    assess_button.image = assess_icon
    assess_button.pack(side='left', padx=5)
    assess_button.config(state=tk.DISABLED)

    # Create the 'Save & Export' button with the resized image
    save_export_button = ttk.Button(button_frame, text="Save & Export", command=save_export_button_clicked,
                                    image=export_icon, compound=tk.LEFT)
    save_export_button.image = export_icon
    save_export_button.pack(side='left', padx=5)
    save_export_button.config(state=tk.DISABLED)

    # Create the 'Generate Report' button with the resized image
    report_button = ttk.Button(button_frame, text="Generate Report", command=generate_pdf_report_clicked,
                               image=report_icon, compound=tk.LEFT)
    report_button.image = report_icon
    report_button.pack(side='left', padx=5)
    report_button.config(state=tk.DISABLED)

    # Disable input fields initially
    disable_input_fields()

    # Bind the entry fields to enable the 'Assess Soil Health' button when all fields are filled
    for entry in info_entries:
        if isinstance(entry, tk.Entry):
            entry.bind("<KeyRelease>", lambda event: enable_assess_button())
        elif isinstance(entry, tk.StringVar):
            entry.trace("w", lambda *args: enable_assess_button())

    for entry in entries:
        entry.bind("<KeyRelease>", lambda event: enable_assess_button())

    # Create labels to display the soil health score and recommendations
    result_label = ttk.Label(window, text="")
    result_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)  # Use grid instead of pack
    recommendations_label = ttk.Label(window, text="", wraplength=400)
    recommendations_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)  # Use grid instead of pack

    # Create a frame to hold the PDF report
    pdf_display_frame = ttk.Frame(window)
    pdf_display_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
    pdf_display_frame.grid_rowconfigure(0, weight=1)
    pdf_display_frame.grid_columnconfigure(0, weight=1)

    def visualize_results(indicator_values, soil_health_score, visualization_frame):
        # Clear the existing visualization
        for widget in visualization_frame.winfo_children():
            widget.destroy()

        # Create a radar chart
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw={'projection': 'polar'})
        angles = np.linspace(0, 2 * np.pi, len(soil_indicators), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))
        indicator_values = np.concatenate((indicator_values, [indicator_values[0]]))

        ax.plot(angles, indicator_values, 'o-', linewidth=1)
        ax.fill(angles, indicator_values, alpha=0.25)

        # Modify the labels for each soil indicator
        labels = [
            'pH',
            'N',
            'P',
            'K',
            'EC',
            'Temp',
            'Moist',
            'Humid'
        ]
        ax.set_thetagrids(angles[:-1] * 180 / np.pi, labels)

        ax.set_title("Soil Health Indicators", fontsize=10)
        ax.grid(True)

        # Embed the chart in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=visualization_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    return window

#Create the database table

create_database()

#Create the main window

window = create_gui()
window.mainloop()