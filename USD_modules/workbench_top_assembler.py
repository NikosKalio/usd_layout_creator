"""
USD Assembly Script for Workbench Components

This script creates a USD (Universal Scene Description) assembly for a workbench top model.
It provides functionality to:
- Create a new USD stage for the workbench assembly
- Define a root transform node for the entire assembly
- Load individual workbench components and apply specific transformations
- Reference external USD files for each component
- Apply translation, rotation, and scale transformations to each component

The script uses a components list where each component's properties (position, rotation, scale)
can be defined for assembly.
"""

from pxr import Usd, UsdGeom, Sdf, Gf

# Create a new USD stage
stage = Usd.Stage.CreateNew('assets/cleaned_workbench_assembly.usda')

# Define a root Xform for the assembly
rootXform = UsdGeom.Xform.Define(stage, '/WorkbenchAssembly')

# Function to load and apply transformations
def add_component_to_stage(stage, prim_path, reference_path, position, rotation, scale):
    prim = UsdGeom.Xform.Define(stage, prim_path)
    
    # Apply transformations separately
    xformOp = prim.AddTransformOp()
    xformOp.Set(Gf.Matrix4d().SetTranslate(position))

    # Apply rotation
    rotationOp = prim.AddRotateXYZOp()
    rotationOp.Set(rotation)  # Now expects a Gf.Vec3d for rotation

    # Apply scale
    scaleOp = prim.AddScaleOp()
    scaleOp.Set(scale)
    
    # Reference the asset
    prim.GetPrim().GetReferences().AddReference(reference_path)

# Add components to the USD file with proper transformations
# Replace with correct paths and transformation data

# Example data (replace these with actual data for each component)
components = [
    {
        "name": "workbench_top",
        "asset_path": "components/workbench_top_1.usda",
        "translation": Gf.Vec3d(0, 0.850, 0),
        "rotation": Gf.Vec3d(-90, 0, 0),  # Rotate -90 degrees around X axis
        "scale": Gf.Vec3d(1.5, 0.725, 1.0)
    }
    # Add more components as needed
    
    
]

for component in components:
    add_component_to_stage(
        stage,
        '/WorkbenchAssembly',
        component['asset_path'],
        component['translation'],
        component['rotation'],
        component['scale']
    )

# Save the stage
stage.GetRootLayer().Save()
