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

def generate_crop_recommendations(soil_health_score):
    if soil_health_score < 0.4:
        return "Green Manure Crops, Legumes, Cowpea, Sesbania"
    elif soil_health_score < 0.6:
        return "Millets(Pearl Millet, Sorghum), Maize, Soybean, Groundnut"
    elif soil_health_score < 0.8:
        return "Rice, Wheat, Cotton, Sugarcane, Mustard, Sunflower"
    else:
        return "Vegetables, Fruits, Spices, Pulses, Oilseeds"