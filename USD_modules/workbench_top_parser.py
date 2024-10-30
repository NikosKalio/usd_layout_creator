"""
This module handles the parsing and extraction of properties from USD (Universal Scene Description) files
specifically for workbench top components. It provides functionality to:
- Read USD files containing workbench top geometry
- Extract properties like dimensions, material, color, and type
- Convert the USD data into WorkbenchTopModel objects for further processing
- Handle unit conversions (mm to meters)

The module serves as a bridge between USD asset files and the application's internal data model,
making it easier to work with workbench top components in a standardized way.
"""

from models import WorkbenchTopModel
from pxr import Usd, UsdGeom
import os

def extract_workbench_top_properties(file_path: str) -> WorkbenchTopModel:
    stage = Usd.Stage.Open(file_path)
    if not stage:
        raise ValueError(f"Failed to open USD stage for {file_path}")

    root_prim = stage.GetDefaultPrim()
    if not root_prim:
        raise ValueError(f"No default prim found in {file_path}")

    # Find the geometry prim
    geometry_prim = root_prim.GetChild("geometry")
    if not geometry_prim:
        raise ValueError(f"No geometry prim found in {file_path}")

    # Extract custom attributes
    custom_data = geometry_prim.GetCustomData()
    function = custom_data.get("function", "Unknown")
    type_ = custom_data.get("type", "Unknown")
    material = custom_data.get("material", "Unknown")
    
    # Extract dimensions
    width = custom_data.get("width", 0) / 1000  # Convert mm to meters
    depth = custom_data.get("depth", 0) / 1000  # Convert mm to meters
    height = custom_data.get("height", 0) / 1000  # Convert mm to meters
    
    # Extract color
    display_color_attr = geometry_prim.GetAttribute("primvars:displayColor")
    color = tuple(display_color_attr.Get()[0]) if display_color_attr else (0.5, 0.5, 0.5)

    return WorkbenchTopModel(
        name=os.path.splitext(os.path.basename(file_path))[0],
        asset_path=file_path,
        dimensions=(width, depth, height),
        function=function,
        type=type_,
        color=color,
        material=material
    )

def create_workbench_top(workbench_top_path: str) -> WorkbenchTopModel:
    try:
        workbench_top = extract_workbench_top_properties(workbench_top_path)
        return workbench_top
    except ValueError as e:
        print(f"Error processing {workbench_top_path}: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    workbench_top_path = "assets/components/workbench_top_1.usda"

    try:
        workbench_top = create_workbench_top(workbench_top_path)
        if workbench_top:
            print("Workbench top created successfully:")
            print(f"Name: {workbench_top.name}")
            print(f"Dimensions: {workbench_top.dimensions}")
            print(f"Asset Path: {workbench_top.asset_path}")
            print(f"Function: {workbench_top.function}")
            print(f"Type: {workbench_top.type}")
            print(f"Color: {workbench_top.color}")
            print(f"Material: {workbench_top.material}")
    except Exception as e:
        print(f"Error creating workbench top: {e}")
