import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox  # Add 'messagebox' to the import statement
from PIL import Image as PILImage, ImageTk

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

def save_results(data):
    conn = sqlite3.connect('soil_health.db')
    c = conn.cursor()

    # Create the soil_tests table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS soil_tests
                     (test_id INTEGER PRIMARY KEY,
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

    c.execute('''INSERT INTO soil_tests
                     (test_id, collection_date, latitude, longitude, name, area, gender, age, address, mobile_no,
                      soil_ph, nitrogen, phosphorus, potassium, electrical_conductivity, temperature, moisture, humidity,
                      soil_health_score, recommendations)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (data['test_id'], data['collection_date'], data['latitude'], data['longitude'], data['name'],
               data['area'], data['gender'], data['age'], data['address'], data['mobile_no'], data['soil_ph'],
               data['nitrogen'], data['phosphorus'], data['potassium'], data['electrical_conductivity'],
               data['temperature'], data['moisture'], data['humidity'], data['soil_health_score'],
               str(data['recommendations'])))

    conn.commit()
    conn.close()

def view_database(window):
    # Create a new window for database browsing
    db_window = tk.Toplevel(window)
    db_window.title("Soil Health Database")

    # Create a Treeview widget to display the records
    tree = ttk.Treeview(db_window, show="headings")  # Add show="headings" to hide the empty first column
    tree["columns"] = (
    "id", "test_id", "collection_date", "latitude", "longitude", "name", "area", "gender", "age", "address",
    "mobile_no", "soil_ph", "nitrogen", "phosphorus", "potassium", "electrical_conductivity", "temperature", "moisture",
    "humidity", "soil_health_score", "recommendations")
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
        selected_item = tree.focus()
        if selected_item:
            test_id = tree.item(selected_item)['values'][1]  # Get the test_id from the selected row
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")],
                                                     initialfile=f"{test_id}_test.xlsx")
            if file_path:
                conn = sqlite3.connect('soil_health.db')
                c = conn.cursor()
                c.execute("SELECT * FROM soil_tests WHERE test_id = ?", (test_id,))
                data = c.fetchall()
                conn.close()

                workbook = openpyxl.Workbook()
                sheet = workbook.active
                sheet.append(
                    ["ID", "Test ID", "Collection Date", "Latitude", "Longitude", "Name", "Area (ha)", "Gender", "Age",
                     "Address", "Mobile No.", "Soil pH", "Nitrogen", "Phosphorus", "Potassium",
                     "Electrical Conductivity", "Temperature", "Moisture", "Humidity", "Soil Health Score",
                     "Recommendations"])
                for row in data:
                    sheet.append(row)
                workbook.save(file_path)
                messagebox.showinfo("Export", "Records exported to Excel successfully.")
        else:
            messagebox.showwarning("No Selection", "Please select a record to export.")

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