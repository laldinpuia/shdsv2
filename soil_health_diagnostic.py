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
from reportlab.platypus import SimpleDocTemplate, Image as ReportLabImage, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from indicators import soil_indicators
from fahp import fahp_weights, evaluate_soil_health
from assessment import assess_soil_health, generate_rating, generate_crop_recommendations
from PIL import Image as PILImage, ImageTk
from tkcalendar import Calendar
import openpyxl

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

def generate_pdf_report(data, file_path, indicator_values):
    report = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()

    # Create a custom style for Heading3 if it doesn't exist
    if 'Heading3' not in styles:
        styles.add(ParagraphStyle(name='Heading3', fontName='Helvetica-Bold', fontSize=12, alignment=TA_CENTER))

    # Modify the title style to use a smaller font size and center alignment
    styles["Title"].fontSize = 16
    styles["Title"].alignment = TA_CENTER

    report_elements = [Paragraph("Soil Health Report", styles["Title"]), Spacer(1, 0.2 * inch)]

    # Farmer Information
    farmer_info = [
        ['Name', data['name']],
        ['Gender', data['gender']],
        ['Age', data['age']],
        ['Address', data['address']],
        ['Mobile No.', data['mobile_no']],
        ['Area (ha)', data['area']]
    ]
    farmer_table = Table(farmer_info)
    farmer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
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
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
    ]))

    # Create a table to hold both farmer information and sample details tables
    info_table = Table([[farmer_table, sample_details_table]])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
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
    report_elements.append(Spacer(1, 0.2 * inch))

    # Soil Health Indicators
    table_data = [['Soil Health Indicators', 'Values', 'Normal Values']]
    for indicator in soil_indicators:
        indicator_name = indicator.name.lower().replace(' ', '_').replace('(', '').replace(')', '')
        value = data.get(indicator_name, 'N/A')
        normal_value = indicator.optimal_range
        table_data.append([str(indicator), value, f"{normal_value[0]} - {normal_value[1]} {indicator.unit}"])
    table_data.append(['Soil Health Score', f"{data['soil_health_score']:.2f}", '0 - 1'])
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
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
    ]))

    report_elements.append(Paragraph("Soil Health Indicators", styles["Heading3"]))
    report_elements.append(table)
    report_elements.append(Spacer(1, 0.2 * inch))

    # Create the radar chart
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})
    angles = np.linspace(0, 2 * np.pi, len(soil_indicators), endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))
    indicator_values = np.concatenate((indicator_values, [indicator_values[0]]))

    ax.plot(angles, indicator_values, 'o-', linewidth=1)
    ax.fill(angles, indicator_values, alpha=0.25)

    # Modify the labels for each soil indicator

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

    # Save the radar chart as an image in memory
    chart_buffer = io.BytesIO()
    plt.savefig(chart_buffer, format='png', dpi=300, bbox_inches='tight')
    chart_buffer.seek(0)
    chart_img = ReportLabImage(chart_buffer, width=3 * inch, height=3 * inch)
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


def export_to_excel(test_id):
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")], initialfile=f"{test_id}_test.xlsx")
    if file_path:
        conn = sqlite3.connect('soil_health.db')
        c = conn.cursor()
        c.execute("SELECT * FROM soil_tests WHERE test_id = ?", (test_id,))
        data = c.fetchall()
        conn.close()

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(['ID', 'Test ID', 'Sample Collection Date', 'Latitude', 'Longitude', 'Name', 'Area (ha)', 'Gender',
                      'Age', 'Address', 'Mobile No.', 'Soil pH', 'Nitrogen', 'Phosphorus', 'Potassium',
                      'Electrical Conductivity', 'Temperature', 'Moisture', 'Humidity', 'Soil Health Score',
                      'Crop Recommendations'])
        for row in data:
            sheet.append(row)
        workbook.save(file_path)
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

