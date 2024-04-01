import csv

# Define the ranges for each soil health indicator
soil_ph_ranges = ['<5.5', '5.5-6.5', '6.5-7.5', '7.5-8.5', '>8.5']
nitrogen_ranges = ['<100', '100-150', '150-200', '200-250', '>250']
phosphorus_ranges = ['<10', '10-20', '20-30', '30-40', '>40']
potassium_ranges = ['<50', '50-100', '100-150', '150-200', '>200']
ec_ranges = ['<0.5', '0.5-1.0', '1.0-1.5', '1.5-2.0', '>2.0']
temperature_ranges = ['<20', '20-25', '25-30', '30-35', '>35']
moisture_ranges = ['<30', '30-50', '50-70', '70-90', '>90']
humidity_ranges = ['<30', '30-50', '50-70', '70-90', '>90']

# Generate the fuzzy comparison matrix dataset
dataset = []
for ph in soil_ph_ranges:
    for n in nitrogen_ranges:
        for p in phosphorus_ranges:
            for k in potassium_ranges:
                for ec in ec_ranges:
                    for temp in temperature_ranges:
                        for moist in moisture_ranges:
                            for humid in humidity_ranges:
                                fuzzy_value = 0.5  # Default fuzzy value (Medium)
                                if (
                                    ph in ['<5.5', '>8.5'] or
                                    n == '<100' or
                                    p == '<10' or
                                    k == '<50' or
                                    ec == '<0.5' or
                                    temp == '<20' or
                                    moist == '<30' or
                                    humid == '<30'
                                ):
                                    fuzzy_value = 0.2  # Low
                                elif (
                                    ph in ['6.5-7.5'] and
                                    n in ['150-200'] and
                                    p in ['20-30'] and
                                    k in ['100-150'] and
                                    ec in ['1.0-1.5'] and
                                    temp in ['25-30'] and
                                    moist in ['50-70'] and
                                    humid in ['50-70']
                                ):
                                    fuzzy_value = 0.8  # High
                                row = [ph, n, p, k, ec, temp, moist, humid, fuzzy_value]
                                dataset.append(row)

# Save the dataset to a CSV file
with open('fuzzy_comparison_matrix.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Soil pH', 'Nitrogen (mg/kg)', 'Phosphorus (mg/kg)', 'Potassium (mg/kg)',
                     'Electrical Conductivity (dS/m)', 'Temperature (°C)', 'Moisture (%)', 'Humidity (%)',
                     'Fuzzy Value'])
    writer.writerows(dataset)

print("Fuzzy comparison matrix dataset generated successfully!")
print(f"Total rows: {len(dataset)}")