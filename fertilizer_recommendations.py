import csv

def load_fertilizer_recommendations():
    fertilizer_recommendations = []
    try:
        with open('fertilizer_recommendations.csv', 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            for row in csv_reader:
                recommendation = {
                    'soil_ph_min': float(row[0]),
                    'soil_ph_max': float(row[1]),
                    'nitrogen_min': float(row[2]),
                    'nitrogen_max': float(row[3]) if row[3] != 'inf' else float('inf'),
                    'phosphorus_min': float(row[4]),
                    'phosphorus_max': float(row[5]) if row[5] != 'inf' else float('inf'),
                    'potassium_min': float(row[6]),
                    'potassium_max': float(row[7]) if row[7] != 'inf' else float('inf'),
                    'electrical_conductivity_min': float(row[8]),
                    'electrical_conductivity_max': float(row[9]) if row[9] != 'inf' else float('inf'),
                    'temperature_min': float(row[10]),
                    'temperature_max': float(row[11]) if row[11] != 'inf' else float('inf'),
                    'moisture_min': float(row[12]),
                    'moisture_max': float(row[13]) if row[13] != 'inf' else float('inf'),
                    'humidity_min': float(row[14]),
                    'humidity_max': float(row[15]) if row[15] != 'inf' else float('inf'),
                    'recommendation': row[16]
                }
                fertilizer_recommendations.append(recommendation)
    except FileNotFoundError:
        print("Error: fertilizer_recommendations.csv file not found.")
    except csv.Error as e:
        print(f"Error reading fertilizer_recommendations.csv: {e}")
    return fertilizer_recommendations

def get_fertilizer_recommendation(soil_data):
    fertilizer_recommendations = load_fertilizer_recommendations()
    for recommendation in fertilizer_recommendations:
        if (recommendation['soil_ph_min'] <= soil_data['soil_ph'] <= recommendation['soil_ph_max'] and
            recommendation['nitrogen_min'] <= soil_data['nitrogen'] <= recommendation['nitrogen_max'] and
            recommendation['phosphorus_min'] <= soil_data['phosphorus'] <= recommendation['phosphorus_max'] and
            recommendation['potassium_min'] <= soil_data['potassium'] <= recommendation['potassium_max'] and
            recommendation['electrical_conductivity_min'] <= soil_data['electrical_conductivity'] <= recommendation['electrical_conductivity_max'] and
            recommendation['temperature_min'] <= soil_data['temperature'] <= recommendation['temperature_max'] and
            recommendation['moisture_min'] <= soil_data['moisture'] <= recommendation['moisture_max'] and
            recommendation['humidity_min'] <= soil_data['humidity'] <= recommendation['humidity_max']):
            return recommendation['recommendation']
    return "No specific fertilizer recommendation available for the given soil data. Please consult with local agriculture experts for personalized recommendations."