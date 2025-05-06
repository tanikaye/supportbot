import numpy as np

def cosine_similarity(vec1, vec2):
    """
    Computes cosine similarity between two lists of floats.
    """
    a = np.array(vec1)
    b = np.array(vec2)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
