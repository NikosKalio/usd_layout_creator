"""
Component Retriever Module

This module provides functionality to retrieve relevant industrial components from a vector index
based on natural language queries. It uses LlamaIndex for vector similarity search to find
the most relevant components matching the user's requirements.

Key features:
- Loads a pre-built vector index of component descriptions
- Performs semantic similarity search using VectorIndexRetriever
- Returns top matching components with their relevance scores
- Configurable number of results via similarity_top_k parameter

Usage:
    query = "I need a plastic workbench top with high chemical resistance"
    results = retrieve_components(query)
"""

# retrieve index components based on structured users input.
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.retrievers import VectorIndexRetriever
from dotenv import load_dotenv
import logging
import sys
import os

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Failed to import OPENAI_API_KEY")

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

# Rebuild storage context
storage_context = StorageContext.from_defaults(persist_dir="LLM_chain/index_components")

# Load index
index = load_index_from_storage(storage_context)

# Create a VectorIndexRetriever
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=2 # Adjust this value based on how many results you want
)

def retrieve_components(query):
    nodes = retriever.retrieve(query)
    return [{"content": node.node.text, "score": node.score} for node in nodes]

# Example usage
if __name__ == "__main__":
    # Example query
    #query = "I need a rolling cabinet around 500mm wide"
    query = "I need a plastic workbench top with high chemical and impact resistance"
    
    # Retrieve components based on the query
    retrieved_components = retrieve_components(query)
    
    # Print the retrieved components
    print("Retrieved Components:")
    for i, component in enumerate(retrieved_components, 1):
        print(f"\nComponent {i}:")
        print(f"Content: {component['content'][:100]}...")  # Print first 100 characters
        print(f"Score: {component['score']}")

    # You can further process or use these components as needed
