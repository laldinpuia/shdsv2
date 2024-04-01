import csv

def get_fertilizer_recommendation(ph, nitrogen, phosphorus, potassium, ec, temperature, moisture, humidity):
    with open('fertilizer_recommendations.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            if (
                ph in row[0] and
                nitrogen in row[1] and
                phosphorus in row[2] and
                potassium in row[3] and
                ec in row[4] and
                temperature in row[5] and
                moisture in row[6] and
                humidity in row[7]
            ):
                return row[8]
    return "No specific fertilizer recommendation found for the given soil health indicators."