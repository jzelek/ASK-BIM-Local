def simplify_uri(uri, prefixes):
    """
    Replaces a full URI with its prefix notation.
    """
    for prefix, full_uri in prefixes.items():
        if uri.startswith(full_uri):
            return uri.replace(full_uri, f"{prefix}:")
    return uri

def simplify_nested_dict_with_values(nested_dict, prefixes):
    """
    Applies URI simplification to all keys (and any URI value) in a nested dictionary.
    """
    simplified_dict = {}
    for class_uri, properties in nested_dict.items():
        simplified_class = simplify_uri(class_uri, prefixes)
        simplified_properties = {
            simplify_uri(prop, prefixes): (
                simplify_uri(example, prefixes) if isinstance(example, str) and example.startswith("http") else example
            )
            for prop, example in properties.items()
        }
        simplified_dict[simplified_class] = simplified_properties
    return simplified_dict

def format_query(raw_query):
    """
    Converts a SPARQL query wrapped with triple backticks into a plain multi-line string.
    """
    cleaned_query = raw_query.strip()
    if cleaned_query.startswith("```sparql"):
        cleaned_query = cleaned_query[len("```sparql"):].strip()
    if cleaned_query.startswith("```"):
        cleaned_query = cleaned_query[len("```"):].strip()
    if cleaned_query.endswith("```"):
        cleaned_query = cleaned_query[:-3].strip()
    
    return cleaned_query