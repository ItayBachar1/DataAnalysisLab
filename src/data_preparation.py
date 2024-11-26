# data_preparation.py
import os
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss

# Set batch size for incremental processing
BATCH_SIZE = 500

# Check if files already exist to avoid overwriting
if not os.path.exists("faiss_index.index") or not os.path.exists("airbnb_embeddings.npy"):
    # Load Airbnb dataset and descriptions
    df = pd.read_json("hf://datasets/MongoDB/airbnb_embeddings/airbnb_embeddings.json", lines=True)
    descriptions = df['description'].tolist()

    # Initialize model and FAISS index
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    d = embedding_model.get_sentence_embedding_dimension()
    index = faiss.IndexFlatL2(d)

    # Process embeddings in batches
    all_embeddings = []
    for start in range(0, len(descriptions), BATCH_SIZE):
        batch_descriptions = descriptions[start:start + BATCH_SIZE]
        batch_embeddings = embedding_model.encode(batch_descriptions, convert_to_tensor=True).cpu().detach().numpy()

        # Add batch to index
        index.add(batch_embeddings.astype('float32'))

        # Collect embeddings for saving
        all_embeddings.append(batch_embeddings)
        print(f"Processed batch {start // BATCH_SIZE + 1} of {len(descriptions) // BATCH_SIZE + 1}")

    # Concatenate all embeddings and save
    all_embeddings = np.vstack(all_embeddings)
    np.save("airbnb_embeddings.npy", all_embeddings)

    # Save FAISS index to a file
    faiss.write_index(index, "faiss_index.index")
    print("Completed and saved embeddings and FAISS index.")
else:
    print("FAISS index and embeddings file already exist.")