def view_database():
    # Create a new window for database browsing
    db_window = tk.Toplevel(window)
    db_window.title("Soil Health Database")

    # Create a Treeview widget to display the records
    tree = ttk.Treeview(db_window, show="headings")  # Add show="headings" to hide the empty first column
    tree["columns"] = ("id", "test_id", "collection_date", "latitude", "longitude", "name", "area", "gender", "age", "address", "mobile_no", "soil_ph", "nitrogen", "phosphorus", "potassium", "electrical_conductivity", "temperature", "moisture", "humidity", "soil_health_score", "recommendations")
    tree.heading("id", text="ID")
    tree.heading("test_id", text="Test ID")
    tree.heading("collection_date", text="Collection Date")
    tree.heading("latitude", text="Latitude")
    tree.heading("longitude", text="Longitude")
    tree.heading("name", text="Name")
    tree.heading("area", text="Area (ha)")
    tree.heading("gender", text="Gender")
    tree.heading("age", text="Age")
    tree.heading("address", text="Address")
    tree.heading("mobile_no", text="Mobile No.")
    tree.heading("soil_ph", text="Soil pH")
    tree.heading("nitrogen", text="Nitrogen")
    tree.heading("phosphorus", text="Phosphorus")
    tree.heading("potassium", text="Potassium")
    tree.heading("electrical_conductivity", text="Electrical Conductivity")
    tree.heading("temperature", text="Temperature")
    tree.heading("moisture", text="Moisture")
    tree.heading("humidity", text="Humidity")
    tree.heading("soil_health_score", text="Soil Health Score")
    tree.heading("recommendations", text="Recommendations")

    # Set column widths
    tree.column("id", width=50)
    tree.column("test_id", width=100)
    tree.column("collection_date", width=120)
    tree.column("latitude", width=100)
    tree.column("longitude", width=100)
    tree.column("name", width=150)
    tree.column("area", width=100)
    tree.column("gender", width=80)
    tree.column("age", width=50)
    tree.column("address", width=200)
    tree.column("mobile_no", width=120)
    tree.column("soil_ph", width=80)
    tree.column("nitrogen", width=80)
    tree.column("phosphorus", width=80)
    tree.column("potassium", width=80)
    tree.column("electrical_conductivity", width=150)
    tree.column("temperature", width=100)
    tree.column("moisture", width=80)
    tree.column("humidity", width=80)
    tree.column("soil_health_score", width=120)
    tree.column("recommendations", width=200)

    # Create a frame for sorting and filtering options
    options_frame = ttk.Frame(db_window)
    options_frame.pack(pady=10)

    # Create a dropdown for selecting the sorting column
    sort_label = ttk.Label(options_frame, text="Sort by:")
    sort_label.pack(side=tk.LEFT, padx=5)
    sort_var = tk.StringVar()
    sort_dropdown = ttk.Combobox(options_frame, textvariable=sort_var,
                                 values=["ID", "Test ID", "Collection Date", "Name", "Soil Health Score"],
                                 state="readonly")
    sort_dropdown.pack(side=tk.LEFT, padx=5)
    sort_dropdown.current(0)  # Set default sorting to ID

    # Create an entry field for filtering records
    filter_label = ttk.Label(options_frame, text="Filter:")
    filter_label.pack(side=tk.LEFT, padx=5)
    filter_entry = ttk.Entry(options_frame)
    filter_entry.pack(side=tk.LEFT, padx=5)

    # Create a button to apply sorting and filtering
    def apply_options():
        # Get the selected sorting column and filter text
        sort_column = sort_var.get()
        filter_text = filter_entry.get().strip()

        # Clear existing records in the Treeview
        tree.delete(*tree.get_children())

        # Connect to the database and retrieve records
        conn = sqlite3.connect('soil_health.db')
        c = conn.cursor()

        # Prepare the SQL query based on sorting and filtering options
        query = "SELECT * FROM soil_tests"
        if filter_text:
            query += f" WHERE name LIKE '%{filter_text}%' OR test_id LIKE '%{filter_text}%'"
        if sort_column == "ID":
            query += " ORDER BY id"
        elif sort_column == "Test ID":
            query += " ORDER BY test_id"
        elif sort_column == "Collection Date":
            query += " ORDER BY collection_date"
        elif sort_column == "Name":
            query += " ORDER BY name"
        elif sort_column == "Soil Health Score":
            query += " ORDER BY soil_health_score"

        c.execute(query)
        records = c.fetchall()
        conn.close()

        # Insert the sorted and filtered records into the Treeview
        for record in records:
            tree.insert("", "end", values=record)

    # Load the 'apply.png' icon
    apply_icon = PILImage.open('apply.png')
    apply_icon = apply_icon.resize((20, 20), PILImage.LANCZOS)
    apply_photo = ImageTk.PhotoImage(apply_icon)

    apply_button = ttk.Button(options_frame, text="Apply", command=apply_options, image=apply_photo, compound=tk.LEFT)
    apply_button.image = apply_photo  # Keep a reference to the image to prevent garbage collection
    apply_button.pack(side=tk.LEFT, padx=5)

    # Create a button to export the records to Excel (.xlsx)
    def export_to_excel():
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.append(
                ["ID", "Test ID", "Collection Date", "Latitude", "Longitude", "Name", "Area (ha)", "Gender", "Age",
                 "Address", "Mobile No.", "Soil pH", "Nitrogen", "Phosphorus", "Potassium",
                 "Electrical Conductivity", "Temperature", "Moisture", "Humidity", "Soil Health Score",
                 "Recommendations"])
            for record in tree.get_children():
                values = tree.item(record)['values']
                sheet.append(values)
            workbook.save(file_path)
            messagebox.showinfo("Export", "Records exported to Excel successfully.")

    # Load the 'excel.png' icon
    excel_icon = PILImage.open('excel.png')
    excel_icon = excel_icon.resize((20, 20), PILImage.LANCZOS)
    excel_photo = ImageTk.PhotoImage(excel_icon)

    export_button = ttk.Button(db_window, text="Export to Excel (.xlsx)", command=export_to_excel, image=excel_photo,
                               compound=tk.LEFT)
    export_button.image = excel_photo  # Keep a reference to the image to prevent garbage collection
    export_button.pack(pady=10)

    # Retrieve and display the initial records
    apply_options()

    tree.pack(expand=True, fill=tk.BOTH)

    # Load the 'close.png' icon
    close_icon = PILImage.open('close.png')
    close_icon = close_icon.resize((20, 20), PILImage.LANCZOS)
    close_photo = ImageTk.PhotoImage(close_icon)

    # Add a button to close the database browsing window
    close_button = ttk.Button(db_window, text="Close", command=db_window.destroy, image=close_photo, compound=tk.LEFT)
    close_button.image = close_photo  # Keep a reference to the image to prevent garbage collection
    close_button.pack(pady=10)

