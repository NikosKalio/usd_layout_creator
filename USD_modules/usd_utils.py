"Utilities for loading/transforming/manipulating usd files"

import os
from pxr import Usd, UsdGeom

def merge_usda_files(output_file, top_file, input_files, panel_file, quantity, layers, spacing=0.0):
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

    current_x_translation = - spacing
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

                length_scale = (total_length) / (top_length * 2)
                width_scale = max_width / top_width

                xform = UsdGeom.Xform(top_prim)

                # Position the top model above the merged models
                xform.AddTranslateOp().Set(value=(total_length / 2, 0.0, max_height + top_height))
                xform.AddScaleOp().Set(value=(length_scale, width_scale, 1))
            else:
                print(f"Warning: No geometry found in {top_file}. Skipping scaling.")
        else:
            print(f"Error: Top file {top_file} does not exist.")

        
        for i in range(layers):
            current_x = 0.0
            for col in range(quantity):
                    prim_path = f"/Panel_{col}_layer_{i}"
                    
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
                            panel_extent = panel_geom.GetExtentAttr().Get()
                            panel_length = panel_extent[1][0] - panel_extent[0][0]
                            panel_width = panel_extent[1][1] - panel_extent[0][1]
                            panel_height =panel_extent[1][2] - panel_extent[0][2]
                            # Position panel in grid
                            xform = UsdGeom.Xform(panel_prim)
                            xform.AddTranslateOp().Set(value=(
                                current_x  + panel_length,
                                model_width + panel_height,
                                max_height + panel_width + i * 2 * panel_width
                            ))
                            xform.AddRotateXOp().Set(value=(90))


                            
                            current_x += 2 * panel_length
                        else:
                            print(f"Warning: No geometry found in {panel_file}")
                            
                    except Exception as e:
                        print(f"Error processing panel {panel_file}: {e}")
                        continue
                    

        stage.GetRootLayer().Save()
        print(f"Scene successfully created with top model: {output_file}")

    except Exception as e:
        print(f"Error adding top file {top_file} to the scene: {e}")



if __name__ == "__main__":
    # Example usage
    input_usda_files = [
    "assets/components/cabinet_with_hinged_doors_1.usda",
    "assets/components/cabinet_with_hinged_doors_2.usda",
    "assets/components/drawer_cabinet_4.usda",
    "assets/components/rolling_cabinet_2.usda",
    "assets/components/cabinet_with_hinged_doors_1.usda",
]
    
    rear_panel = "assets/components/rear_panel_with_keyholes_5.usda"

    quantity = 3
    layers = 3
    top_usda = "assets/components/workbench_top_1.usda" 
output_usda_file = "merged_scene.usda"
# merge_usda_files(output_usda_file, input_usda_files, spacing=0.1)
merge_usda_files(output_usda_file, top_usda, input_usda_files,rear_panel, quantity, layers=3, spacing=0.01)