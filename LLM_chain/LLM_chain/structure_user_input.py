"""
This script processes natural language descriptions of workbench assemblies and converts them into structured data.

Key functionality:
1. Reads user input from a text file describing a workbench setup
2. Uses LLM to parse the description into structured components:
   - Cabinets (type, requirements)
   - Workbench top (type, requirements)
   - Rear panels (if needed, type, color, requirements)
   - General requirements
3. Saves the structured output as a timestamped JSON file

The script uses OpenAI's API and provides default values when specific details are not mentioned in the input.
"""

# takes user input in natural language and returns a structure that describes the main components of the workbench

# POC scope:
# 1. different types of cabinets with diffferent sizes
#2. different types of workbenches according to functions
#3. diffeerent sizes and collors of different panels.

import os
from dotenv import load_dotenv, find_dotenv
import json
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from openai import OpenAI
from datetime import datetime

# Load .env
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

def structure_user_input(user_input):
    # Define a simple output structure
    class Category(str, Enum):
        cabinet = "Cabinet"
        workbench_top = "Workbench Top"
        rear_panels = "Rear Panels"

    class Size(str, Enum):
        small = "Small"
        medium = "Medium"
        large = "Large"

    class WorkbenchComponent(BaseModel):
        category: Category
        requirements: List[str]
        size: Optional[Size]


    class WorkbenchCombination(BaseModel):
        components: List[WorkbenchComponent]

    # Define prompt template
    prompt_template_str = """
    You are tasked with interpreting expert user inputs to identify specific components for a modular workspace. Your goal is to extract the following information for each component:

    1. **Category**: Determine the type of component mentioned (e.g., Cabinet, Workbench Top, Rear Panel).
    2. **Size**: Identify the size specification if provided (e.g., Small, Medium, Large).
    3. **Requirements**: List any additional specifications or requirements mentioned. These might include colors, materials, or functions that users require.

    The output should include multiple searches:
    - At least two cabinet searches (with sizes and requirements).
    - One workbench top search.
    - One rear panel search.

    On average, a combination has 4-6 cabinets, 1 workbench top, and 2 rows of rear panels. They can be arbitrarily large, with N cabinets.
    Infer reasonable values for any missing information. Use standard types and colors if not specified.

    Return the data as a list of components.
    Infer reasonable values for any missing information. Use standard types and colors if not specified.
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": prompt_template_str},
            {"role": "user", "content": user_input}
        ],
        response_format=WorkbenchCombination,
    )

    #I need three cabinets, one small with shelves, two medium with drawers, a large wooden workbench
    # I want two drawer cabinets, one small one large, a resin workbench top, and black rear panels. top, and white rear panels.

    # Get the components from the parsed response
    return completion.choices[0].message.parsed.components

searches = structure_user_input("I need three cabinets, one small with shelves, two medium with drawers.n I want two drawer cabinets, one small one large, a wooden workbench top, and black rear panel, and a cabinet that provides power.")

# Function to format the output
def format_component(component):
    return f"Category: {component.category.value}, Requirements: {', '.join(component.requirements)}, Size: {component.size.value if component.size else 'N/A'}"

# Assuming 'searches' is a list of components
def print_searches(searches):
    print("\nThe searches to be done are:")
    for component in searches:
        print(format_component(component))

def convert_to_dict(searches):
    """
    Convert structured user input into a dictionary with metadata.
    
    Args:
        searches: List of WorkbenchComponent objects
        
    Returns:
        dict: Dictionary containing components and metadata
    """
    timestamp = datetime.now()
    
    return {
        "metadata": {
            "createdAt": timestamp.isoformat(),
            "timestamp": timestamp.strftime("%Y%m%d_%H%M%S")
        },
        "components": [
            {
                "category": component.category.value,
                "requirements": component.requirements,
                "size": component.size.value if component.size else None
            }
            for component in searches
        ]
    }

# Create searches directory if it doesn't exist
searches_dir = os.path.join(os.path.dirname(__file__), "searches")
os.makedirs(searches_dir, exist_ok=True)

# Use the new function to convert searches to dict
searches_dict = convert_to_dict(searches)

# Generate filename using timestamp from the dict
filename = f"search_{searches_dict['metadata']['timestamp']}.json"
filepath = os.path.join(searches_dir, filename)

# Save to JSON file
with open(filepath, "w") as f:
    json.dump(searches_dict, f, indent=2)
