# Workbench Assembly USD Project

This project focuses on working with Universal Scene Description (USD) files for workbench assemblies. It includes tools for assembling, visualizing, and manipulating USD files related to workbench components.

## Project Structure

### Asset Generator
Located in `asset_generator/`, this module creates an asset library of typical Lista components:
- Processes manually created CSV files based on the Lista catalogue
- Generates USD files for standard components like cabinets, workbench tops, and panels
- Handles unit conversions and metadata embedding

### LLM Chain
Located in `LLM_chain/`, this module provides intelligent component retrieval:
- Indexes generated USDA assets using vector embeddings
- Implements a RAG (Retrieval Augmented Generation) system
- Retrieves components based on similarity search of user prompts
- Structures natural language input into component requirements

### USD Modules
Located in `USD_modules/`, this module handles USD scene creation:
- Defines Pydantic data models for components and assemblies
- Parses USD files into structured component models
- Creates assemblies from component models
- Generates USD scenes from assembly definitions

**Note:** Currently, there are known issues with the USD scene creation where files are imported but not translated properly.

## Core Files
- `workbench_assembler.py`: Main script for assembling workbench components
- `visualization.py`: Script for visualizing USD files
- `usd_utils.py`: Utility functions for working with USD files

### Assets
- `assets/`: Directory containing USD files for workbench components and assemblies
  - `cleaned_workbench_assembly.usda`
  - `workbench_assembly.usda`
  - `workbench_assembly_2.usda`
  - `components/`: Subdirectory for individual workbench components
    - `workbench_top_1.usda`
    - `workbench_top_2.usda`

## Setup

### Virtual Environment
1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- On Windows:
```bash
venv\Scripts\activate
```
- On macOS/Linux:
```bash
source venv/bin/activate
```

## Requirements

This project requires the following Python packages:
- pandas==2.2.3
- usd-core==24.8
- pydantic==2.6.4
- python-dotenv==1.0.1
- llama-index==0.11.19
- openai==1.12.0
- llama-index-core==0.10.10
- typing-extensions==4.10.0

To install the required packages, run:
```bash
pip install -r requirements.txt
```

## Known Issues
- USD scene creation module currently has bugs in component translation
- Component positioning in assemblies needs refinement

- Filepaths needs to be updated. Most likely they are broken when Nikos was structuring the repo.

## Future Developments

### Workshop Environment Generation
- Create comprehensive workshop environment models
- Generate realistic workshop layouts based on space & functionalconstraints

### Enhanced USD Scene Generation
- Implement advanced scene composition based on:
  - Workbench assemblies
  - Workshop environments
  - Natural language user prompts


