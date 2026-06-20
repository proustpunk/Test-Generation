from sentence_transformers import SentenceTransformer
import numpy as np

EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
embedder = SentenceTransformer(EMBED_MODEL_NAME)

def embed_texts(texts, batch_size=32):

    embs = embedder.encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        show_progress_bar=False
    ).astype(np.float32)


    norms = np.linalg.norm(embs,axis=1,keepdims=True)
    norms[norms==0] = 1.0
    embs = embs/norms
    return embs

def embed_text(text):
    return embed_texts([text])[0]


