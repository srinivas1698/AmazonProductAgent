from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
import os


# Load the environment variables from .env file
load_dotenv()

# Access the API keys
pinecone_api_key = os.getenv('PINECONE_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')



openai_client = OpenAI(api_key=openai_api_key)




def pad_vectors(vector, target_length=3072):
    # Calculate the number of zeros needed to reach the target length
    padding_size = target_length - len(vector)
    # Check if padding is necessary
    if padding_size > 0:
        # Pad the vector with zeros at the end
        padded_vector = np.pad(vector, (0, padding_size), mode='constant')
    else:
        padded_vector = vector[:target_length]
    # Append the padded vector to the list
    return padded_vector

def get_embedding(text_to_embed):
    # Embed a line of text
    response = openai_client.embeddings.create(
    	model= "text-embedding-3-large",
    	input=[text_to_embed]
    )
    
    # Extract the AI output embedding as a list of floats
    vector = response.data[0].embedding
    vector = pad_vectors(vector)
    return vector


