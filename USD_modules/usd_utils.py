"Utilities for loading/transforming/manipulating usd files"

import os
from pxr import Usd, UsdGeom

def merge_usda_files(output_file, input_files, spacing=0.0):
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
    prev_width = 0.0

    for index, file_path in enumerate(input_files):
        if not os.path.exists(file_path):
            print(f"Warning: Input file {file_path} does not exist. Skipping.")
            continue

        model_name = os.path.splitext(os.path.basename(file_path))[0]
        prim_path = f"/Model_{index}"

        # Add reference to the stage
        try:
            model_prim = stage.DefinePrim(prim_path)
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
                model_width = extent[1][0] - extent[0][0]  # Bounding box width

                current_x_translation += prev_width + model_width + spacing
                prev_width = model_width
            else:
                print(f"Warning: Could not find geometry for {file_path}. Using default spacing.")
                current_x_translation += prev_width + spacing

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

    # Save the output stage
    try:
        stage.GetRootLayer().Save()
        print(f"Scene successfully created: {output_file}")
    except Exception as e:
        print(f"Error saving output file {output_file}: {e}")


if __name__ == "__main__":
    # Example usage
    input_usda_files = [
    "assets/components/cabinet_with_hinged_doors_1.usda",
    "assets/components/cabinet_with_hinged_doors_2.usda",
    "assets/components/drawer_cabinet_4.usda",
    "assets/components/rolling_cabinet_2.usda",
    "assets/components/cabinet_with_hinged_doors_9.usda",
    "assets/components/hinged_door_cabinet_with_bin_1.usda"
]
output_usda_file = "merged_scene.usda"
merge_usda_files(output_usda_file, input_usda_files, spacing=0.1)