import csv

def load_fertilizer_recommendations():
    fertilizer_recommendations = []
    try:
        with open('fertilizer_recommendations.csv', 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            for row in csv_reader:
                min_score = float(row[0])
                max_score = float(row[1])
                recommendation = row[2]
                fertilizer_recommendations.append((min_score, max_score, recommendation))
    except FileNotFoundError:
        print("Error: fertilizer_recommendations.csv file not found.")
    except csv.Error as e:
        print(f"Error reading fertilizer_recommendations.csv: {e}")
    return fertilizer_recommendations

def get_fertilizer_recommendation(soil_health_score):
    fertilizer_recommendations = load_fertilizer_recommendations()
    for min_score, max_score, recommendation in fertilizer_recommendations:
        if min_score <= soil_health_score < max_score:
            return recommendation
    return "No specific fertilizer recommendation available for the given soil health score. Please consult with local agriculture experts for personalized recommendations."