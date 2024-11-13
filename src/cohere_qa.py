import cohere
import pandas as pd
import os

# Initialize Cohere client using an environment variable for the API key
cohere_api_key = os.getenv("COHERE_API_KEY")
if not cohere_api_key:
    raise ValueError("Cohere API key not found. Set it as an environment variable COHERE_API_KEY.")
co = cohere.Client(cohere_api_key)

# Load the cleaned airbnb dataset
data = pd.read_csv("../data/cleaned_airbnb_data.csv")
#dataset = load_dataset("MongoDB/airbnb_embeddings")
#data = dataset["train"].to_pandas()

# Take a random sample of 500 rows
sample_data = data.sample(n=500, random_state=3).reset_index(drop=True)

print("Data loaded. Processing a sample of 500 descriptions...")

# Define topics for synthetic question generation
topics = [
    "accessibility for people with disabilities",
    "specific infrastructure",
    "basic amenities",
]

# Function to generate synthetic Q&A pairs for each topic
def generate_synthetic_qa(description, amenities, access, transit):
    qa_pairs = []
    for topic in topics:
        prompt = f"""
        Based on the following property details, generate a relevant question and answer that a user might ask when booking, specifically about {topic}.

        Description: "{description}"
        Amenities: "{amenities}"
        Access: "{access}"
        Transit Options: "{transit}"

        Focus on creating questions that a potential guest would likely ask regarding {topic}.

        Format your response like this:
        Q: [Question]
        A: [Answer]
        """

        response = co.generate(
            model='command-xlarge-nightly',
            prompt=prompt,
            max_tokens=150,
            temperature=0.5
        )

        qa_result = response.generations[0].text.strip()

        # Extract Q and A from the response
        if "Q:" in qa_result and "A:" in qa_result:
            parts = qa_result.split("A:", 1)
            question = parts[0].replace("Q:", "").strip()
            answer = parts[1].strip()
            qa_pairs.append((question, answer))
        else:
            qa_pairs.append((None, None))

    return qa_pairs

# Apply the question-answer generation function to each row in the sample data
all_qa_rows = []
batch_size = 100
output_file = "synthetic_qa_pairs1.csv"

# Initialize CSV file for the first batch if it doesn’t already exist
pd.DataFrame(columns=["_id", "synthetic_question", "synthetic_answer"]).to_csv(output_file, index=False)

for index, row in sample_data.iterrows():
    description = row["description"]
    amenities = row.get("amenities", "Not specified")
    access = row.get("access", "Not specified")
    transit = row.get("transit", "Not specified")

    qa_pairs = generate_synthetic_qa(description, amenities, access, transit)

    for question, answer in qa_pairs:
        all_qa_rows.append({
            "_id": row["_id"],
            "synthetic_question": question,
            "synthetic_answer": answer
        })

    # Save every 100 records to prevent data loss in case of interruption
    if (index + 1) % batch_size == 0:
        qa_df = pd.DataFrame(all_qa_rows)
        qa_df.to_csv(output_file, mode='a', index=False, header=False)  # Append to the CSV
        print(f"Saved batch up to record {index + 1}")
        all_qa_rows = []  # Clear the batch list after saving

# Save any remaining records after the loop ends
if all_qa_rows:
    qa_df = pd.DataFrame(all_qa_rows)
    qa_df.to_csv(output_file, mode='a', index=False, header=False)
    print("Saved final batch.")

print("Processing complete.")
