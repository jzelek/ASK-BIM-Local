from SPARQLWrapper import SPARQLWrapper, JSON
from config import SPARQL_ENDPOINT

def run_sparql_query(query):
    """
    Executes a SPARQL query against the configured endpoint.
    """
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    try:
        results = sparql.query().convert()
        return results["results"]["bindings"]
    except Exception as e:
        print(f"Error running SPARQL query: {e}")
        return []

def format_sparql_results(results):
    """
    Formats the SPARQL query results into a readable string.
    """
    formatted_results = []
    for result in results:
        formatted_result = ", ".join([f"{k}: {v['value']}" for k, v in result.items()])
        formatted_results.append(f"({formatted_result})")
    return "\n".join(formatted_results)