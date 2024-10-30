"""
This script provides different strategies for selecting and assembling components based on user queries.
It implements four different selection strategies:
1. Highest K Score: Selects components based on their similarity scores
2. LLM Picker: Uses GPT to select components based on the user's query
3. LLM Different Strategy: Uses GPT to select diverse, complementary components
4. Random Picker: Randomly selects components

Each strategy takes a list of components (with their content and scores) and returns the best assemblies
based on the chosen strategy. The components are typically USD (Universal Scene Description) files
containing 3D furniture/cabinet definitions.

NEEDS DEBUGGING
"""

# takes the n (number of components) x k (number of retrivals per component) and chooses which assemblies to create

#1. highest k score
#2. llm picker
#3. llm different strategy
#4. random picker#
#5. change sequence of cabinets in assembly


import random
import re
from typing import List, Dict, Any
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logging.basicConfig(level=logging.INFO)

def extract_default_prim(content: str) -> str:
    """Extract the defaultPrim name from the content."""
    match = re.search(r'defaultPrim = "(\w+)"', content)
    if match:
        return match.group(1)
    else:
        # If defaultPrim is not found, try to extract the name from the Xform definition
        xform_match = re.search(r'def Xform "(\w+)"', content)
        return xform_match.group(1) if xform_match else "Unknown"



def highest_k_score(component_results: List[Dict[str, Any]], k: int) -> List[Dict[str, Any]]:
    logging.info(f"Entering highest_k_score function with {len(component_results)} results")
    logging.info(f"First component result: {component_results[0]}")
    
    if not component_results:
        logging.warning("No component results provided")
        return []

    if not isinstance(component_results[0], dict):
        logging.error(f"Expected dict, got {type(component_results[0])}")
        return []

    try:
        # Convert score to float if it's a string
        for result in component_results:
            if isinstance(result['score'], str):
                result['score'] = float(result['score'])
        
        sorted_results = sorted(component_results, key=lambda x: x['score'], reverse=True)
        return sorted_results[:k]
    except KeyError as e:
        logging.error(f"KeyError: {e}. 'score' key not found in component result.")
        return []
    except (TypeError, ValueError) as e:
        logging.error(f"Error: {e}. Unexpected data structure or value in component results.")
        return []

def llm_picker(components: List[Dict[str, Any]], k: int, query: str) -> List[Dict[str, Any]]:
    """
    Strategy 2: Use LLM to pick the best result for each component based on the query.
    """
    prompt = f"Given the following components and the user query '{query}', select the best option for each component:\n\n"
    for i, component in enumerate(components):
        prompt += f"Component {i+1}:\n"
        prompt += f"1. {extract_default_prim(component['content'])} (Score: {component['score']})\n"
        prompt += "\n"
    prompt += f"For each component, return only the number of the best option, separated by spaces."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content.strip()
    
    # Extract numbers from the response
    numbers = re.findall(r'\d+', content)
    
    if len(numbers) != len(components):
        print(f"Warning: LLM response doesn't match the number of components. Using default selection.")
        numbers = ['1'] * len(components)

    selected_indices = [int(num) - 1 for num in numbers]
    
    return [
        {
            'content': extract_default_prim(components[i][min(j, len(components[i])-1)]['content']),
            'score': components[i][min(j, len(components[i])-1)]['score']
        }
        for i, j in enumerate(selected_indices)
    ]

def llm_different_strategy(components: List[List[Dict[str, Any]]], k: int, query: str) -> List[Dict[str, Any]]:
    """
    Strategy 3: Use LLM to pick results using a different strategy.
    """
    prompt = f"Given the following components and the user query '{query}', select diverse options that complement each other:\n\n"
    for i, component_results in enumerate(components):
        prompt += f"Component {i+1}:\n"
        for j, result in enumerate(component_results):
            prompt += f"{j+1}. {extract_default_prim(result['content'])} (Score: {result['score']})\n"
        prompt += "\n"
    prompt += f"For each component, return only the number of the selected option, separated by spaces."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content.strip()
    
    # Extract numbers from the response
    numbers = re.findall(r'\d+', content)
    
    if len(numbers) != len(components):
        print(f"Warning: LLM response doesn't match the number of components. Using default selection.")
        numbers = ['1'] * len(components)

    selected_indices = [int(num) - 1 for num in numbers]
    
    return [
        {
            'content': extract_default_prim(components[i][min(j, len(components[i])-1)]['content']),
            'score': components[i][min(j, len(components[i])-1)]['score']
        }
        for i, j in enumerate(selected_indices)
    ]

def random_picker(components: List[List[Dict[str, Any]]], k: int) -> List[Dict[str, Any]]:
    """
    Strategy 4: Randomly pick one result for each component.
    """
    return [
        {
            'content': extract_default_prim(random.choice(component_results)['content']),
            'score': random.choice(component_results)['score']
        }
        for component_results in components
    ]