def validate_gps_entry(P):
    if P == "":
        return True
    try:
        float_value = float(P)
        return -180 <= float_value <= 180
    except ValueError:
        return False

def validate_name_entry(P):
    if len(P) <= 60 and re.match(r"^[A-Za-z.\s]*$", P):
        return True
    else:
        return False

def validate_area_entry(P):
    if P == "":
        return True
    elif re.match(r"^\d+(\.\d{0,2})?$", P):
        return 0 <= float(P) <= 50
    else:
        return False

def validate_soil_ph(P):
    if P == "":
        return True
    elif re.match(r"^\d+(\.\d{0,2})?$", P):
        return 0 <= float(P) <= 8.50
    else:
        return False

def validate_nitrogen(P):
    if P == "":
        return True
    try:
        value = float(P)
        return 10 <= value <= 500
    except ValueError:
        return False

def validate_phosphorus(P):
    if P == "":
        return True
    try:
        value = float(P)
        return 10 <= value <= 200
    except ValueError:
        return False

def validate_potassium(P):
    if P == "":
        return True
    try:
        value = float(P)
        return 10 <= value <= 400
    except ValueError:
        return False

def validate_electrical_conductivity(P):
    if P == "":
        return True
    elif re.match(r"^\d+(\.\d{0,2})?$", P):
        return 0 <= float(P) <= 4
    else:
        return False
