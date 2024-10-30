from pxr import Usd, UsdGeom, Sdf, Gf, Kind
import os
import csv

def create_usd_from_csv_row(row):
    # Extract data from the row
    name = row['Name']
    file_name = f"{name}.usda"
    file_path = os.path.join("assets", "components", file_name)
    
    # Create a new stage
    stage = Usd.Stage.CreateNew(file_path)
    
    # Create the main xform
    main_xform = UsdGeom.Xform.Define(stage, f"/{name}")
    stage.SetDefaultPrim(main_xform.GetPrim())

    # Assign the 'component' kind
    Usd.ModelAPI(main_xform.GetPrim()).SetKind(Kind.Tokens.component)

    
    # Create the geometry
    geometry = UsdGeom.Cube.Define(stage, f"/{name}/geometry")
    
    # Set dimensions
    width, depth, height = int(row['Width']) / 1000, int(row['Depth']) / 1000, int(row['Height']) / 1000
    
    # Set the scale
    geometry.AddScaleOp().Set(Gf.Vec3f(width, depth, height))
    
    # Set the extent based on the dimensions
    half_width, half_depth, half_height = width/2, depth/2, height/2
    min_extent = Gf.Vec3f(-half_width, -half_depth, -half_height)  # Minimum corner
    max_extent = Gf.Vec3f(half_width, half_depth, half_height)     # Maximum corner
    geometry.GetExtentAttr().Set([min_extent, max_extent])
    
    # Set the color (object color)
    color_map = {
        'grey': (0.5, 0.5, 0.5),
        'black': (0.0, 0.0, 0.0),
        'blue': (0.0, 0.0, 1.0),
        'yellow': (1.0, 1.0, 0.0),
        'white': (1.0, 1.0, 1.0)
    }
    object_color = color_map.get(row['Color (Object)'].lower(), (0.5, 0.5, 0.5))
    geometry.GetDisplayColorAttr().Set([Gf.Vec3f(*object_color)])
    
    # Add custom metadata attributes
    prim = geometry.GetPrim()
    prim.SetCustomDataByKey('type', row['Type'])
    prim.SetCustomDataByKey('function', row['Function'])
    prim.SetCustomDataByKey('width', int(row['Width']))
    prim.SetCustomDataByKey('depth', int(row['Depth']))
    prim.SetCustomDataByKey('height', int(row['Height']))
    prim.SetCustomDataByKey('color_attribute', row['Color (Attribute)'])
    prim.SetCustomDataByKey('material', row['Material'])
    
    # Save the stage
    stage.GetRootLayer().Save()
    
    print(f"USD file created: {file_path}")

def process_csv_file(file_path):
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            create_usd_from_csv_row(row)

# Usage
process_csv_file('Lista Products - Enumerated.csv')




