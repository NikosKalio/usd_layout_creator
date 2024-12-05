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

import json
# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Failed to import OPENAI_API_KEY")

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


# Rebuild storage context
storage_context = StorageContext.from_defaults(persist_dir="LLM_chain/LLM_chain/index_components")
# Load index
index = load_index_from_storage(storage_context)

# Create a VectorIndexRetriever
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=1 # Adjust this value based on how many results you want
)

def load_search_json(filename):
    with open(filename, 'r') as f:
        search_data = json.load(f)
    return search_data

def retrieve_modules(query):
    nodes = retriever.retrieve(query)
    results = []
    for node in nodes:
        content = node.node.text
        # Extract defaultPrim name using string parsing
        default_prim = None
        for line in content.split('\n'):
            if 'defaultPrim = ' in line:
                # Extract text between quotes
                default_prim = line.split('"')[1] if '"' in line else line.split('=')[1].strip()
                break
                
        results.append({
            "content": content,
            "score": node.score,
            "default_prim": default_prim
        })
    return results



# search_data = load_search_json('LLM_chain/LLM_chain/searches/search_20241202_121421.json')
# cabinets= [c for c in search_data['components'] if c['category'] == "Cabinet"]

"""
# Example usage
if __name__ == "__main__":
    # Example query
    #query = "I need a rolling cabinet around 500mm wide"
    print(json.dumps(cabinets[1], indent=2))
    query = str(cabinets[2])
    
    # Retrieve components based on the query
    retrieved_modules = retrieve_modules(query)
    
    # Print the retrieved components
    print("Retrieved Components:")
    for i, component in enumerate(retrieved_modules, 1):
        print(f"\nComponent {i}:")
        print(f"Default Prim: {component['default_prim']}")
        print(f"Content: {component['content']}...")
        print(f"Score: {component['score']}")

    # You can further process or use these components as needed
"""
