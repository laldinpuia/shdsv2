import csv

def get_crop_recommendation(soil_health_score):
    with open('crop_recommendations.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            score_range = row[0].split('-')
            if float(score_range[0]) <= soil_health_score <= float(score_range[1]):
                return row[1]
    return "No specific crop recommendation found for the given soil health score."