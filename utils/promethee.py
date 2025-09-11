import numpy as np

def promethee_method(weights, criteria, alternatives):
    """
    Implementation of the PROMETHEE method.

    Parameters:
        weights (list): Weights for criteria (must sum to 1).
        criteria (list): List of criteria with types ("max" or "min").
        alternatives (list): [["Company", v1, v2, ...], ...].

    Returns:
        dict: Net flows and ranking.
    """
    if len(weights) != len(criteria):
        raise ValueError("Number of weights must match number of criteria.")

    num_criteria = len(criteria)
    num_alternatives = len(alternatives)

    # Extract decision matrix
    decision_matrix = np.array([alt[1:] for alt in alternatives], dtype=float)

    # Normalize
    normalized_matrix = np.zeros_like(decision_matrix, dtype=float)
    for j in range(num_criteria):
        max_val = decision_matrix[:, j].max()
        min_val = decision_matrix[:, j].min()

        if max_val == min_val:
            normalized_matrix[:, j] = 0.0  # no variation
        else:
            if criteria[j] == "max":
                normalized_matrix[:, j] = (decision_matrix[:, j] - min_val) / (max_val - min_val)
            elif criteria[j] == "min":
                normalized_matrix[:, j] = (max_val - decision_matrix[:, j]) / (max_val - min_val)

    # Pairwise differences
    difference_matrix = np.zeros((num_alternatives, num_alternatives, num_criteria))
    for i in range(num_alternatives):
        for k in range(num_alternatives):
            difference_matrix[i, k] = normalized_matrix[i] - normalized_matrix[k]

    # Preference functions
    preference_matrix = np.maximum(difference_matrix, 0)

    # Aggregate preferences
    aggregated_preference = np.zeros((num_alternatives, num_alternatives))
    for i in range(num_alternatives):
        for k in range(num_alternatives):
            aggregated_preference[i, k] = np.sum(preference_matrix[i, k] * weights)

    # Flows
    leaving_flows = aggregated_preference.sum(axis=1) / (num_alternatives - 1)
    entering_flows = aggregated_preference.sum(axis=0) / (num_alternatives - 1)
    net_flows = leaving_flows - entering_flows

    # Ranking
    rankings = sorted(
        [(alternatives[i][0], flow) for i, flow in enumerate(net_flows)],
        key=lambda x: x[1],
        reverse=True
    )

    return {
        "net_flows": dict(rankings),
        "rankings": [alt[0] for alt in rankings]
    }