def choose_assemblies(components: List[Dict[str, Any]], k: int, query: str) -> Dict[str, Any]:
    logging.info(f"Choosing assemblies for query: {query}")
    logging.info(f"Number of components: {len(components)}")
    logging.info(f"First component: {components[0]}")

    try:
        return {
            "highest_k_score": highest_k_score(components, k),
            "llm_picker": llm_picker(components, k, query),
            "llm_different_strategy": llm_different_strategy(components, k, query),
            "random_picker": random_picker(components, k)
        }
    except Exception as e:
        logging.exception(f"Error in choose_assemblies: {e}")
        return {}

# Example usage
if __name__ == "__main__":
    components = [
        [
            {
                "content": '''#usda 1.0
(
    defaultPrim = "cabinet_with_hinged_doors_7"
)

def Xform "cabinet_with_hinged_doors_7" (
    kind = "component"
)
{
    def Cube "geometry" (
        customData = {
            string color_attribute = "Null"
            int depth = 725
            string function = "Cabinet with hinged door to accommodate larger object storage"
            int height = 800
            string material = "Metal"
            string type = "Cabinet with hinged doors"
            int width = 717
        }
    )
    {
        float3[] extent = [(-0.3585, -0.3625, -0.4), (0.3585, 0.3625, 0.4)]
        color3f[] primvars:displayColor = [(1, 1, 1)]
        float3 xformOp:scale = (0.717, 0.725, 0.8)
        uniform token[] xformOpOrder = ["xformOp:scale"]
    }
}''',
                "score": 0.3523
            },
            {
                "content": '''#usda 1.0
(
    defaultPrim = "cabinet_with_hinged_doors_7"
)

def Xform "cabinet_with_hinged_doors_7" (
    kind = "component"
)
{
    def Cube "geometry" (
        customData = {
            string color_attribute = "Null"
            int depth = 725
            string function = "Cabinet with hinged door to accommodate larger object storage"
            int height = 800
            string material = "Metal"
            string type = "Cabinet with hinged doors"
            int width = 717
        }
    )
    {
        float3[] extent = [(-0.3585, -0.3625, -0.4), (0.3585, 0.3625, 0.4)]
        color3f[] primvars:displayColor = [(1, 1, 1)]
        float3 xformOp:scale = (0.717, 0.725, 0.8)
        uniform token[] xformOpOrder = ["xformOp:scale"]
    }
}''',
                "score": 0.6523
            },
            {
                "content": '''#usda 1.0
(
    defaultPrim = "wide_drawer_cabinet"
)

def Xform "wide_drawer_cabinet" (
    kind = "component"
)
{
    // ... content for wide drawer cabinet ...
}''',
                "score": 0.8312
            },
            {
                "content": '''#usda 1.0
(
    defaultPrim = "wide_drawer_cabinet"
)

def Xform "wide_drawer_cabinet" (
    kind = "component"
)
{
    // ... content for wide drawer cabinet ...
}''',
                "score": 0.8312
            }
        ],
        [
            {
                "content": '''#usda 1.0
(
    defaultPrim = "universal_workbench_top"
)

def Xform "universal_workbench_top" (
    kind = "component"
)
{
    // ... content for universal workbench top ...
}''',
                "score": 0.9105
            },
            {
                "content": '''#usda 1.0
(
    defaultPrim = "impact_resistant_workbench_top"
)

def Xform "impact_resistant_workbench_top" (
    kind = "component"
)
{
    // ... content for impact-resistant workbench top ...
}''',
                "score": 0.7001
            },
            {
                "content": '''#usda 1.0
(
    defaultPrim = "heavy_duty_workbench_top"
)

def Xform "heavy_duty_workbench_top" (
    kind = "component"
)
{
    // ... content for heavy-duty workbench top ...
}''',
                "score": 0.8956
            }
        ],
        [
            {
                "content": '''#usda 1.0
(
    defaultPrim = "blue_rear_panels"
)

def Xform "blue_rear_panels" (
    kind = "component"
)
{
    // ... content for blue rear panels ...
}''',
                "score": 0.7845
            },
            {
                "content": '''#usda 1.0
(
    defaultPrim = "perforated_rear_panels"
)

def Xform "perforated_rear_panels" (
    kind = "component"
)
{
    // ... content for perforated rear panels ...
}''',
                "score": 0.7723
            },
            {
                "content": '''#usda 1.0
(
    defaultPrim = "white_rear_panels"
)

def Xform "white_rear_panels" (
    kind = "component"
)
{
    // ... content for white rear panels ...
}''',
                "score": 0.7612
            }
        ]
    ]

    query = "I want a workbench with storage"
    k = 3

    results = choose_assemblies(components, k, query)

 #   for strategy, selected_components in results.items():
 #       print(f"\n{strategy.replace('_', ' ').title()}:")
 #       for comp in selected_components:
 #           print(f"- {comp['content']} (Score: {comp['score']})")


    # Add multiple runs for random picker to show variability
    # print("\nRandom Picker (4 runs):")
    for i in range(4):
        random_results = random_picker(components, k)
        print(f"\nRun {i+1}:")
        for comp in random_results:
            print(f"- {extract_default_prim(comp['content'])} (Score: {comp['score']})")
