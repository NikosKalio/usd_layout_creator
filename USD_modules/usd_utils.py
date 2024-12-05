"Utilities for loading/transforming/manipulating usd files"

import os
from pxr import Usd, UsdGeom


def rear_panel_matrix(output_file, panel_files, quantities, rows=1, spacing=0.0):
    """
    Creates a USD scene with rear panels arranged in a grid.

    Args:
        output_file (str): Path to the output USDA file
        panel_files (list): List of panel file paths
        quantities (list): List of quantities for each panel (columns)
        rows (int): Number of rows to create
        spacing (float): Spacing between panels

    Returns:
        tuple: (stage, total_width, total_height) of the created panel matrix
    """
    # Initialize stage
    stage = Usd.Stage.CreateNew(output_file)
    UsdGeom.SetStageUpAxis(stage, "Z")
    
    current_x = 0.0
    current_y = 0.0
    panel_count = 0
    max_height = 0.0
    max_width = 0.0
    
    # Iterate through panels and their quantities
    for panel_file, quantity in zip(panel_files, quantities):
        if not os.path.exists(panel_file):
            print(f"Warning: Panel file {panel_file} does not exist. Skipping.")
            continue
            
        # Create instances for each row and column
        for row in range(rows):
            current_x = 0.0  # Reset X position for each row
            current_y = row * (max_width + spacing)  # Calculate Y position based on row
            
            for col in range(quantity):
                panel_name = os.path.splitext(os.path.basename(panel_file))[0]
                prim_path = f"/Panel_{panel_count}"
                
                try:
                    # Add panel reference
                    panel_prim = stage.DefinePrim(prim_path)
                    panel_prim.GetReferences().AddReference(panel_file)
                    
                    # Get panel dimensions
                    referenced_stage = Usd.Stage.Open(panel_file)
                    panel_geom = None
                    
                    # Find the first boundable geometry
                    for prim in referenced_stage.Traverse():
                        if prim.IsA(UsdGeom.Boundable):
                            panel_geom = UsdGeom.Boundable(prim)
                            break
                    
                    if panel_geom:
                        extent = panel_geom.GetExtentAttr().Get()
                        panel_width = extent[1][0] - extent[0][0]
                        panel_height = extent[1][1] - extent[0][1]
                        
                        max_height = max(max_height, panel_height)
                        max_width = max(max_width, panel_width)
                        
                        # Position panel in grid using current_y
                        xform = UsdGeom.Xform(panel_prim)
                        xform.AddTranslateOp().Set(value=(
                            2 * current_x,
                            current_y,  # Use tracked Y position
                            0.0
                        ))
                        
                        current_x += panel_width + spacing
                    else:
                        print(f"Warning: No geometry found in {panel_file}")
                        
                except Exception as e:
                    print(f"Error processing panel {panel_file}: {e}")
                    continue
                    
                panel_count += 1
    
    total_height = (rows - 1) * (max_width + spacing) if rows > 1 else 0
    
    stage.GetRootLayer().Save()
    return stage, current_x - spacing, total_height  # Subtract last spacing


