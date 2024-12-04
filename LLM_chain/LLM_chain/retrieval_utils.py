import json
import os
from pxr import Usd, UsdGeom

def calculate_rear_panels_constrained(L_cabinet):
    # Calculate maximum a and b
    a_max = (L_cabinet + 749) // 750
    b_max = (L_cabinet + 999) // 1000

    # Generate all possible configurations from 0 to max
    candidates = [
        {"a": a, "b": b, "spacing": a * 750 + b * 1000 - L_cabinet}
        for a in range(a_max + 1)
        for b in range(b_max + 1)
        if a * 750 + b * 1000 >= L_cabinet
    ]

    # Select the configuration with the smallest spacing
    if not candidates:
        return None

    best_config = min(candidates, key=lambda c: c["spacing"])
    return best_config

# Example
#L_cabinet = 2500
#result = calculate_rear_panels_constrained(L_cabinet)
#print("Result:", result)


#print(json.dumps(load_search_json('searches/search_20241202_121421.json'), indent=2))


def width_cabinet(input_files):
    length_of_cabinets= []
    for index, file_path in enumerate(input_files):
            if not os.path.exists(file_path):
                print(f"Warning: Input file {file_path} does not exist. Skipping.")
                continue

            model_name = os.path.splitext(os.path.basename(file_path))[0]
            prim_path = f"/Model_{index}"

            # Compute translation based on bounding box size
            try:
                referenced_stage = Usd.Stage.Open(file_path)
                model_geometry_prim = referenced_stage.GetPrimAtPath(f'/{model_name}/geometry')

                if model_geometry_prim:
                    boundable = UsdGeom.Boundable(model_geometry_prim)
                    extent = boundable.GetExtentAttr().Get()
                    model_width = extent[1][0] - extent[0][0]  # Bounding box width
                    length_of_cabinets.append(model_width)
                    

                else:
                    print(f"Warning: Could not find geometry for {file_path}.Try again.")
                    

            except Exception as e:
                print(f"Error computing bounds for {file_path}: {e}")
                continue

    return length_of_cabinets

input_usda_files = [
    r"../../assets/components/cabinet_with_hinged_doors_1.usda",
    r"../../assets/components/cabinet_with_hinged_doors_2.usda",
    r"../../assets/components/drawer_cabinet_4.usda",
    r"../../assets/components/rolling_cabinet_2.usda",
    r"../../assets/components/cabinet_with_hinged_doors_9.usda",
    r"../../assets/components/hinged_door_cabinet_with_bin_1.usda"
]



#print(width_cabinet(input_usda_files))
#total_width = sum(width_cabinet(input_usda_files))
#print(total_width*1000)


def construct_file_path(filename, directory="../../assets/components"):
    return os.path.join(directory, filename +".usda")

# Example usage:
# search_data = load_search_json('searches/search_20241202_121421.json')
# total_width = 2500  # Example width in mm
# result = number_of_panels(search_data, total_width)
# print(json.dumps(result, indent=2))

file_path = construct_file_path("cabinet_with_hinged_doors_1")
print(file_path)
