from LLM_chain.LLM_chain.main import main
from USD_modules.usd_utils import merge_usda_files, extract_filepaths

def demo (user_input):
    assembly_data_model = main(user_input)

    filepaths = extract_filepaths(assembly_data_model)
    # Group files by component type
    cabinet_usdas = [f"assets/components/{fp}.usda" for fp in filepaths if "cabinet" in fp.lower()]
    top_usdas = [f"assets/components/{fp}.usda" for fp in filepaths if "top" in fp.lower()]
    rear_panel_usdas = [f"assets/components/{fp}.usda" for fp in filepaths if "rear_panel" in fp.lower()]
    spacing = assembly_data_model["metadata"]["spacing"] / (assembly_data_model["metadata"]["number_of_cabinets"] - 1) / 1000


    quantity = 2
    layers = 3
    output_usda_file = "assembly.usda"
    print(assembly_data_model)
    merge_usda_files(output_usda_file, top_usdas[0], cabinet_usdas,rear_panel_usdas[0], quantity, layers, spacing= spacing)