def merge_usda_files(output_file, top_file, input_files, spacing=0.0):
    """
    Merges multiple USDA files into a new USD scene, positioning them side by side.

    Args:
        output_file (str): Path to the output USDA file.
        input_files (list of str): List of input USDA file paths.
        spacing (float): Spacing between models in the scene.

    Returns:
        None
    """
    # Initialize a new USD stage
    try:
        stage = Usd.Stage.CreateNew(output_file)
    except Exception as e:
        print(f"Error creating output file {output_file}: {e}")
        return

    current_x_translation = 0.0
    prev_length = 0.0
    max_height = 0.0
    max_width = 0.0

    for index, file_path in enumerate(input_files):
        if not os.path.exists(file_path):
            print(f"Warning: Input file {file_path} does not exist. Skipping.")
            continue

        model_name = os.path.splitext(os.path.basename(file_path))[0]
        prim_path = f"/Model_{index}"

        # Add reference to the stage
        try:
            model_prim = stage.DefinePrim(prim_path)
            UsdGeom.SetStageUpAxis(stage, "Z")
            model_prim.GetReferences().AddReference(file_path)
        except Exception as e:
            print(f"Error adding reference to {file_path}: {e}")
            continue

        # Compute translation based on bounding box size
        try:
            referenced_stage = Usd.Stage.Open(file_path)
            model_geometry_prim = referenced_stage.GetPrimAtPath(f'/{model_name}/geometry')

            if model_geometry_prim:
                boundable = UsdGeom.Boundable(model_geometry_prim)
                extent = boundable.GetExtentAttr().Get()
                model_length = extent[1][0] - extent[0][0]  # Bounding box length
                model_width = extent[1][1] - extent[0][1]
                model_height =extent[1][2] - extent[0][2]

                max_height = max(max_height, model_height)
                max_width = max(max_width, model_width)
                current_x_translation += prev_length + model_length + spacing
                prev_length = model_length
            else:
                print(f"Warning: Could not find geometry for {file_path}. Using default spacing.")
                current_x_translation += prev_length + spacing

        except Exception as e:
            print(f"Error computing bounds for {file_path}: {e}")
            continue

        # Apply translation
        try:
            xform = UsdGeom.Xform(model_prim)
            xform.AddTranslateOp().Set(value=(current_x_translation, 0.0, 0.0))
        except Exception as e:
            print(f"Error applying transform to {prim_path}: {e}")
            continue

    total_length = current_x_translation + model_length
    try:
        if os.path.exists(top_file):
            top_prim_path = "/TopModel"
            top_prim = stage.DefinePrim(top_prim_path)
            top_prim.GetReferences().AddReference(top_file)

            # Scale the top model to match the total length
            top_referenced_stage = Usd.Stage.Open(top_file)
            top_geometry_prim = None

            for prim in top_referenced_stage.Traverse():
                if prim.IsA(UsdGeom.Boundable):
                    top_geometry_prim = prim
                    break

            if top_geometry_prim:
                top_boundable = UsdGeom.Boundable(top_geometry_prim)
                top_extent = top_boundable.GetExtentAttr().Get()
                top_length = top_extent[1][0] - top_extent[0][0]
                top_width =top_extent[1][1] - top_extent[0][1]
                top_height =top_extent[1][2] - top_extent[0][2]

                length_scale = (total_length - spacing) / (top_length * 2)
                width_scale = max_width / top_width

                xform = UsdGeom.Xform(top_prim)

                # Position the top model above the merged models
                xform.AddTranslateOp().Set(value=((total_length + spacing) / 2, 0.0, max_height + top_height))
                xform.AddScaleOp().Set(value=(length_scale, width_scale, 1))
            else:
                print(f"Warning: No geometry found in {top_file}. Skipping scaling.")
        else:
            print(f"Error: Top file {top_file} does not exist.")

        stage.GetRootLayer().Save()
        print(f"Scene successfully created with top model: {output_file}")

    except Exception as e:
        print(f"Error adding top file {top_file} to the scene: {e}")

"""
if __name__ == "__main__":
    # Example usage
    input_usda_files = [
    "../assets/components/hinged_door_cabinet_with_bin_1.usda",
    "../assets/components/rolling_cabinet_7.usda",
    "../assets/components/drawer_cabinet_8.usda"
]
    top_usda = "../assets/components/workbench_top_3.usda" 
output_usda_file = "demo_scene.usda"
# merge_usda_files(output_usda_file, input_usda_files, spacing=0.1)
merge_usda_files(output_usda_file, top_usda, input_usda_files, spacing=(2/(3-1)/1000))
"""

#panel_files = ["../assets/components/rear_panel_with_keyholes_5.usda"]
#quantities = [2]  # From your JSON data
#output_file = "rear_panel_row.usda"
#stage, total_width, total_height = rear_panel_matrix(output_file, panel_files, quantities, rows=2, spacing=0)