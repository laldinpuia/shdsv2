import numpy as np

def triangular_fuzzy_number(a, b, c):
    return (a, b, c)

def defuzzify(tfn):
    a, b, c = tfn
    return (a + b + c) / 3

def predefined_fuzzy_comparison_matrix():
    # Define the fuzzy pairwise comparison matrix based on expert knowledge
    matrix = np.array([
        [[1, 1, 1], [1, 2, 3], [1, 2, 3], [1, 2, 3], [2, 3, 4], [1, 2, 3], [2, 3, 4], [1, 2, 3]],
        [[1/3, 1/2, 1], [1, 1, 1], [1, 2, 3], [1, 2, 3], [2, 3, 4], [1, 2, 3], [2, 3, 4], [1, 2, 3]],
        [[1/3, 1/2, 1], [1/3, 1/2, 1], [1, 1, 1], [1, 2, 3], [2, 3, 4], [1, 2, 3], [2, 3, 4], [1, 2, 3]],
        [[1/3, 1/2, 1], [1/3, 1/2, 1], [1/3, 1/2, 1], [1, 1, 1], [1, 2, 3], [1, 2, 3], [2, 3, 4], [1, 2, 3]],
        [[1/4, 1/3, 1/2], [1/4, 1/3, 1/2], [1/4, 1/3, 1/2], [1/3, 1/2, 1], [1, 1, 1], [1, 2, 3], [1, 2, 3], [1, 2, 3]],
        [[1/3, 1/2, 1], [1/3, 1/2, 1], [1/3, 1/2, 1], [1/3, 1/2, 1], [1/3, 1/2, 1], [1, 1, 1], [1, 2, 3], [1, 2, 3]],
        [[1/4, 1/3, 1/2], [1/4, 1/3, 1/2], [1/4, 1/3, 1/2], [1/4, 1/3, 1/2], [1/3, 1/2, 1], [1/3, 1/2, 1], [1, 1, 1], [1, 2, 3]],
        [[1/3, 1/2, 1], [1/3, 1/2, 1], [1/3, 1/2, 1], [1/3, 1/2, 1], [1/3, 1/2, 1], [1/3, 1/2, 1], [1/3, 1/2, 1], [1, 1, 1]]
    ])
    return matrix

def fuzzy_geometric_mean(matrix):
    n = matrix.shape[0]
    geometric_means = []
    for i in range(n):
        row = matrix[i]
        geometric_mean = np.ones(3)
        for j in range(n):
            geometric_mean *= row[j]
        geometric_mean **= 1/n
        geometric_means.append(geometric_mean)
    return np.array(geometric_means)

def fuzzy_weights(geometric_means):
    n = len(geometric_means)
    fuzzy_weights = []
    for i in range(n):
        weight = geometric_means[i] / np.sum(geometric_means, axis=0)
        fuzzy_weights.append(weight)
    return np.array(fuzzy_weights)

def consistency_ratio(matrix):
    n = matrix.shape[0]
    defuzzified_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            defuzzified_matrix[i, j] = defuzzify(matrix[i, j])
    eigenvalues, _ = np.linalg.eig(defuzzified_matrix)
    max_eigenvalue = np.max(eigenvalues)
    consistency_index = (max_eigenvalue - n) / (n - 1)
    random_index = {1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
    consistency_ratio = consistency_index / random_index[n]
    return consistency_ratio

def fahp_weights():
    matrix = predefined_fuzzy_comparison_matrix()
    geometric_means = fuzzy_geometric_mean(matrix)
    weights = fuzzy_weights(geometric_means)
    defuzzified_weights = [defuzzify(weight) for weight in weights]
    normalized_weights = defuzzified_weights / np.sum(defuzzified_weights)
    return normalized_weights

def evaluate_soil_health(normalized_values):
    weights = fahp_weights()
    soil_health_score = sum(weight * value for weight, value in zip(weights, normalized_values))
    return soil_health_score