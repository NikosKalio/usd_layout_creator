"""
USD Scene Creator Module

This module provides functionality for creating and manipulating USD (Universal Scene Description) scenes
specifically for workbench assemblies. It handles:

1. Creating new USD scenes with workbench components (cabinets and tops)
2. Importing and referencing USD assets
3. Applying transformations to position cabinets sequentially
4. Scaling and positioning workbench tops relative to the cabinet assembly
5. Managing USD layers and sublayers for transformation data

The module works with AssemblyModel objects that contain metadata about cabinets
and workbench tops, including their dimensions and asset paths.
"""

from pxr import Usd, UsdGeom, Sdf, Gf, Vt
from typing import List
from models import AssemblyModel

# create scene, import assets, scale workbench top accordinly
#WEORK IN PROGRESS

def create_usd_scene(assembly: AssemblyModel, output_path: str) -> None:
    """
    Create a USD scene from the given assembly model.
    
    :param assembly: The AssemblyModel containing cabinets and workbench top
    :param output_path: The path where the USD file will be saved
    """
    # Create a new USD stage
    stage = Usd.Stage.CreateNew(output_path)

    # Define a root Xform for the assembly
    root_xform = UsdGeom.Xform.Define(stage, '/WorkbenchAssembly')

    # Import cabinets
    for i, cabinet in enumerate(assembly.cabinets.cabinets):
        prim_path = f'/WorkbenchAssembly/Cabinet_{i+1}'
        import_asset(stage, prim_path, cabinet.asset_path)

    # Import workbench top with scaling based on dimensions
    workbench_prim_path = '/WorkbenchAssembly/WorkbenchTop'
    import_asset_with_transform(stage, workbench_prim_path, assembly.workbench_top.asset_path, 
                                Gf.Vec3d(*assembly.workbench_top.dimensions))

    # Save the stage
    stage.GetRootLayer().Save()

def import_asset(stage: Usd.Stage, prim_path: str, asset_path: str) -> None:
    """
    Import (reference) an asset into the USD stage.
    
    :param stage: The USD stage
    :param prim_path: The prim path where the asset will be referenced
    :param asset_path: The path to the asset file
    """
    prim = UsdGeom.Xform.Define(stage, prim_path)
    
    # Extract the file name from the asset_path
    file_name = asset_path.split('/')[-1]
    prim.GetPrim().GetReferences().AddReference(f"./components/{file_name}")

def import_asset_with_transform(stage: Usd.Stage, prim_path: str, asset_path: str, scale: Gf.Vec3d) -> None:
    """
    Import (reference) an asset into the USD stage with scaling.
    
    :param stage: The USD stage
    :param prim_path: The prim path where the asset will be referenced
    :param asset_path: The path to the asset file
    :param scale: The scale to apply (x, y, z)
    """
    prim = UsdGeom.Xform.Define(stage, prim_path)
    
    # Apply scale
    scaleOp = prim.AddScaleOp()
    scaleOp.Set(scale)
    
    # Reference the asset
    # Extract the file name from the asset_path
    file_name = asset_path.split('/')[-1]
    prim.GetPrim().GetReferences().AddReference(f"./components/{file_name}")

def add_sub_layer(sub_layer_path: str, root_layer) -> Sdf.Layer:
    sub_layer: Sdf.Layer = Sdf.Layer.CreateNew(sub_layer_path)
    root_layer.subLayerPaths.append(sub_layer.identifier)
    return sub_layer

