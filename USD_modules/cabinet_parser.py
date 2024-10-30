"""
Cabinet Parser Module

This script provides functionality to parse and analyze USD (Universal Scene Description) cabinet files
and create cabinet assemblies. It performs the following main functions:

1. Extracts properties from USD cabinet files including:
   - Dimensions, colors, and materials
   - Custom data (function, type)
   - Transform operations
   - Geometry information

2. Creates cabinet assemblies by:
   - Processing multiple cabinet USD files
   - Combining them into a single assembly
   - Checking for consistency between cabinets
   - Calculating total assembly dimensions

The script uses two main functions:
- extract_usd_properties(): Parses individual USD files into CabinetModel objects
- create_assembly(): Combines multiple cabinets into a CabinetAssembly

Dependencies: pxr (USD), custom models (CabinetModel, AssemblyModel, CabinetAssembly)
"""

# Takes the path of a set of cabinets and returns a cabinet model
# extracts a length range

from models import CabinetModel, AssemblyModel, CabinetAssembly
from pxr import Usd, UsdGeom
from typing import Dict, Any, List, Tuple
import os

# assets/components/cabinet_with_hinged_doors_4.usda
# assets/components/rolling_cabinet_6.usda




def extract_usd_properties(file_path: str) -> CabinetModel:
    stage = Usd.Stage.Open(file_path)
    if not stage:
        raise ValueError(f"Failed to open USD stage for {file_path}")

    root_prim = stage.GetDefaultPrim()
    if not root_prim:
        raise ValueError(f"No default prim found in {file_path}")

    # Extract kind
    kind = Usd.ModelAPI(root_prim).GetKind()

    # Find the geometry prim
    geometry_prim = root_prim.GetChild("geometry")
    if not geometry_prim:
        raise ValueError(f"No geometry prim found in {file_path}")

    # Extract custom data
    custom_data = geometry_prim.GetCustomData()

    # Extract extent
    extent_attr = geometry_prim.GetAttribute("extent")
    extent = extent_attr.Get() if extent_attr else None

    # Extract display color
    display_color_attr = geometry_prim.GetAttribute("primvars:displayColor")
    display_color = display_color_attr.Get() if display_color_attr else None

    # Extract xformOps
    xform_ops = {}
    xformable = UsdGeom.Xformable(geometry_prim)
    for op in xformable.GetOrderedXformOps():
        op_name = op.GetOpName()
        op_value = op.Get()
        xform_ops[op_name] = op_value

    # Extract xformOpOrder
    xform_op_order_attr = geometry_prim.GetAttribute("xformOpOrder")
    xform_op_order = xform_op_order_attr.Get() if xform_op_order_attr else None

    return CabinetModel(
        name=os.path.splitext(os.path.basename(file_path))[0],
        asset_path=file_path,
        dimensions=tuple(xform_ops.get('xformOp:scale', (1.0, 1.0, 1.0))),
        function=custom_data.get('function', 'Unknown'),
        type=custom_data.get('type', 'Unknown'),
        color=tuple(display_color[0]) if display_color else (1.0, 1.0, 1.0),  # Default to white if no color is specified
        material=custom_data.get('material', 'Unknown')
    )






def create_assembly(cabinet_paths: List[str]) -> CabinetAssembly:
    cabinets = []
    for path in cabinet_paths:
        try:
            cabinet = extract_usd_properties(path)
            cabinets.append(cabinet)
        except ValueError as e:
            print(f"Error processing {path}: {e}")
    
    assembly = CabinetAssembly(cabinets=cabinets)
    
    # Check for consistency and print any warnings
    warnings = assembly.check_consistency()
    for warning in warnings:
        print(warning)
    
    return assembly

# Example usage:
cabinet_paths = [
    "assets/components/drawer_cabinet_2.usda",
    "assets/components/cabinet_with_hinged_doors_4.usda",
    "assets/components/rolling_cabinet_6.usda"
]

try:
    assembly = create_assembly(cabinet_paths)
    print("Assembly created successfully:")
    print(f"Number of cabinets: {len(assembly.cabinets)}")
    print(f"Total length of assembly: {assembly.total_length}")

    # Print details of each cabinet
    for i, cabinet in enumerate(assembly.cabinets, 1):
        print(f"\nCabinet {i}:")
        print(f"  Name: {cabinet.name}")
        print(f"  Asset Path: {cabinet.asset_path}")
        print(f"  Dimensions: {cabinet.dimensions}")
        print(f"  Function: {cabinet.function}")
        print(f"  Type: {cabinet.type}")
        print(f"  Color: {cabinet.color}")
        print(f"  Material: {cabinet.material}")

except Exception as e:
    print(f"Error creating assembly: {e}")


