from pxr import Usd, UsdGeom, Sdf, Gf
#from utils.helperfunctions import create_new_stage

file_name = "drawer_cabinet2.usda"
file_path = "assets/components/" + file_name
stage = Usd.Stage.CreateNew(file_path)

# Create the drawer cabinet
cabinet = UsdGeom.Xform.Define(stage, "/drawer_cabinet_1")
stage.SetDefaultPrim(cabinet.GetPrim())

# Create the box for the cabinet
cabinet = UsdGeom.Cube.Define(stage, "/drawer_cabinet_1/geometry")

# Set the box dimensions
width, depth, height = 411 / 1000, 572 / 1000, 800 / 1000  # Convert to meters
half_width, half_depth, half_height = width/2, depth/2, height/2

# Set the extent attribute to define the box dimensions
# Set the extent for a rectangular box
min_extent = Gf.Vec3f(-half_width, -half_depth, -half_height)  # Minimum corner
max_extent = Gf.Vec3f(half_width, half_depth, half_height)     # Maximum corner
# Set the extent attribute for the cube
cabinet.GetExtentAttr().Set([min_extent, max_extent])

# Set the color (grey)
color_attr = cabinet.GetDisplayColorAttr()
color_attr.Set([(0.5, 0.5, 0.5)])  # Grey color


# Step 1: Add custom metadata attributes (semantic meaning)
cabinet.GetPrim().SetCustomDataByKey('type', 'Drawer Cabinet')
cabinet.GetPrim().SetCustomDataByKey('function', 'Stationary cabinet used for storage')
cabinet.GetPrim().SetCustomDataByKey('width', 411)  # mm
cabinet.GetPrim().SetCustomDataByKey('depth', 572)  # mm
cabinet.GetPrim().SetCustomDataByKey('height', 800)  # mm
cabinet.GetPrim().SetCustomDataByKey('color_attribute', 'Null')  # Semantic color
cabinet.GetPrim().SetCustomDataByKey('material', 'Metal')

# Step 2: Set the object color (visual appearance)
cabinet.GetDisplayColorAttr().Set([Gf.Vec3f(1.0, 0, 0)])  # Grey color for the cuboid appearance





# Save the stage
stage.GetRootLayer().Save()

print(f"Drawer cabinet USD file created: {file_path}")