def validate_temperature(P):
    if P == "":
        return True
    try:
        value = int(P)
        return 0 <= value <= 50
    except ValueError:
        return False

def validate_moisture(P):
    if P == "":
        return True
    try:
        value = int(P)
        return 0 <= value <= 100
    except ValueError:
        return False

def validate_humidity(P):
    if P == "":
        return True
    try:
        value = int(P)
        return 0 <= value <= 100
    except ValueError:
        return False
def create_gui():
    window = ThemedTk(theme="ubuntu")  # Use the "ubuntu" theme
    window.title("Soil Health Diagnostic System")

    # Set the main icon of the program
    icon = PILImage.open("main.ico")
    window.iconphoto(True, ImageTk.PhotoImage(icon))

    # Configure the weights for the rows and columns
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)
    window.grid_columnconfigure(2, weight=2)  # Give more weight to the third column
    window.grid_rowconfigure(0, weight=1)

    # Load the image for the soil health indicators label
    label_image = PILImage.open('shi.png')
    label_image = label_image.resize((30, 30), PILImage.Resampling.LANCZOS)
    label_icon = ImageTk.PhotoImage(label_image)

    # Load the image for the farmer information label
    farmer_image = PILImage.open('farmer.png')
    farmer_image = farmer_image.resize((30, 30), PILImage.Resampling.LANCZOS)
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

    latitude_entry = ttk.Entry(gps_frame, validate='key',
                               validatecommand=(info_frame.register(validate_gps_entry), '%P'))
    latitude_entry.grid(row=0, column=0, sticky='ew', padx=(0, 5))
    latitude_label = ttk.Label(gps_frame, text="° N")
    latitude_label.grid(row=0, column=1, sticky='w')

    longitude_entry = ttk.Entry(gps_frame, validate='key',
                                validatecommand=(info_frame.register(validate_gps_entry), '%P'))
    longitude_entry.grid(row=0, column=2, sticky='ew', padx=(5, 0))
    longitude_label = ttk.Label(gps_frame, text="° E")
    longitude_label.grid(row=0, column=3, sticky='w')

    info_entries.extend([latitude_entry, longitude_entry])

    # Name field
    name_label = ttk.Label(info_frame, text='Name')
    name_label.grid(row=3, column=0, sticky='w', padx=5, pady=5)
    name_entry = ttk.Entry(info_frame, validate='key', validatecommand=(info_frame.register(validate_name_entry), '%P'))
    name_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
    info_entries.append(name_entry)

    # Area (ha) field
    area_label = ttk.Label(info_frame, text='Area (ha)')
    area_label.grid(row=4, column=0, sticky='w', padx=5, pady=5)
    area_entry = ttk.Entry(info_frame, validate='key', validatecommand=(info_frame.register(validate_area_entry), '%P'))
    area_entry.grid(row=4, column=1, sticky='ew', padx=5, pady=5)
    area_entry.bind("<Tab>", lambda event, entry=area_entry: on_area_tab(event, gender_dropdown))
    info_entries.append(area_entry)

    # Gender field
    gender_label = ttk.Label(info_frame, text='Gender')
    gender_label.grid(row=5, column=0, sticky='w', padx=5, pady=5)
    gender_var = tk.StringVar()
    gender_dropdown = ttk.Combobox(info_frame, textvariable=gender_var, values=['Male', 'Female', 'Others'], state='readonly')
    gender_dropdown.grid(row=5, column=1, sticky='ew', padx=5, pady=5)
    info_entries.append(gender_var)

    # Age field
    age_label = ttk.Label(info_frame, text='Age')
    age_label.grid(row=6, column=0, sticky='w', padx=5, pady=5)
    age_entry = ttk.Entry(info_frame)
    age_entry.grid(row=6, column=1, sticky='ew', padx=5, pady=5)
    age_entry.config(validate='key',
                     validatecommand=(
                         info_frame.register(lambda P: (P.isdigit() and (1 <= int(P) <= 99)) or P == ''), '%P'))
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
    label_image = PILImage.open('shi.png')
    label_image = label_image.resize((30, 30), PILImage.Resampling.LANCZOS)
    label_icon = ImageTk.PhotoImage(label_image)

    # Create a label with the image and text for soil health indicators
    label = ttk.Label(window, text="Soil Health Indicators", font=("Helvetica", 14, "bold"), image=label_icon,
                      compound=tk.LEFT)
    label.image = label_icon  # Keep a reference to the image to prevent garbage collection

    # Use the label as the labelwidget for the LabelFrame
    input_frame = ttk.LabelFrame(window, labelwidget=label)
    input_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
    input_frame.grid_columnconfigure(1, weight=1)  # Make the entry fields expand

    # Create a frame to hold the visualization (radar chart and result labels)
    visualization_frame = ttk.Frame(window)
    visualization_frame.grid(row=0, column=2, sticky='nsew', padx=10, pady=10)
    visualization_frame.grid_rowconfigure(0, weight=1)
    visualization_frame.grid_columnconfigure(0, weight=1)

    # Hide the visualization frame initially
    visualization_frame.grid_remove()

    # Create labels and entry fields for each soil indicator
    labels = []
    entries = []
    validation_functions = [
        validate_soil_ph,
        validate_nitrogen,
        validate_phosphorus,
        validate_potassium,
        validate_electrical_conductivity,
        validate_temperature,
        validate_moisture,
        validate_humidity
    ]

    for i, (indicator, validation_func) in enumerate(zip(soil_indicators, validation_functions)):
        label = ttk.Label(input_frame, text=str(indicator))
        label.grid(row=i, column=0, sticky='w', padx=5, pady=5)
        entry = ttk.Entry(input_frame, validate='key', validatecommand=(input_frame.register(validation_func), '%P'))
        entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
        labels.append(label)
        entries.append(entry)

    # Create a button to trigger the soil health assessment
    def assess_button_clicked():
        # Disable and grey out the input fields in the Farmer Information and Soil Health Indicators frame
        disable_input_fields()
        for label, entry in zip(labels, entries):
            label.config(foreground="gray")
            entry.config(state=tk.DISABLED)

        # Validate the input fields
        try:
            indicator_values = []
            for entry, indicator in zip(entries, soil_indicators):
                value = entry.get().strip()
                if value == "":
                    indicator_values.append(None)
                else:
                    value = float(value)
                    if not indicator.min_value <= value <= indicator.max_value:
                        raise ValueError(f"Invalid value for {indicator.name}: {value}")
                    indicator_values.append(value)

            latitude = float(latitude_entry.get().strip())
            longitude = float(longitude_entry.get().strip())

            if gender_var.get() == "":
                raise ValueError("Please select a gender")

            # Normalize the indicator values based on their ranges
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

            visualize_results(indicator_values, soil_health_score, visualization_frame)

            save_results(data)

            save_export_button.config(state=tk.NORMAL)
            report_button.config(state=tk.DISABLED)
            clear_button.config(state=tk.NORMAL)

            # Show the visualization frame
            visualization_frame.grid()
        except ValueError as e:
            tk.messagebox.showerror("Invalid Input", str(e))

    # Create a function to clear all the input fields
    def clear_button_clicked():
        enable_input_fields()
        clear_button.config(state=tk.NORMAL)  # Enable the 'Clear' button
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

        # Clear all input fields
        for entry in info_entries:
            if isinstance(entry, tk.Entry):
                entry.delete(0, tk.END)  # Replace 'end' with tk.END
            elif isinstance(entry, tk.StringVar):
                entry.set('')
        for entry in entries:
            entry.delete(0, tk.END)  # Replace 'end' with tk.END

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
            indicator_values = [float(entry.get()) for entry in entries]  # Get the indicator values from the entries
            generate_pdf_report(data, file_path, indicator_values)  # Pass indicator_values as an argument
            tk.messagebox.showinfo("Report Confirmation", "Soil Health Report Generated Successfully")
            disable_all_elements()  # Disable all elements except for the 'New Test' button
            new_test_button.config(state=tk.NORMAL)  # Enable the 'New Test' button

    def save_export_button_clicked():
        test_id = test_id_entry.get()
        file_path = export_to_excel(test_id)
        if file_path:
            tk.messagebox.showinfo("Save Confirmation", "Soil Test Report Saved Successfully")
            report_button.config(state=tk.NORMAL)

    def new_test_button_clicked():
        clear_button_clicked()
        enable_input_fields()
        clear_button.config(state=tk.NORMAL)  # Enable the 'Clear' button
        assess_button.config(state=tk.DISABLED)
        save_export_button.config(state=tk.DISABLED)
        report_button.config(state=tk.DISABLED)

        # Clear the radar chart frame and soil health recommendations frames and labels
        for widget in visualization_frame.winfo_children():
            widget.destroy()

        # Resize the program window to its normal state
        window.geometry("")  # Set an empty geometry to reset the window size
        window.update()  # Update the window to apply the changes

        # Hide the visualization frame
        visualization_frame.grid_remove()

        # Clear all input fields
        for entry in info_entries:
            if isinstance(entry, tk.Entry):
                entry.delete(0, tk.END)  # Replace 'end' with tk.END
            elif isinstance(entry, tk.StringVar):
                entry.set('')
        for entry in entries:
            entry.delete(0, tk.END)  # Replace 'end' with tk.END

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
                               lambda event: on_sample_date_click(event, info_frame,
                                                                  sample_date_entry))  # Pass sample_date_entry as an argument
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

    # Create a frame for the buttons

    button_frame = ttk.Frame(window)
    button_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="we")  # Use grid instead of pack

    # Configure the button frame to expand horizontally

    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)
    button_frame.columnconfigure(2, weight=1)
    button_frame.columnconfigure(3, weight=1)
    button_frame.columnconfigure(4, weight=1)
    button_frame.columnconfigure(5, weight=1)

    # Resize the images to fit the buttons
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

    # Load the 'database.png' icon
    database_icon = PILImage.open('database.png')
    database_icon = database_icon.resize((20, 20), PILImage.LANCZOS)
    database_photo = ImageTk.PhotoImage(database_icon)

    # Create the 'New Test' button with the resized image
    new_test_button = ttk.Button(button_frame, text="New Test", command=new_test_button_clicked, image=new_icon,
                                 compound=tk.LEFT)
    new_test_button.image = new_icon
    new_test_button.grid(row=0, column=0, padx=5, sticky="we")  # Use grid instead of pack

    # Create the 'Clear' button with the resized image
    clear_button = ttk.Button(button_frame, text="Clear", command=clear_button_clicked, image=clear_icon,
                              compound=tk.LEFT)
    clear_button.image = clear_icon
    clear_button.grid(row=0, column=1, padx=5, sticky="we")  # Use grid instead of pack
    clear_button.config(state=tk.NORMAL)  # Enable the 'Clear' button initially

    # Create the 'Assess Soil Health' button with the resized image
    assess_button = ttk.Button(button_frame, text="Assess Soil Health", command=assess_button_clicked,
                               image=assess_icon, compound=tk.LEFT)
    assess_button.image = assess_icon
    assess_button.grid(row=0, column=2, padx=5, sticky="we")  # Use grid instead of pack
    assess_button.config(state=tk.DISABLED)

    # Create the 'Save & Export' button with the resized image
    save_export_button = ttk.Button(button_frame, text="Save & Export", command=save_export_button_clicked,
                                    image=export_icon, compound=tk.LEFT)
    save_export_button.image = export_icon
    save_export_button.grid(row=0, column=3, padx=5, sticky="we")  # Use grid instead of pack
    save_export_button.config(state=tk.DISABLED)

    # Create the 'Generate Report' button with the resized image
    report_button = ttk.Button(button_frame, text="Generate Report", command=generate_pdf_report_clicked,
                               image=report_icon, compound=tk.LEFT)
    report_button.image = report_icon
    report_button.grid(row=0, column=4, padx=5, sticky="we")  # Use grid instead of pack
    report_button.config(state=tk.DISABLED)

    # Create the 'View Database' button with the icon
    view_database_button = ttk.Button(button_frame, text="View Database", command=view_database, image=database_photo,
                                      compound=tk.LEFT)
    view_database_button.image = database_photo  # Keep a reference to the image to prevent garbage collection
    view_database_button.grid(row=0, column=5, padx=5, sticky="we")  # Use grid instead of pack

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
    # result_label = ttk.Label(window, text="")
    # result_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)  # Use grid instead of pack
    # recommendations_label = ttk.Label(window, text="", wraplength=400)
    # recommendations_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)  # Use grid instead of pack

    def visualize_results(indicator_values, soil_health_score, visualization_frame):
        # Clear the existing visualization
        for widget in visualization_frame.winfo_children():
            widget.destroy()

        # Create a frame to hold the radar chart and result labels
        visualization_content_frame = ttk.Frame(visualization_frame)
        visualization_content_frame.pack(fill=tk.BOTH, expand=True)

        # Create a frame to hold the radar chart
        radar_chart_frame = ttk.Frame(visualization_content_frame)
        radar_chart_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create a radar chart
        fig, ax = plt.subplots(figsize=(4.5, 4.5), subplot_kw={'projection': 'polar'})
        angles = np.linspace(0, 2 * np.pi, len(soil_indicators), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))
        indicator_values = np.concatenate((indicator_values, [indicator_values[0]]))

        ax.plot(angles, indicator_values, 'o-', linewidth=1)
        ax.fill(angles, indicator_values, alpha=0.25)

        # Modify the labels for each soil indicator
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

        # Embed the chart in the radar_chart_frame
        canvas = FigureCanvasTkAgg(fig, master=radar_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Adjust the window size to properly display the radar chart
        # window.update_idletasks()  # Update the window to calculate the required size
        # required_width = window.winfo_reqwidth()
        # required_height = window.winfo_reqheight()
        # screen_width = window.winfo_screenwidth()
        # screen_height = window.winfo_screenheight()
        # window_width = min(required_width, screen_width - 100)  # Limit the window width to fit the screen
        # window_height = min(required_height, screen_height - 100)  # Limit the window height to fit the screen
        # window.geometry(f"{window_width}x{window_height}")  # Set the window size based on the required size
        # window.update()  # Update the window to apply the changes

        # Create a frame to hold the result labels
        result_frame = ttk.Frame(visualization_content_frame)
        result_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create a frame to center the result labels
        center_frame = ttk.Frame(result_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Create labels to display the soil health score and recommendations
        result_label = ttk.Label(result_frame, text=f"Soil Health Score:{soil_health_score:.2f}",
                                 font=("Helvetica", 10, "bold"))
        result_label.pack(side=tk.TOP, padx=10)

        recommendations_text = f"\nCrop Recommendations:\n{generate_crop_recommendations(soil_health_score)}"
        recommendations_label = ttk.Label(result_frame, text=recommendations_text, font=("Helvetica", 10, "bold"),
                                          justify=tk.CENTER, wraplength=400)
        recommendations_label.pack(side=tk.BOTTOM, padx=10)

        # Call the save_results function
        try:
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
            save_results(data)
        except ValueError as e:
            tk.messagebox.showerror("Invalid Input", str(e))

    return window

#Create the database table

create_database()

#Create the main window

window = create_gui()
window.mainloop()