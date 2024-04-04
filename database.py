import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox  # Add 'messagebox' to the import statement
from PIL import Image as PILImage, ImageTk
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
                  soil_health_score REAL(3,2),
                  recommendations TEXT)''')
    conn.commit()
    conn.close()

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
                  data['humidity'], round(data['soil_health_score'], 2), data['recommendations']))
    conn.commit()
    conn.close()

def view_database(window):
    # Create a new window for database browsing
    db_window = tk.Toplevel(window)
    db_window.title("Soil Health Database Viewer")

    # Configure the Treeview style
    style = ttk.Style()
    style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
    style.map("Treeview", background=[("selected", "#7ed957")])  # Set the selected row color to Ubuntu orange

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

    # Create a frame to hold the Treeview and scrollbar
    tree_frame = ttk.Frame(db_window)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    # Create a vertical scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a Treeview widget to display the records
    tree = ttk.Treeview(tree_frame, show="headings", yscrollcommand=scrollbar.set, height=15)
    tree["columns"] = (
        "id", "test_id", "collection_date", "latitude", "longitude", "name", "area", "gender", "age", "address",
        "mobile_no", "soil_ph", "nitrogen", "phosphorus", "potassium", "electrical_conductivity", "temperature",
        "moisture", "humidity", "soil_health_score", "recommendations")
    tree.heading("id", text="ID", command=lambda: sort_column("id"))
    tree.heading("test_id", text="Test ID", command=lambda: sort_column("test_id"))
    tree.heading("collection_date", text="Collection Date", command=lambda: sort_column("collection_date"))
    tree.heading("latitude", text="Latitude", command=lambda: sort_column("latitude"))
    tree.heading("longitude", text="Longitude", command=lambda: sort_column("longitude"))
    tree.heading("name", text="Name", command=lambda: sort_column("name"))
    tree.heading("area", text="Area (ha)", command=lambda: sort_column("area"))
    tree.heading("gender", text="Gender", command=lambda: sort_column("gender"))
    tree.heading("age", text="Age", command=lambda: sort_column("age"))
    tree.heading("address", text="Address", command=lambda: sort_column("address"))
    tree.heading("mobile_no", text="Mobile No.", command=lambda: sort_column("mobile_no"))
    tree.heading("soil_ph", text="Soil pH", command=lambda: sort_column("soil_ph"))
    tree.heading("nitrogen", text="Nitrogen", command=lambda: sort_column("nitrogen"))
    tree.heading("phosphorus", text="Phosphorus", command=lambda: sort_column("phosphorus"))
    tree.heading("potassium", text="Potassium", command=lambda: sort_column("potassium"))
    tree.heading("electrical_conductivity", text="Electrical Conductivity", command=lambda: sort_column("electrical_conductivity"))
    tree.heading("temperature", text="Temperature", command=lambda: sort_column("temperature"))
    tree.heading("moisture", text="Moisture", command=lambda: sort_column("moisture"))
    tree.heading("humidity", text="Humidity", command=lambda: sort_column("humidity"))
    tree.heading("soil_health_score", text="Soil Health Score", command=lambda: sort_column("soil_health_score"))
    tree.heading("recommendations", text="Recommendations", command=lambda: sort_column("recommendations"))

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

    # Configure the scrollbar to work with the Treeview
    scrollbar.config(command=tree.yview)

    # Load the sorting order icons
    ascending_icon = PILImage.open("ascending.png")
    ascending_icon = ascending_icon.resize((16, 16), PILImage.LANCZOS)
    ascending_photo = ImageTk.PhotoImage(ascending_icon)
    descending_icon = PILImage.open("descending.png")
    descending_icon = descending_icon.resize((16, 16), PILImage.LANCZOS)
    descending_photo = ImageTk.PhotoImage(descending_icon)

    # Keep references to the icon images to prevent garbage collection
    tree.ascending_photo = ascending_photo
    tree.descending_photo = descending_photo

    # Variables to store the current sorting column and order
    current_sorting_column = ""
    current_sorting_order = "ascending"

    def sort_column(column):
        nonlocal current_sorting_column, current_sorting_order

        # Determine the new sorting order
        if current_sorting_column == column:
            current_sorting_order = "descending" if current_sorting_order == "ascending" else "ascending"
        else:
            current_sorting_column = column
            current_sorting_order = "ascending"

        # Clear existing records in the Treeview
        tree.delete(*tree.get_children())

        # Connect to the database and retrieve records
        conn = sqlite3.connect('soil_health.db')
        c = conn.cursor()

        # Prepare the SQL query based on the sorting column and order
        query = f"SELECT * FROM soil_tests ORDER BY {column} {'ASC' if current_sorting_order == 'ascending' else 'DESC'}"
        c.execute(query)
        records = c.fetchall()
        conn.close()

        # Insert the sorted records into the Treeview
        for record in records:
            tree.insert("", "end", values=record)

        # Update the sorting order icon in the column header
        for col in tree["columns"]:
            tree.heading(col, image="")  # Clear the icon for all columns
        tree.heading(column, image=ascending_photo if current_sorting_order == "ascending" else descending_photo)

    # Bind the selection event to highlight the selected row
    def on_select(event):
        tree.tk.call(tree, "tag", "configure", "selected", "-background",
                     "#E95420")  # Set the selected row color to Ubuntu orange

    tree.bind("<<TreeviewSelect>>", on_select)

    # Create a button to delete the selected record from the database
    def delete_record():
        selected_item = tree.focus()
        if selected_item:
            values = tree.item(selected_item)['values']
            record_id = values[0]  # Get the ID of the selected record

            confirm = messagebox.askyesno("Delete Record", "Are you sure you want to delete this record permanently?")
            if confirm:
                conn = sqlite3.connect('soil_health.db')
                c = conn.cursor()
                c.execute("DELETE FROM soil_tests WHERE id=?", (record_id,))
                conn.commit()
                conn.close()
                tree.delete(selected_item)
                messagebox.showinfo("Delete", "Record deleted successfully.")
        else:
            messagebox.showwarning("No Selection", "Please select a record to delete.")

    # Load the 'delete.png' icon
    delete_icon = PILImage.open('delete.png')
    delete_icon = delete_icon.resize((20, 20), PILImage.LANCZOS)
    delete_photo = ImageTk.PhotoImage(delete_icon)

    delete_button = ttk.Button(db_window, text="Delete Record", command=delete_record, image=delete_photo,
                               compound=tk.LEFT)
    delete_button.image = delete_photo  # Keep a reference to the image to prevent garbage collection
    delete_button.pack(side=tk.TOP, padx=5)

    # Create a button to export the records to Excel (.xlsx)
    def export_to_excel():
        selected_item = tree.focus()
        if selected_item:
            values = tree.item(selected_item)['values']
            test_id = values[1]  # Get the test_id from the selected row
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")],
                                                     initialfile=f"{test_id}_test.xlsx")
            if file_path:
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                header = ["ID", "Test ID", "Collection Date", "Latitude", "Longitude", "Name", "Area (ha)", "Gender",
                          "Age",
                          "Address", "Mobile No.", "Soil pH", "Nitrogen", "Phosphorus", "Potassium",
                          "Electrical Conductivity", "Temperature", "Moisture", "Humidity", "Soil Health Score",
                          "Recommendations"]
                sheet.append(header)

                # Format the values based on their respective data types
                formatted_values = []
                for i, value in enumerate(values):
                    if i in [3, 4, 6, 11, 12, 13, 14, 15, 16, 17, 18, 19]:
                        formatted_values.append(round(float(value), 2) if value else None)
                    elif i == 8:
                        formatted_values.append(int(value) if value else None)
                    else:
                        formatted_values.append(value)

                sheet.append(formatted_values)
                workbook.save(file_path)
                messagebox.showinfo("Export", "Database Record exported to Excel successfully.")
        else:
            messagebox.showwarning("No Selection", "Please select a record to Export.")

    # Load the 'excel.png' icon
    excel_icon = PILImage.open('excel.png')
    excel_icon = excel_icon.resize((20, 20), PILImage.LANCZOS)
    excel_photo = ImageTk.PhotoImage(excel_icon)

    export_button = ttk.Button(db_window, text="Export to Excel (.xlsx)", command=export_to_excel, image=excel_photo,
                               compound=tk.LEFT)
    export_button.image = excel_photo  # Keep a reference to the image to prevent garbage collection
    export_button.pack(side=tk.TOP, padx=5)

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

    # Center the database window on the user's screen
    db_window.update_idletasks()
    screen_width = db_window.winfo_screenwidth()
    screen_height = db_window.winfo_screenheight()
    db_window_width = db_window.winfo_width()
    db_window_height = db_window.winfo_height()
    x = (screen_width // 2) - (db_window_width // 2)
    y = (screen_height // 2) - (db_window_height // 2)
    db_window.geometry(f"+{x}+{y}")

    db_window.transient(window)  # Make the db_window transient to the main window
    db_window.grab_set()  # Grab the focus to the db_window
    db_window.wait_window()  # Wait until the db_window is closed before returning to the main window