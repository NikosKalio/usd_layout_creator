"""
This script creates and stores vector embeddings for USDA component documents.
It reads documents from a specified directory, converts them into embeddings using
OpenAI's API, and saves the indexed data for future retrieval.

The script:
1. Loads environment variables (OpenAI API key)
2. Sets up logging
3. Processes documents from the assets directory
4. Creates vector embeddings using LlamaIndex
5. Persists the index to disk for later use
"""

# create embedings of usda compnonents.
import os
from pathlib import Path
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Document
from dotenv import load_dotenv
import logging
import sys
from llama_index.core import StorageContext, load_index_from_storage


# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Failed to import OPENAI_API_KEY")

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the path to the components folder


# Load documents and build index
def index_directory(assets_path, index_store_path):
    documents = SimpleDirectoryReader(
            assets_path
            ).load_data()
    
    index = VectorStoreIndex.from_documents(documents, show_progress=True)
    index.storage_context.persist(persist_dir=index_store_path)
    return index

assets_path = Path("../assets/components")
index_store_path = Path("LLM_chain/index_components")
index = index_directory(assets_path, index_store_path)