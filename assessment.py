import csv
from indicators import soil_indicators
from fahp import evaluate_soil_health

def assess_soil_health(indicator_values):
    # Validate the indicator values
    for indicator, value in zip(soil_indicators, indicator_values):
        if not indicator.min_value <= value <= indicator.max_value:
            raise ValueError(f"Invalid value for {indicator.name}: {value}")

    # Normalize the indicator values based on their ranges
    normalized_values = []
    for indicator, value in zip(soil_indicators, indicator_values):
        normalized_value = (value - indicator.min_value) / (indicator.max_value - indicator.min_value)
        normalized_values.append(normalized_value)

    # Calculate the soil health score using FAHP
    soil_health_score = evaluate_soil_health(normalized_values)

    return soil_health_score

def generate_rating(soil_health_score):
    if soil_health_score < 0.2:
        return "Very Poor"
    elif soil_health_score < 0.4:
        return "Poor"
    elif soil_health_score < 0.6:
        return "Below Average"
    elif soil_health_score < 0.7:
        return "Average"
    elif soil_health_score < 0.8:
        return "Above Average"
    elif soil_health_score < 0.9:
        return "Good"
    else:
        return "Excellent"

def load_crop_recommendations():
    crop_recommendations = []
    try:
        with open('crop_recommendations.csv', 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            for row in csv_reader:
                min_score = float(row[0])
                max_score = float(row[1])
                recommendation = row[2]
                crop_recommendations.append((min_score, max_score, recommendation))
    except FileNotFoundError:
        print("Error: crop_recommendations.csv file not found.")
    except csv.Error as e:
        print(f"Error reading crop_recommendations.csv: {e}")
    return crop_recommendations

def generate_crop_recommendations(soil_health_score):
    crop_recommendations = load_crop_recommendations()
    for min_score, max_score, recommendation in crop_recommendations:
        if min_score <= soil_health_score < max_score:
            return recommendation
    return "No specific crop recommendations available for the given soil health score."