# -*- coding: utf-8 -*-
import csv

def generate_fertilizer_recommendations_csv():
    fertilizer_recommendations = [
        ['5.0', '5.5', '0', '75', '0', '10', '0', '50', '0', '0.5', '20', '25', '20', '40', '30', '50', 'Apply lime (e.g., calcium carbonate) at a rate of 1-2 t/ha to increase soil pH. Use nitrogen-rich fertilizers (e.g., urea, ammonium sulfate) at a rate of 40-60 kg/ha. Include phosphorus fertilizers (e.g., single superphosphate, diammonium phosphate) at a rate of 20-30 kg/ha.'],
        ['5.5', '6.5', '75', '150', '10', '20', '50', '100', '0.5', '1.0', '25', '30', '40', '60', '50', '70', 'Apply nitrogen-rich fertilizers (e.g., urea, ammonium sulfate) at a rate of 60-80 kg/ha. Include phosphorus fertilizers (e.g., single superphosphate, diammonium phosphate) at a rate of 30-40 kg/ha and potassium fertilizers (e.g., muriate of potash, potassium sulfate) at a rate of 40-60 kg/ha.'],
        ['6.5', '7.5', '150', '225', '20', '30', '100', '150', '1.0', '1.5', '30', '35', '60', '80', '70', '90', 'Apply balanced NPK fertilizers (e.g., 15-15-15, 19-19-19) at a rate of 125-175 kg/ha. Consider fertigation or foliar application for precise nutrient management. Include micronutrients (e.g., zinc, boron) based on soil test results.'],
        ['7.5', '8.5', '225', '300', '30', '40', '150', '200', '1.5', '2.0', '35', '40', '80', '90', '90', '100', 'Reduce nitrogen application to 40-60 kg/ha and focus on balanced fertilization. Apply potassium fertilizers (e.g., muriate of potash, potassium sulfate) at a rate of 60-80 kg/ha. Consider organic amendments (e.g., compost, vermicompost) to improve soil structure and fertility.'],
        ['8.5', '9.5', '300', '400', '40', '50', '200', '250', '2.0', '2.5', '40', '45', '90', '100', '100', '100', 'Avoid applying nitrogenous fertilizers due to high pH levels. Focus on soil amendments such as gypsum (1-2 t/ha), sulfur (100-200 kg/ha), or organic matter to improve soil conditions. Apply potassium fertilizers (e.g., muriate of potash, potassium sulfate) at a rate of 80-100 kg/ha.'],
        ['9.5', '14.0', '400', 'inf', '50', 'inf', '250', 'inf', '2.5', 'inf', '45', 'inf', '100', 'inf', '100', 'inf', 'Soil highly alkaline and saline. Avoid applying fertilizers. Focus on soil reclamation using gypsum (2-4 t/ha), sulfur (200-400 kg/ha), and organic amendments. Consult with local agriculture experts for specific recommendations based on crop and soil type.']
    ]

    header = ['Soil pH Range (Min)', 'Soil pH Range (Max)', 'Nitrogen Range (Min) (mg/kg)', 'Nitrogen Range (Max) (mg/kg)',
              'Phosphorus Range (Min) (mg/kg)', 'Phosphorus Range (Max) (mg/kg)', 'Potassium Range (Min) (mg/kg)',
              'Potassium Range (Max) (mg/kg)', 'Electrical Conductivity Range (Min) (dS/m)',
              'Electrical Conductivity Range (Max) (dS/m)', 'Temperature Range (Min) (°C)', 'Temperature Range (Max) (°C)',
              'Moisture Range (Min) (%)', 'Moisture Range (Max) (%)', 'Humidity Range (Min) (%)',
              'Humidity Range (Max) (%)', 'Fertilizer Recommendation']

    with open('fertilizer_recommendations.csv', 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(header)
        csv_writer.writerows(fertilizer_recommendations)

    print("fertilizer_recommendations.csv file generated successfully.")

# Run the function to generate the CSV file
generate_fertilizer_recommendations_csv()