# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
import numpy as np
from fahp import fuzzy_geometric_mean, fuzzy_weights, defuzzify, fahp_weights, evaluate_soil_health

class CalculationsWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Soil Health Calculations")
        self.geometry("800x400")

        self.create_widgets()

    def create_widgets(self):
        self.table = ttk.Treeview(self, columns=("Criteria", "Soil Sample Value", "Fuzzy Geometric Mean",
                                                  "Fuzzy Weight", "Normalized Weight", "Soil Health Score",
                                                  "Total Soil Health Score"), show="headings")
        self.table.heading("Criteria", text="Criteria")
        self.table.heading("Soil Sample Value", text="Soil Sample Value")
        self.table.heading("Fuzzy Geometric Mean", text="Fuzzy Geometric Mean")
        self.table.heading("Fuzzy Weight", text="Fuzzy Weight")
        self.table.heading("Normalized Weight", text="Normalized Weight")
        self.table.heading("Soil Health Score", text="Soil Health Score")
        self.table.heading("Total Soil Health Score", text="Total Soil Health Score")
        self.table.pack(fill=tk.BOTH, expand=True)

        criteria = ["Soil pH", "Nitrogen (ppm)", "Phosphorus (ppm)", "Potassium (ppm)",
                    "EC (dS/m)", "Temperature (°C)", "Moisture (%)", "Humidity (%)"]
        ranges = [(0, 8.5), (10, 500), (10, 200), (10, 400), (0, 4.00), (1, 50), (1, 100), (1, 100)]
        self.entry_vars = []

        for criterion, range_ in zip(criteria, ranges):
            frame = ttk.Frame(self)
            label = ttk.Label(frame, text=criterion)
            label.pack(side=tk.LEFT, padx=5)
            entry_var = tk.DoubleVar()
            entry_var.set(range_[0])
            self.entry_vars.append(entry_var)
            entry = ttk.Entry(frame, textvariable=entry_var)
            entry.pack(side=tk.LEFT)
            frame.pack(anchor=tk.W, padx=10, pady=5)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        calculate_button = ttk.Button(button_frame, text="Calculate", command=self.calculate)
        calculate_button.pack(side=tk.LEFT, padx=5)

        close_button = ttk.Button(button_frame, text="Close", command=self.destroy)
        close_button.pack(side=tk.LEFT, padx=5)

    def calculate(self):
        soil_sample_values = []
        for entry_var in self.entry_vars:
            value = entry_var.get()
            soil_sample_values.append(value)

        soil_sample_values = np.array(soil_sample_values)
        geometric_mean = fuzzy_geometric_mean(soil_sample_values)
        fuzzy_weight = fuzzy_weights(geometric_mean)
        normalized_weights = fahp_weights()
        soil_health_scores = evaluate_soil_health(soil_sample_values)

        for i, item in enumerate(self.table.get_children()):
            self.table.set(item, "Soil Sample Value", str(soil_sample_values[i]))
            self.table.set(item, "Fuzzy Geometric Mean", str(geometric_mean))
            self.table.set(item, "Fuzzy Weight", str(fuzzy_weight))
            self.table.set(item, "Normalized Weight", str(normalized_weights[i]))
            self.table.set(item, "Soil Health Score", str(soil_health_scores[i]))

        total_soil_health_score = sum(soil_health_scores)
        self.table.set(self.table.get_children()[0], "Total Soil Health Score", str(total_soil_health_score))

if __name__ == "__main__":
    app = CalculationsWindow()
    app.mainloop()