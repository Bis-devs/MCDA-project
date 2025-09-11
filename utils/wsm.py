import numpy as np
from pymcdm.methods import WSM

def wsm_method(names, X, weights, criteria):
    """
    Run WSM and return ranking
    """
    method = WSM()
    scores = method(X, weights, criteria)
    ranking = sorted(zip(names, scores), key=lambda x: x[1], reverse=True)

    return {
        "scores": dict(ranking),
        "ranking": [name for name, _ in ranking]
    }
