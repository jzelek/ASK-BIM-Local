from SPARQLWrapper import SPARQLWrapper, JSON
from pathlib import Path
from rdflib import Graph

from config import LOCAL_RDF_FILE, SPARQL_ENDPOINT, USE_LOCAL_RDF_FILE


_LOCAL_GRAPH = None


def _get_local_graph():
    global _LOCAL_GRAPH
    if _LOCAL_GRAPH is None:
        rdf_path = Path(__file__).resolve().parent / LOCAL_RDF_FILE
        if not rdf_path.exists():
            raise RuntimeError(
                "The local RDF file was not found. Check LOCAL_RDF_FILE in "
                f"config.py. Expected path: {rdf_path}"
            )

        graph = Graph()
        graph.parse(rdf_path)
        _LOCAL_GRAPH = graph
    return _LOCAL_GRAPH


def _rdflib_query_to_bindings(query_results):
    bindings = []
    for row in query_results:
        binding = {}
        for variable, value in row.asdict().items():
            binding[str(variable)] = {"value": str(value)}
        bindings.append(binding)
    return bindings

def run_sparql_query(query):
    """
    Executes a SPARQL query against the local RDF file or configured endpoint.
    """
    if USE_LOCAL_RDF_FILE:
        try:
            return _rdflib_query_to_bindings(_get_local_graph().query(query))
        except Exception as e:
            raise RuntimeError(
                "Could not run the SPARQL query against the local RDF file. "
                f"Check LOCAL_RDF_FILE in config.py. Original error: {e}"
            ) from e

    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    try:
        results = sparql.query().convert()
        return results["results"]["bindings"]
    except Exception as e:
        raise RuntimeError(
            "Could not run the SPARQL query. Make sure GraphDB is running and "
            f"the endpoint in config.py is reachable: {SPARQL_ENDPOINT}. "
            f"Original error: {e}"
        ) from e

def format_sparql_results(results):
    """
    Formats the SPARQL query results into a readable string.
    """
    formatted_results = []
    for result in results:
        formatted_result = ", ".join([f"{k}: {v['value']}" for k, v in result.items()])
        formatted_results.append(f"({formatted_result})")
    return "\n".join(formatted_results)
