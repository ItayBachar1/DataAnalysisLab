from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch


# Load the model and tokenizer
model_name = "meta-llama/Llama-3.2-1B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Explicitly set pad_token_id to eos_token_id
model.config.pad_token_id = model.config.eos_token_id

# Set up a text generation pipeline and pass pad_token_id explicitly
qa_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0 if torch.cuda.is_available() else -1,
    pad_token_id=model.config.eos_token_id
)

# Load the Airbnb dataset from Hugging Face
dataset = load_dataset("MongoDB/airbnb_embeddings")
data = dataset["train"].to_pandas()

print("Data loaded. Processing each description...")

def generate_qa(description):
    prompt = f"""
    Based on the following property description, create one question and answer related to what someone might be looking for when booking a property:

    Description: "{description}"

    Provide the output in this format:
    Q: [Question]
    A: [Answer]
    """

    # Generate response with max_new_tokens for limited output
    response = qa_pipeline(prompt, max_new_tokens=150, do_sample=True, temperature=0.5)
    return response[0]["generated_text"].strip()

# Apply the function to each row in the full dataset
all_data = data.copy()

for index, row in all_data.iterrows():
    description = row["description"]
    qa_result = generate_qa(description)

    # Split Q and A from the generated text
    question, answer = "", ""
    if "Q:" in qa_result and "A:" in qa_result:
        parts = qa_result.split("A:", 1)
        question = parts[0].replace("Q:", "").strip()
        answer = parts[1].strip()

    all_data.at[index, "synthetic_question"] = question
    all_data.at[index, "synthetic_answer"] = answer

    if index % 50 == 0:
        print(f"Processed {index} records.")

print("Processing complete.")

all_data[["_id", "description", "synthetic_question", "synthetic_answer"]].to_csv("synthetic_qa_pairs_llama_full.csv", index=False)
