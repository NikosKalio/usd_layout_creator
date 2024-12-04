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
from structure_user_input import structure_user_input, convert_to_dict
from component_retriever import retrieve_modules, retriever, index
from retrieval_utils import width_cabinet,calculate_rear_panels_constrained, construct_file_path
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
    # Get user input
    print("\nPlease describe your workbench configuration needs.")
    print("Example: 'I need three cabinets, one small with shelves, two medium with drawers, a wooden workbench top, and black rear panels'")
    user_input = """I need a modular workspace setup that includes three cabinets: 
    One bin cabinet on the left, small-sized with a compact footprint, 
    one rolling cabinet in the center, small-sized with smooth castors for mobility, designed with multiple drawers, 
    and one drawer cabinet on the right, small-sized and optimized for tool storage. 
    The workbench should have an ABS top for durability and easy maintenance. 
    The rear of the setup requires three rows of rear panels, designed for modular functionality and support."""
    #input("\nEnter your requirements: ")
    
    # Validate input is not empty
    if not user_input.strip():
        raise ValueError("User input cannot be empty")
    try:
        logging.info("Starting main function")


        
        # Step 1: Structure user input
        logging.info("Step 1: Structuring user input")
        structured_input = structure_user_input(user_input)
        if not structured_input:
            raise ValueError("No structured input received")
        searches = convert_to_dict(structured_input)
        logging.info(f"Structured input: {(json.dumps(searches, indent=2))}")




        # Step 2: Retrieve components for each part of the structured input
        cabinets = [c for c in searches['components'] if c['category'] == "Cabinet"]
        for cabinet in cabinets:
            try:
                retrieved_modules = retrieve_modules(str(cabinet))
                if retrieved_modules:
                    # Assuming you want the first result's default_prim
                    cabinet['filepath'] = retrieved_modules[0]['default_prim']
                else:
                    cabinet['filepath'] = None
            except Exception as e:
                logging.error(f"Failed to retrieve module for cabinet: {cabinet}. Error: {e}")
                cabinet['filepath'] = None

        logging.info(f"Retrieved cabinets: {json.dumps(cabinets, indent=2)}")

        workbenches = [c for c in searches['components'] if c['category'] == "Workbench Top"]
        for workbench in workbenches:
            try:
                retrieved_modules = retrieve_modules(str(workbench))
                if retrieved_modules:
                    # Assuming you want the first result's default_prim
                    workbench['filepath'] = retrieved_modules[0]['default_prim']
                else:
                    workbench['filepath'] = None
            except Exception as e:
                logging.error(f"Failed to retrieve module for workbench: {workbench}. Error: {e}")
                workbench['filepath'] = None


                
        # Step 3: Add filepaths to the json
        assembly_data_model = searches  # This is a dictionary

        # Overwrite the cabinets and workbench with the updated data
        # Remove existing cabinets and workbench top from the components
        assembly_data_model['components'] = [
            component for component in assembly_data_model['components']
            if component['category'] not in ["Cabinet", "Workbench Top"]
        ]
        # Add the updated cabinets and workbench to the components
        assembly_data_model['components'].extend(cabinets)
        assembly_data_model['components'].extend(workbenches)
        logging.info("Assembly data model after adding cabinets and workbenches: %s", json.dumps(assembly_data_model, indent=2))



        # Step 4: Calculate length and config of rear panels
        # Calculate total width of cabinets using the width_cabinet function
        cabinet_filepaths = [construct_file_path(cabinet['filepath']) for cabinet in cabinets if cabinet['filepath']]
        cabinet_widths = width_cabinet(cabinet_filepaths)
        total_cabinet_width = round(sum(cabinet_widths) * 1000)
        logging.info(f"Total width of cabinets: {total_cabinet_width}")

        # Calculate rear panel configuration
        panels_config = calculate_rear_panels_constrained(total_cabinet_width)
        logging.info(f"Rear panel configuration: {panels_config }")

        # Step 5: Add rear panels to the assembly data model

        # Check if there is a category "Rear Panels" in the assembly data model
        rear_panels_components = [
            component for component in assembly_data_model['components']
            if component['category'] == "Rear Panels"
        ]

        if not rear_panels_components:
            logging.info("No 'Rear Panels' category found in the assembly data model.")
        else:
            logging.info("Adding rear panels to the assembly data model")
            rear_panels = []

            # L_panels['quantity_a'] and L_panels['quantity_b'] are calculated in step 4
            quantity_a = panels_config['a']
            quantity_b = panels_config['b']

            # Nest rear panels as children under 'size' in the existing rear panel component
            for panel in rear_panels_components:
                panel['size'] = []
                if quantity_a > 0:
                    panel['size'].append({
                        'filepath': 'rear_panel_with_keyholes_4',
                        'quantity': quantity_a
                    })
                    logging.info(f"Adding {quantity_a} rear panels to the nested panels under 'size'")

                if quantity_b > 0:
                    panel['size'].append({
                        'filepath': 'rear_panel_with_keyholes_5',
                        'quantity': quantity_b
                    })
                    logging.info(f"Adding {quantity_b} rear panels to the nested panels under 'size'")

            logging.info("Assembly data model after nesting rear panels under 'size': %s", json.dumps(assembly_data_model, indent=2))

        # Step 6: write metadata
        assembly_data_model['metadata'] = {
            'W_tot_cabinets': total_cabinet_width,
            'spacing': panels_config['spacing'],
            'number_of_cabinets': len(cabinets)
        }
        logging.info(f"Metadata added to assembly data model: {json.dumps(assembly_data_model, indent=2)}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
