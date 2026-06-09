import json
import os
import sys
from pathlib import Path
from config import (
    GRAPH_DIAGRAM_DIR,
    KG_CACHE_FILE,
    PREFIXES,
    QUERY_CLASSES_WITH_PROPERTIES,
    QUERY_PROPS_WITH_VALUES,
)
from local_llm_client import LocalLLMClient
from sparql_client import run_sparql_query
from utils import save_kg_diagram, simplify_nested_dict_with_values
from process_query import process_user_query

# Change only the question below to test different queries
user_question = "What is the sum of number of doors and windows in the building?"

def build_nested_dict():
    # Run the SPARQL queries to build the nested dictionary
    results_classes_props = run_sparql_query(QUERY_CLASSES_WITH_PROPERTIES)
    results_props_values = run_sparql_query(QUERY_PROPS_WITH_VALUES)

    if not results_classes_props or not results_props_values:
        raise RuntimeError(
            "GraphDB responded, but the ASK-BIM preprocessing queries returned "
            "no KG classes or properties. Check that the Barcelona knowledge "
            "graph is loaded in GraphDB and that SPARQL_ENDPOINT in config.py "
            "points to the correct repository."
        )
    
    # Create a mapping of property full URIs to example values
    property_to_details = {
        prop['property']['value']: prop['examples']['value'] 
        for prop in results_props_values
    }
    
    nested_dict = {}
    for class_entry in results_classes_props:
        class_uri = class_entry['class']['value']
        properties = class_entry['properties']['value'].split(", ")
        property_details = {
            full_uri: property_to_details.get(full_uri, None)
            for full_uri in property_to_details.keys()
            if full_uri.split("#")[-1] in properties
        }
        nested_dict[class_uri] = property_details
    return nested_dict

def get_or_build_kg_data(cache_file=KG_CACHE_FILE):
    """
    Checks if the preprocessed KG data exists in a cache file.
    If it exists, load and return it. Otherwise, build the data, save it, and return it.
    """
    cache_path = Path(cache_file)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    if cache_path.exists():
        print("Loading preprocessed KG data from", cache_file)
        with cache_path.open("r") as f:
            simplified_nested_dict = json.load(f)
        if not simplified_nested_dict:
            print(cache_file, "is empty. Rebuilding KG data.")
            nested_dict = build_nested_dict()
            simplified_nested_dict = simplify_nested_dict_with_values(nested_dict, PREFIXES)
            with cache_path.open("w") as f:
                json.dump(simplified_nested_dict, f, indent=2)
            print("KG data cached to", cache_file)
            diagram_paths = save_kg_diagram(
                simplified_nested_dict,
                output_dir=GRAPH_DIAGRAM_DIR,
            )
            print("KG diagram saved to", diagram_paths["svg"])
            print("KG Mermaid source saved to", diagram_paths["mermaid"])
    else:
        print("Preprocessing KG data (this may take a while)...")
        nested_dict = build_nested_dict()
        simplified_nested_dict = simplify_nested_dict_with_values(nested_dict, PREFIXES)
        with cache_path.open("w") as f:
            json.dump(simplified_nested_dict, f, indent=2)
        print("KG data cached to", cache_file)
        diagram_paths = save_kg_diagram(
            simplified_nested_dict,
            output_dir=GRAPH_DIAGRAM_DIR,
        )
        print("KG diagram saved to", diagram_paths["svg"])
        print("KG Mermaid source saved to", diagram_paths["mermaid"])
    return simplified_nested_dict

def main():
    # Initialize the local LLM client
    llm_client = LocalLLMClient()
    
    # Load (or build once) the preprocessed knowledge graph data
    simplified_nested_dict = get_or_build_kg_data()
    classes = list(simplified_nested_dict.keys())
    
    # Process the query using the preprocessed data
    answer = process_user_query(
        user_question,
        classes,
        simplified_nested_dict,
        PREFIXES,
        llm_client,
    )
    print(answer)

if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print("\nASK-BIM could not continue:")
        print(error)
        sys.exit(1)
