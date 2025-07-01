# -----------------------------------------------------------------------------------------------------------------

import numpy as np

from sentence_transformers import SentenceTransformer, util

# -----------------------------------------------------------------------------------------------------------------

def answer_discrepancy(model : SentenceTransformer, options : list[str], answer : int, prediction : int) -> bool:
    '''
    Determines if there is a considerable discrepancy between an answer and a prediction
    '''
    embeddings = [model.encode(option, convert_to_tensor=True) for option in options]
    distances = [1 - util.cos_sim(embeddings[answer], embedding).item() for embedding in embeddings]
    threshold_index = (len(options) + 1) // 2
    most_distant_indices = set(np.argsort(distances)[-threshold_index:])
    return prediction in most_distant_indices

# -----------------------------------------------------------------------------------------------------------------