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

import logging
from LLM_chain.LLM_chain.structure_user_input import structure_user_input, convert_to_dict
from LLM_chain.LLM_chain.component_retriever import retrieve_modules
from LLM_chain.LLM_chain.retrieval_utils import width_cabinet,calculate_rear_panels_constrained, construct_file_path
from dotenv import load_dotenv, find_dotenv
import os

# Load .env
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def main(user_input):
    # Get user input
    # print("\nPlease describe your workbench configuration needs.")
    # print("Example: 'I need three cabinets, one small with shelves, two medium with drawers, a wooden workbench top, and black rear panels'")
    #input("\nEnter your requirements: ")
    
    # Validate input is not empty
    if not user_input.strip():
        raise ValueError("User input cannot be empty")
    try:


        
        # Step 1: Structure user input
        structured_input = structure_user_input(user_input)
        if not structured_input:
            raise ValueError("No structured input received")
        searches = convert_to_dict(structured_input)

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

        # Step 4: Calculate length and config of rear panels
        # Calculate total width of cabinets using the width_cabinet function
        cabinet_filepaths = [construct_file_path(cabinet['filepath']) for cabinet in cabinets if cabinet['filepath']]
        cabinet_widths = width_cabinet(cabinet_filepaths)
        total_cabinet_width = round(sum(cabinet_widths) * 1000)

        # Calculate rear panel configuration
        panels_config = calculate_rear_panels_constrained(total_cabinet_width)

        # Step 5: Add rear panels to the assembly data model

        # Check if there is a category "Rear Panels" in the assembly data model
        rear_panels_components = [
            component for component in assembly_data_model['components']
            if component['category'] == "Rear Panels"
        ]

        if rear_panels_components:

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

                if quantity_b > 0:
                    panel['size'].append({
                        'filepath': 'rear_panel_with_keyholes_5',
                        'quantity': quantity_b
                    })

        #Step 6: append metadata (don't overwrite)
        if 'metadata' not in assembly_data_model:
            assembly_data_model['metadata'] = {}

        assembly_data_model['metadata'].update({
            'W_tot_cabinets': total_cabinet_width,
            'spacing': panels_config['spacing'],
            'number_of_cabinets': len(cabinets)
        })

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    return assembly_data_model