def sequence_cabinets(stage: Usd.Stage, sub_layer: Sdf.Layer, assembly: AssemblyModel) -> float:
    """
    Sequence the cabinets next to each other, aligned along the Z-axis.
    The first cabinet is placed at 0.0, and subsequent cabinets are placed
    at the sum of half their width and half the width of the previous cabinet.
    
    :param stage: The USD stage containing the scene
    :param sub_layer: The sublayer where transformations will be stored
    :param assembly: The AssemblyModel containing cabinet metadata
    :return: The total width of all cabinets
    """
    current_x = 0.0
    previous_half_width = 0.0

    for i, cabinet in enumerate(assembly.cabinets.cabinets):
        cabinet_path = f"/WorkbenchAssembly/Cabinet_{i+1}"
        cabinet_prim = stage.GetPrimAtPath(cabinet_path)
        
        if not cabinet_prim:
            print(f"Warning: Cabinet_{i+1} not found")
            continue

        # Get the cabinet's dimensions from the model
        cabinet_width, cabinet_height, cabinet_depth = cabinet.dimensions
        
        # Calculate the X position for this cabinet
        if i == 0:
            # First cabinet is placed at 0.0
            x_position = 0.0
        else:
            # Subsequent cabinets are placed at the sum of half their width and half the previous cabinet's width
            x_position = current_x + previous_half_width + (cabinet_width / 2)

        # Create an over in the sublayer
        over = Sdf.CreatePrimInLayer(sub_layer, cabinet_path)
        over.specifier = Sdf.SpecifierOver

        # Calculate the transformation
        # X: calculated position, Y: 0, Z: align back face to Z=0
        translation = Gf.Vec3d(x_position, 0, 0)
        
        # Apply the transformation
        xformable = UsdGeom.Xformable(cabinet_prim)
        xformable.ClearXformOpOrder()  # Clear existing transform operations
        translate_op = xformable.AddTranslateOp()
        translate_op.Set(translation)

        # Set the xformOpOrder explicitly
        xformable.SetXformOpOrder([translate_op])

        # Update the current X position and previous half width for the next iteration
        current_x = x_position
        previous_half_width = cabinet_width / 2

        print(f"Placed Cabinet_{i+1} at X: {x_position}")

    # Calculate and return the total width (position of the last cabinet + its half width)
    total_width = current_x + previous_half_width
    return total_width

def apply_transformation(input_path: str, output_path: str, assembly: AssemblyModel) -> None:
    """
    Apply transformations to place cabinets next to each other and position the workbench top.
    
    :param input_path: Path to the input USD file
    :param output_path: Path where the transformed USD file will be saved
    :param assembly: The AssemblyModel containing metadata for the entire assembly
    """
    # Open the input stage
    stage = Usd.Stage.Open(input_path)
    
    # Get the root layer
    root_layer = stage.GetRootLayer()
    
    # Create a new sublayer
    sub_layer = add_sub_layer(output_path, root_layer)
    
    # Get the WorkbenchAssembly prim
    assembly_prim = stage.GetPrimAtPath("/WorkbenchAssembly")
    if not assembly_prim:
        raise RuntimeError("WorkbenchAssembly prim not found")

    # Sequence the cabinets and get the total width
    total_cabinet_width = sequence_cabinets(stage, sub_layer, assembly)

    # Handle the WorkbenchTop
    workbench_top_path = "/WorkbenchAssembly/WorkbenchTop"
    workbench_top_prim = stage.GetPrimAtPath(workbench_top_path)
    
    if workbench_top_prim:
        # Create an over in the sublayer
        over = Sdf.CreatePrimInLayer(sub_layer, workbench_top_path)
        over.specifier = Sdf.SpecifierOver

        # Get the workbench top dimensions from the model
        workbench_width, workbench_height, workbench_depth = assembly.workbench_top.dimensions
        
        # Calculate the transformation (center it over the cabinets)
        translation = Gf.Vec3d(total_cabinet_width / 2 - workbench_width / 2, 0, workbench_depth / 2)
        
        # Apply the transformation
        xformable = UsdGeom.Xformable(workbench_top_prim)
        translate_op = xformable.AddTranslateOp()
        translate_op.Set(translation)

        # Update the xformOpOrder
        current_order = xformable.GetOrderedXformOps()
        new_order = current_order + [translate_op]
        xformable.SetXformOpOrder(new_order)

    # Save the stage
    stage.Save()


# Example usage
if __name__ == "__main__":
    from create_assembly_model import create_full_assembly

    cabinet_paths = [
        "assets/components/drawer_cabinet_2.usda",
        "assets/components/cabinet_with_hinged_doors_4.usda",
        "assets/components/rolling_cabinet_2.usda"
    ]
    workbench_top_path = "assets/components/workbench_top_1.usda"

    try:
        assembly = create_full_assembly(cabinet_paths, workbench_top_path)
        initial_scene_path = "assets/final_workbench_assembly.usda"
        transformed_scene_path = "assets/workbench_transformations.usda"
        
        create_usd_scene(assembly, initial_scene_path)
        print(f"Initial USD scene created successfully at {initial_scene_path}")
        
        apply_transformation(initial_scene_path, transformed_scene_path, assembly)
        print(f"Transformed USD scene created successfully as a sublayer at {transformed_scene_path}")
    except Exception as e:
        print(f"Error creating or transforming USD scene: {str(e)}")
