# utils.py
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pandas as pd
import streamlit as st

@st.cache_resource
def load_faiss_index():
    if not os.path.exists("faiss_index.index") or not os.path.exists("airbnb_embeddings.npy"):
        raise FileNotFoundError("FAISS index or embeddings file not found. Please run data_preparation.py first.")
    index = faiss.read_index("faiss_index.index")
    embeddings = np.load("airbnb_embeddings.npy")
    return index, embeddings

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_data
def load_qa_data():
    return pd.read_csv("synthetic_qa_pairs_cohere_sample.csv")

@st.cache_data
def load_airbnb_data():
    return pd.read_json("hf://datasets/MongoDB/airbnb_embeddings/airbnb_embeddings.json", lines=True)
