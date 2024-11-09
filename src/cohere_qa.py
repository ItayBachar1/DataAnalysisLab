import cohere
import pandas as pd
from datasets import load_dataset

# Initialize Cohere client
cohere_api_key = "ghyo2A7f9R6eC97lmGKiPDKl6HwELXcBLwTL8cy4"
co = cohere.Client(cohere_api_key)

# Load the Airbnb dataset and convert it to a pandas DataFrame
dataset = load_dataset("MongoDB/airbnb_embeddings")
data = dataset["train"].to_pandas()

# Take a random sample of 500 rows
sample_data = data.sample(n=500, random_state=42).reset_index(drop=True)

print("Data loaded. Processing a sample of 500 descriptions...")

def generate_qa(description):
    prompt = f"""
    Based on the following property description, create one question and answer related to what someone might be looking for when booking a property:

    Description: "{description}"

    Provide the output in this format:
    Q: [Question]
    A: [Answer]
    """

    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=150,
        temperature=0.5
    )

    return response.generations[0].text.strip()

# Apply the question-answer generation function to each row in the sample data
for index, row in sample_data.iterrows():
    description = row["description"]
    qa_result = generate_qa(description)
    print(qa_result)

    # Split Q and A from the generated text
    question, answer = "", ""
    if "Q:" in qa_result and "A:" in qa_result:
        parts = qa_result.split("A:", 1)
        question = parts[0].replace("Q:", "").strip()
        answer = parts[1].strip()
        print(f"Question: {question}, Answer: {answer}")

    sample_data.at[index, "synthetic_question"] = question
    sample_data.at[index, "synthetic_answer"] = answer

    # Print progress every 50 records
    if index % 50 == 0:
        print(f"Processed {index} records out of 500")

print("Processing complete.")

# Save the generated Q&A pairs for the sample to a CSV file
sample_data[["_id", "description", "synthetic_question", "synthetic_answer"]].to_csv("synthetic_qa_pairs_cohere_sample.csv", index=False)
