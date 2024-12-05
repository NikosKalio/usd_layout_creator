from pxr import Usd, UsdGeom, Sdf, Gf

def get_child_prim(parent_prim, child_name) -> Usd.Prim:
    child_prim: Usd.Prim = parent_prim.GetChild(child_name)
    return child_prim

def get_first_child_mesh(parent_prim: Usd.Prim) -> Usd.Prim:
    for child_prim in parent_prim.GetChildren():
        if child_prim.IsA(UsdGeom.Mesh):
            return child_prim



def print_all_children_names(parent_prim: Usd.Prim):
    children_names = []
    for child_prim in parent_prim.GetAllChildren():
        children_names.append(child_prim.GetName())


def compute_bbox(prim: Usd.Prim) -> Gf.Range3d:
    """
    Compute Bounding Box using ComputeWorldBound at UsdGeom.Imageable
    See https://openusd.org/release/api/class_usd_geom_imageable.html

    Args:
        prim: A prim to compute the bounding box.
    Returns: 
        A range (i.e. bounding box), see more at: https://openusd.org/release/api/class_gf_range3d.html
    """
    imageable = UsdGeom.Imageable(prim)
    time = Usd.TimeCode.Default()
    bound = imageable.ComputeWorldBound(time, UsdGeom.Tokens.default_)
    bound_range= bound.ComputeAlignedBox()
    return bound_range

def get_prim_dims(prim:Usd.Prim)-> tuple[float, float, float]:      
    bbox = compute_bbox(xform_prims[1])
    size = bbox.GetSize()  # Returns a Gf.Vec3d with the dimensions
    length = size[0]   # X dimension
    height = size[1]  # Y dimension
    depth = size[2]  # Z dimension
    return length, height, depth


input_usds = [
    "../NIKOS/Kenny's_Module_1.usd", 
    "../NIKOS/Kenny's_Module_2.usd", 
    "../NIKOS/Kenny's_Module_3.usd",
    "../NIKOS/Kenny's_Module_4.usd", 
    "../NIKOS/Kenny's_Module_5.usd", 
    "../NIKOS/Kenny's_Module_6.usd", 
    "../NIKOS/Kenny's_Module_7.usd", 
    "../NIKOS/Kenny's_Module_8.usd",
    "../NIKOS/Kenny's_Module_9.usd", 
    "../NIKOS/Kenny's_Module_10.usd", 
    "../NIKOS/Kenny's_Module_11.usd",
    "../NIKOS/Kenny's_Module_12.usd", 
    "../NIKOS/Kenny's_Module_13.usd"]

for input_usd in input_usds:
    stage: Usd.Stage = Usd.Stage.Open(input_usd)
    xform_prims = []

    for prim in stage.Traverse():
        if prim.GetTypeName() == "Xform":
            xform_prims.append(prim)
            print(prim.GetName())


    length, height, depth = get_prim_dims(xform_prims[1])
    print(f"Length (X): {length}")
    print(f"Height (Y): {height}")
    print(f"Depth (Z): {depth}")



