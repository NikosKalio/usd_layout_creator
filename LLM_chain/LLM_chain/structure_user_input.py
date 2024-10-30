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
from llama_index.core.program import LLMTextCompletionProgram
from pydantic import BaseModel
from typing import List, Optional

# Load .env
dotenv_path = find_dotenv()
print(f"Dotenv path: {dotenv_path}")
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Print the OpenAI API key (be careful with this in production!)
print(f"OpenAI API Key: {OPENAI_API_KEY}")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")


file_path = 'llm_assets/user_input.txt'

with open(file_path, 'r') as file:
    user_input = file.read()

print(user_input)

# Define a simple output structure
class Cabinet(BaseModel):
    type: str
    requirements: List[str] = []

class WorkbenchTop(BaseModel):
    type: str
    requirements: List[str] = []

class RearPanels(BaseModel):
    needed: bool
    type: Optional[str] = None
    color: Optional[str] = None
    requirements: List[str] = []

class WorkbenchAssembly(BaseModel):
    cabinets: List[Cabinet]
    workbench_top: WorkbenchTop
    rear_panels: RearPanels
    general_requirements: List[str] = []

    def to_dict(self):
        return {
            "cabinets": [cabinet.dict() for cabinet in self.cabinets],
            "workbench_top": self.workbench_top.dict(),
            "rear_panels": self.rear_panels.dict(),
            "general_requirements": self.general_requirements
        }

# Define prompt template
prompt_template_str = """
You are a workbench assembly formatter. Given a description of a workbench setup, extract the following information:

1. Cabinets: List of cabinet types (e.g., "drawer_cabinet", "cabinet_with_hinged_doors", "rolling_cabinet"). 
   For each cabinet, include any specific requirements.
   If types are not specified use at least a drawer cabinet and a hinged door cabinet. 
   If number of cabinets is not specified use 2 cabinets. If size is not specified go for something 725mm depth and 564 wide.

2. Workbench top: The type of workbench top (e.g., "standard", "heavy_duty", "custom").
   Include any specific requirements for the workbench top.
   If nothing is mentioned, use a universal workbench top.

3. Rear panels: Whether rear panels are needed (true/false), and if true, provide panel types and color. 
   Include any specific requirements for the rear panels.
   By default, set as false. If true but no type specified, use blue and 750mm width.

4. General requirements: List any requirements or features that don't fit specifically into the above categories.

The description is: {user_input}

Format the output as a JSON object with the following structure:
{{
  "cabinets": [
    {{
      "type": "cabinet_type_1",
      "requirements": ["requirement1", "requirement2"]
    }},
    {{
      "type": "cabinet_type_2",
      "requirements": ["requirement1", "requirement2"]
    }}
  ],
  "workbench_top": {{
    "type": "top_type",
    "requirements": ["requirement1", "requirement2"]
  }},
  "rear_panels": {{
    "needed": true/false,
    "type": "panel_type",
    "color": "panel_color",
    "requirements": ["requirement1", "requirement2"]
  }},
  "general_requirements": ["requirement1", "requirement2"]
}}

Infer reasonable values for any missing information. Use standard types and colors where not specified.
"""

program = LLMTextCompletionProgram.from_defaults(
    output_cls=WorkbenchAssembly,
    prompt_template_str=prompt_template_str,
    verbose=True,
)

output = program(user_input=user_input)

print(json.dumps(output.to_dict(), indent=2))

# At the end of the file, replace the existing code with:

output_dict = output.to_dict()
print(json.dumps(output_dict, indent=2))

# Generate a unique filename
import datetime
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"workbench_assembly_{timestamp}.json"
directory = 'llm_assets/assembly_json'

# Create the directory if it doesn't exist
os.makedirs(directory, exist_ok=True)

file_path = os.path.join(directory, filename)

# Save the output as a JSON file
with open(file_path, 'w') as json_file:
    json.dump(output_dict, json_file, indent=2)

print(f"Workbench assembly saved as JSON: {file_path}")

def structure_user_input():
    return output_dict
