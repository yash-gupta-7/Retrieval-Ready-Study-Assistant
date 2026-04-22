import faiss
import numpy as np

# Load embeddings
embeddings = np.load("embeddings.npy").astype('float32')

# Create index
index = faiss.IndexFlatL2(embeddings.shape[1])

# Add data
index.add(embeddings)

print("Total vectors:", index.ntotal)

# Save index to disk
faiss.write_index(index, "ncert.index")
print("Index saved to ncert.index")