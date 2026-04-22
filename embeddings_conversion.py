from sentence_transformers import SentenceTransformer
import numpy as np

# STEP 1: Load model
model = SentenceTransformer('all-MiniLM-L6-v2')


# STEP 2: Read chunks file (one chunk per line)
with open("preprocess.txt", "r", encoding="utf-8") as file:
    sentences = [line.strip() for line in file if line.strip()]

# STEP 4: Generate embeddings
embeddings = model.encode(sentences, show_progress_bar=True)


# STEP 5: Save embeddings
np.save("embeddings.npy", embeddings)


# STEP 6: Save chunks as text (used during retrieval to fetch actual text)
with open("sentences.txt", "w", encoding="utf-8") as f:
    for s in sentences:
        f.write(s + "\n")