class SoilIndicator:
    def __init__(self, name, min_value, max_value, optimal_range, unit):
        self.name = name
        self.min_value = min_value
        self.max_value = max_value
        self.optimal_range = optimal_range
        self.unit = unit

    def __str__(self):
        return f"{self.name} ({self.min_value}-{self.max_value} {self.unit})"

# Define soil health indicators
soil_ph = SoilIndicator("Soil pH", 0, 8.5, (6.0, 7.5), "")
nitrogen = SoilIndicator("Nitrogen (N)", 10, 500, (50, 250), "mg/kg")
phosphorus = SoilIndicator("Phosphorus (P)", 10, 200, (20, 100), "mg/kg")
potassium = SoilIndicator("Potassium (K)", 10, 400, (50, 200), "mg/kg")
electrical_conductivity = SoilIndicator("Electrical Conductivity (EC)", 0, 4, (0, 2), "dS/m")
temperature = SoilIndicator("Temperature", 0, 50, (10, 30), "°C")
moisture = SoilIndicator("Moisture", 0, 100, (20, 80), "%")
humidity = SoilIndicator("Humidity", 0, 100, (30, 70), "%")

# Create a list of soil health indicators
soil_indicators = [
    soil_ph,
    nitrogen,
    phosphorus,
    potassium,
    electrical_conductivity,
    temperature,
    moisture,
    humidity
]