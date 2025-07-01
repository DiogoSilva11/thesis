# -----------------------------------------------------------------------------------------------------------------

import faiss

import numpy as np

from numpy import ndarray
from sentence_transformers import SentenceTransformer

# -----------------------------------------------------------------------------------------------------------------

def load_embedding_model() -> SentenceTransformer:
    '''
    Loads the model that will convert text into numerical embeddings
    '''
    embeddings = SentenceTransformer('all-MiniLM-L6-v2')
    print('[AGENT] Embedding model loaded')
    return embeddings

# -----------------------------------------------------------------------------------------------------------------

def get_sentence_embedding(model : SentenceTransformer, sentence: str) -> ndarray:
    '''
    Obtains an embedding that represents an entire sentence
    '''
    return model.encode([sentence])[0]

# -----------------------------------------------------------------------------------------------------------------

def generate_embeddings(model : SentenceTransformer, docs: list[str]) -> ndarray:
    '''
    Generates numerical embeddings from text documents
    '''
    return np.array([get_sentence_embedding(model, doc) for doc in docs])

# -----------------------------------------------------------------------------------------------------------------

def generate_faiss_indices(embeddings: ndarray) -> faiss.IndexFlatL2:
    '''
    Generates FAISS index from embeddings
    '''
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype(np.float32))
    return index

# -----------------------------------------------------------------------------------------------------------------

def query_faiss(model : SentenceTransformer, index: faiss.IndexFlatL2, docs: list[str], query: str, top_k: int = 3) -> list[str]:
    '''
    Retrieves the most similar documents to the query using FAISS
    '''
    query_embedding = get_sentence_embedding(model, query).reshape(1, -1)
    _, indices = index.search(query_embedding.astype(np.float32), top_k)
    results = [docs[i] for i in indices[0]]
    return results

# -----------------------------------------------------------------------------------------------------------------