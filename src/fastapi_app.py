import logging
import faiss
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
from utils import load_faiss_index, load_embedding_model, load_airbnb_data
import numpy as np
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Set up logging to file
logging.basicConfig(filename="app.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize embeddings and metadata
faiss_index = None
embedding_model = None
airbnb_data = None


# User info model
class UserInfo(BaseModel):
    first_name: str
    last_name: str
    max_price: float = Field(..., example=200)  # Max price user is willing to pay
    num_guests: int = Field(..., example=2)  # Number of guests
    accessibility_amenities: List[str] = []  # List of must-have accessibility amenities


class UserQuery(BaseModel):
    query: str
    user_info: UserInfo
    conversation_history: list = Field(default=[])


# Load resources with FAISS and the embedding model
def initialize_resources():
    global faiss_index, embedding_model, airbnb_data

    # Load FAISS index, embeddings, and model
    faiss_index, embeddings = load_faiss_index()
    embedding_model = load_embedding_model()
    airbnb_data = load_airbnb_data()

    # Ensure embeddings are stored for filtering
    airbnb_data['embedding'] = list(embeddings)
    logging.info("Resources initialized successfully.")


# Initialize resources on startup
@app.on_event("startup")
async def startup_event():
    initialize_resources()


# Collect user information
@app.post("/collect_user_info")
async def collect_user_info(user: UserInfo):
    try:
        logging.info(f"Collected user info: {user.dict()}")
        return {"message": "User information collected successfully!", "user_data": user.dict()}
    except Exception as e:
        logging.error(f"Error collecting user info: {e}")
        return {"error": "Failed to collect user information"}


# Retrieve properties based on user query and preferences
def retrieve_properties(query: str, user_info: UserInfo, k=5):
    # Filter airbnb_data based on max_price, num_guests, and accessibility amenities
    filtered_data = airbnb_data[
        (airbnb_data['price'] <= user_info.max_price) &
        (airbnb_data['accommodates'] >= user_info.num_guests)
    ]

    # Further filter listings to include only those with the selected accessibility amenities
    for amenity in user_info.accessibility_amenities:
        filtered_data = filtered_data[filtered_data['amenities'].apply(lambda x: amenity in x)]

    if filtered_data.empty:
        return []  # Return empty list if no properties match the filters

    # Get embeddings only for filtered listings
    filtered_embeddings = np.vstack(filtered_data['embedding'].values).astype('float32')

    # Perform FAISS search on the filtered embeddings
    query_embedding = embedding_model.encode(query).reshape(1, -1).astype('float32')
    temp_index = faiss.IndexFlatL2(filtered_embeddings.shape[1])  # Temporary FAISS index for filtered data
    temp_index.add(filtered_embeddings)
    distances, indices = temp_index.search(query_embedding, k)

    # Retrieve top results based on indices
    results = filtered_data.iloc[indices[0]]
    return results[["_id", "listing_url", "name", "description"]].to_dict(orient="records")


# Handle user query
@app.post("/query")
async def handle_query(user_query: UserQuery):
    try:
        logging.info(f"Received query: {user_query.query} from {user_query.user_info.first_name}")

        relevant_properties = retrieve_properties(user_query.query, user_query.user_info, k=5)

        return {"response": relevant_properties}

    except Exception as e:
        logging.error(f"Error handling query: {e}")
        return {"error": str(e)}


# Run FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
