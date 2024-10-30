"""
This script processes user input for furniture assembly, specifically for workbench configurations.
It follows a multi-step pipeline:

1. Structures raw user input into a standardized format
2. Retrieves relevant components based on user requirements
3. Generates assembly recommendations for each component category
4. Outputs final assembly configurations

The script handles various furniture components including cabinets, workbench tops, and rear panels,
while considering both specific and general requirements for each component.

Dependencies:
- structure_user_input: Formats raw user input
- component_retriever: Finds matching components
- assembly_chooser: Selects optimal assembly configurations
"""

import json
import logging
from structure_user_input import structure_user_input
from component_retriever import retrieve_components
from assembly_chooser import choose_assemblies
from dotenv import load_dotenv, find_dotenv
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load .env
dotenv_path = find_dotenv()
logging.info(f"Dotenv path: {dotenv_path}")
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
logging.info(f"OpenAI API Key: {OPENAI_API_KEY[:10]}...") # Only log the first 10 characters for security

def main():
    try:
        logging.info("Starting main function")
        
        # Step 1: Structure user input
        logging.info("Step 1: Structuring user input")
        structured_input = structure_user_input()
        if not structured_input:
            raise ValueError("No structured input received")
        logging.info(f"Structured input: {json.dumps(structured_input, indent=2)}")

        # Step 2: Retrieve components for each part of the structured input
        logging.info("Step 2: Retrieving components")
        retrieved_components = {}
        
        for component_type, component_data in structured_input.items():
            logging.info(f"Processing component type: {component_type}")
            logging.info(f"Component data: {component_data}")
            
            if component_type == 'general_requirements':
                logging.info("Skipping general requirements")
                continue  # Skip general requirements, handle them separately

            if isinstance(component_data, list):
                # Handle list of components (e.g., cabinets)
                logging.info(f"Handling list of components for {component_type}")
                retrieved_components[component_type] = []
                for item in component_data:
                    query = f"I need a {item['type']} {component_type} with these requirements: {', '.join(item['requirements'])}."
                    if structured_input.get('general_requirements'):
                        query += f" Also keep in mind {', '.join(structured_input['general_requirements'])}."
                    logging.info(f"Query: {query}")
                    result = retrieve_components(query)
                    logging.info(f"Retrieved result: {result}")
                    retrieved_components[component_type].append(result)
            elif isinstance(component_data, dict):
                # Handle single component types (e.g., workbench_top, rear_panels)
                logging.info(f"Handling single component for {component_type}")
                if component_type == 'rear_panels' and not component_data.get('needed', False):
                    logging.info("Skipping rear panels as they are not needed")
                    continue  # Skip rear panels if not needed
                query = f"I need a {component_data.get('type', '')} {component_type}"
                if 'requirements' in component_data:
                    query += f" with these requirements: {', '.join(component_data['requirements'])}."
                if structured_input.get('general_requirements'):
                    query += f" Also keep in mind {', '.join(structured_input['general_requirements'])}."
                logging.info(f"Query: {query}")
                result = retrieve_components(query)
                logging.info(f"Retrieved result: {result}")
                retrieved_components[component_type] = result

        logging.info(f"All retrieved components: {json.dumps(retrieved_components, indent=2)}")

        # Step 3: Choose assemblies for each category
        logging.info("Step 3: Choosing assemblies")
        final_assemblies = {}
        for category, components in retrieved_components.items():
            logging.info(f"Processing category: {category}")
            logging.info(f"Components: {components}")
            if isinstance(components, list) and len(components) > 0 and isinstance(components[0], list):  # For categories with multiple items (e.g., cabinets)
                final_assemblies[category] = []
                for comp_list in components:
                    assemblies = choose_assemblies(comp_list, k=3, query=category)
                    final_assemblies[category].append(assemblies)
            else:
                assemblies = choose_assemblies(components, k=3, query=category)
                final_assemblies[category] = assemblies
            logging.info(f"Assemblies for {category}: {assemblies}")

        # Step 4: Output the results
        logging.info("Step 4: Outputting results")
        if not final_assemblies:
            logging.warning("No assemblies were generated.")
        else:
            logging.info(f"Final assemblies: {json.dumps(final_assemblies, indent=2)}")

    except Exception as e:
        logging.exception(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
