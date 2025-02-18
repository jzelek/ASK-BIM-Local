import json
import os
from config import QUERY_CLASSES_WITH_PROPERTIES, QUERY_PROPS_WITH_VALUES, PREFIXES, OPENAI_API_KEY
from sparql_client import run_sparql_query
from utils import simplify_nested_dict_with_values
from process_query import process_user_query
import openai

def build_nested_dict():
    # Run the SPARQL queries to build the nested dictionary
    results_classes_props = run_sparql_query(QUERY_CLASSES_WITH_PROPERTIES)
    results_props_values = run_sparql_query(QUERY_PROPS_WITH_VALUES)
    
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

def get_or_build_kg_data(cache_file="kg_data.json"):
    """
    Checks if the preprocessed KG data exists in a cache file.
    If it exists, load and return it. Otherwise, build the data, save it, and return it.
    """
    if os.path.exists(cache_file):
        print("Loading preprocessed KG data from", cache_file)
        with open(cache_file, "r") as f:
            simplified_nested_dict = json.load(f)
    else:
        print("Preprocessing KG data (this may take a while)...")
        nested_dict = build_nested_dict()
        simplified_nested_dict = simplify_nested_dict_with_values(nested_dict, PREFIXES)
        with open(cache_file, "w") as f:
            json.dump(simplified_nested_dict, f, indent=2)
        print("KG data cached to", cache_file)
    return simplified_nested_dict

def main():
    # Initialize OpenAI
    openai.api_key = OPENAI_API_KEY
    
    # Load (or build once) the preprocessed knowledge graph data
    simplified_nested_dict = get_or_build_kg_data()
    classes = list(simplified_nested_dict.keys())
    
    # Change only the question below to test different queries
    user_question = "Which corridors have doors wider than 900mm?"
    
    # Process the query using the preprocessed data
    answer = process_user_query(user_question, classes, simplified_nested_dict, PREFIXES, openai)
    print("Final Answer:")
    print(answer)

if __name__ == "__main__":
    main()