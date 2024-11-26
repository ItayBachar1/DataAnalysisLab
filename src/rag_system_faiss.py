# -*- coding: utf-8 -*-
"""Rag_system_faiss.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1nFllolh-hmuN92gfecD5s295aVS13336
"""

import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from transformers import pipeline
from sklearn.metrics import precision_score, recall_score


# Load synthetic QA pairs dataset for question-answer reference
qa_df = pd.read_csv("./data/synthetic_qa_pairs.csv")
print("Columns in synthetic QA file:", qa_df.columns)

# Load Airbnb dataset with property descriptions and embeddings
# df = pd.read_csv("../data/cleaned_airbnb_data.csv")
df = pd.read_csv("./data/cleaned_airbnb_data.csv")
print("Columns in the dataset:", df.columns)
df['description'] = df['description'].fillna('').astype(str)

# Prepare and embed property descriptions using a pre-trained language model
descriptions = df['description'].tolist()
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = embedding_model.encode(descriptions, convert_to_tensor=True).cpu().detach().numpy()


# Initialize and populate a FAISS index with property description embeddings
d = embeddings.shape[1]
index = faiss.IndexFlatL2(d)
index.add(embeddings.astype('float32'))

# Retrieve function: retrieves top-k similar property descriptions based on the query
def retrieve_properties(query, k=10):
    """
    Retrieves the top-k most similar property descriptions based on a user query using FAISS.

    Args:
        query (str): A query string from the user.
        k (int): The number of top results to retrieve.

    Returns:
        list: A list of the top-k retrieved property descriptions.
    """
    query_embedding = embedding_model.encode(query, convert_to_tensor=True).cpu().detach().numpy()
    query_embedding = np.expand_dims(query_embedding, axis=0).astype('float32')
    distances, indices = index.search(query_embedding, k)
    return [descriptions[idx] for idx in indices[0]]

# Load text generation model to generate responses based on the retrieved data
generator = pipeline("text-generation", model="distilgpt2")

# Generate response function: uses retrieved descriptions and synthetic QA pairs to create an answer
def generate_response_with_qa(query):
    """
    Generates a response based on retrieved property descriptions and relevant QA pairs.

    Args:
        query (str): A user query to generate a response for.

    Returns:
        str: A generated response combining property descriptions and QA pairs.
    """
    relevant_descriptions = retrieve_properties(query, k=5)
    if not relevant_descriptions:
        return "No relevant descriptions found."

    # Retrieve relevant synthetic QA pairs related to the query
    relevant_qa_pairs = qa_df[qa_df['synthetic_question'].str.contains(query, case=False, na=False)]

    # Construct a prompt for generation by combining descriptions and QA pairs
    prompt = "Based on these property descriptions and example Q&A, describe a suitable property:\n"
    prompt += "\n".join(relevant_descriptions[:3])
    prompt += "\nExample Q&A:\n"
    prompt += "\n".join([f"Q: {row['synthetic_question']}\nA: {row['synthetic_answer']}" for _, row in relevant_qa_pairs.iterrows()][:3])

    # Generate a response using the text generation model
    response = generator(prompt, max_new_tokens=50, num_return_sequences=1, truncation=True)
    return response[0]['generated_text']

# Rerank results based on user preferences
def rerank_results(results, preferences):
    """
    Reranks retrieved results based on the user's preferences.

    Args:
        results (list): A list of retrieved property descriptions.
        preferences (list): A list of words the user prefers, e.g., "wheelchair", "elevator".

    Returns:
        list: The ranked results based on the user's preferences.
    """
    ranked_results = sorted(results, key=lambda x: sum(1 for word in preferences if word in x.lower()), reverse=True)
    return ranked_results

# Evaluation function: calculates precision and recall between true answers and generated answers
def evaluate_rag_system(true_answers, generated_answers):
    """
    Evaluates the RAG system's performance using precision and recall metrics.

    Args:
        true_answers (list of int): A list of binary ground truth labels (1 for relevant, 0 for non-relevant).
        generated_answers (list of int): A list of binary predicted labels by the RAG system (1 for relevant, 0 for non-relevant).

    Prints:
        Precision and Recall scores.
    """
    precision = precision_score(true_answers, generated_answers, average='binary')
    recall = recall_score(true_answers, generated_answers, average='binary')
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")

# Example usage
query = "Looking for a wheelchair accessible property with an elevator."
retrieved_properties = retrieve_properties(query, k=10)
response = generate_response_with_qa(query)
print("Generated Response with QA:", response)

preferences = ["wheelchair", "elevator", "accessible"]
ranked_results = rerank_results(retrieved_properties, preferences)
print("Ranked Results:", ranked_results[:5])

# Example evaluation of the RAG system with dummy data
true_answers = [1, 0, 1, 1, 0]
generated_answers = [1, 0, 1, 0, 0]
evaluate_rag_system(true_answers, generated_answers)

"""# Evaluation"""

import pandas as pd
from transformers import pipeline, AutoTokenizer
from sentence_transformers import SentenceTransformer
import numpy as np
from evaluate import load

# Load the synthetic QA pairs dataset
qa_df = pd.read_csv("./data/synthetic_qa_pairs.csv")
questions = qa_df['synthetic_question'].tolist()
reference_answers = qa_df['synthetic_answer'].tolist()

# Load models for RAG and basic LLM
rag_model = pipeline("text-generation", model="distilgpt2")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
tokenizer = AutoTokenizer.from_pretrained("distilgpt2")  # Load tokenizer for distilgpt2

# Function to truncate input text to fit model's token limit
def truncate_text(text, max_length=1024):
    tokens = tokenizer.encode(text, truncation=True, max_length=max_length)
    return tokenizer.decode(tokens)

# Basic LLM answer generation function
def generate_llm_answer(question):
    response = rag_model(question, max_new_tokens=50, num_return_sequences=1)
    return response[0]['generated_text'].strip()

# Retrieval function for RAG system (assuming retrieve_properties function is defined elsewhere)
def generate_rag_answer(question):
    relevant_descriptions = retrieve_properties(question, k=3)
    prompt = " ".join(relevant_descriptions) + f"\nQuestion: {question}\nAnswer:"
    truncated_prompt = truncate_text(prompt, max_length=1024)
    response = rag_model(truncated_prompt, max_new_tokens=50, num_return_sequences=1)
    return response[0]['generated_text'].strip()

# Evaluation function for comparing LLM and RAG models
def evaluate_models(questions, reference_answers):
    bleu_metric = load("bleu")
    rouge_metric = load("rouge")
    bertscore_metric = load("bertscore")

    # Evaluate basic LLM model
    llm_generated_answers = [generate_llm_answer(q) for q in questions]
    llm_bleu = bleu_metric.compute(predictions=llm_generated_answers, references=[[ref] for ref in reference_answers])
    llm_rouge = rouge_metric.compute(predictions=llm_generated_answers, references=reference_answers)
    llm_bertscore = bertscore_metric.compute(predictions=llm_generated_answers, references=reference_answers, lang="en")

    # Evaluate RAG model with retrieved properties
    rag_generated_answers = [generate_rag_answer(q) for q in questions]
    rag_bleu = bleu_metric.compute(predictions=rag_generated_answers, references=[[ref] for ref in reference_answers])
    rag_rouge = rouge_metric.compute(predictions=rag_generated_answers, references=reference_answers)
    rag_bertscore = bertscore_metric.compute(predictions=rag_generated_answers, references=reference_answers, lang="en")


    print("LLM Model Performance:")
    print(f"BLEU: {llm_bleu['bleu']:.2f}")
    print(f"ROUGE-1: {llm_rouge['rouge1']:.2f}")
    print(f"BERTScore F1: {np.mean(llm_bertscore['f1']):.2f}\n")

    print("RAG Model Performance:")
    print(f"BLEU: {rag_bleu['bleu']:.2f}")
    print(f"ROUGE-1: {rag_rouge['rouge1']:.2f}")
    print(f"BERTScore F1: {np.mean(rag_bertscore['f1']):.2f}")

# evaluation
evaluate_models(questions[:10], reference_answers[:10])  # Running on a subset for testing

import pandas as pd
from sklearn.metrics import precision_score, recall_score
import numpy as np

qa_df = pd.read_csv("./data/synthetic_qa_pairs.csv")
questions = qa_df['synthetic_question'].tolist()
reference_answers = qa_df['synthetic_answer'].tolist()

# Define your top-K parameter for Recall at K
TOP_K = 5

# Function to calculate Recall at K and MRR
def evaluate_retrieval_metrics(questions, reference_answers, top_k=TOP_K):
    # Initialize variables to store recall at K and MRR
    recall_at_k_scores = []
    reciprocal_ranks = []

    # Iterate over each question and its reference answer
    for question, reference in zip(questions, reference_answers):
        # Retrieve top-K descriptions
        retrieved_descriptions = retrieve_properties(question, k=top_k)

        # Check if any of the retrieved descriptions match the reference answer
        relevant_found = False
        for rank, description in enumerate(retrieved_descriptions, start=1):
            if reference in description:
                reciprocal_ranks.append(1 / rank)
                relevant_found = True
                break

        # If no relevant result was found, add a reciprocal rank of 0
        if not relevant_found:
            reciprocal_ranks.append(0)

        # Calculate recall at K
        recall_at_k = int(any(reference in desc for desc in retrieved_descriptions))
        recall_at_k_scores.append(recall_at_k)

    # Calculate mean Recall at K and MRR
    mean_recall_at_k = np.mean(recall_at_k_scores)
    mean_reciprocal_rank = np.mean(reciprocal_ranks)

    # Display the results
    print(f"Recall at {top_k}: {mean_recall_at_k:.2f}")
    print(f"Mean Reciprocal Rank (MRR): {mean_reciprocal_rank:.2f}")

# Evaluating the retrieval metrics
evaluate_retrieval_metrics(questions[:10], reference_answers[:10])
