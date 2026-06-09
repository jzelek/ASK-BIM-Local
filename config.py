import os
from pathlib import Path

# SPARQL endpoint and queries
SPARQL_ENDPOINT = "http://127.0.0.1:7200/repositories/Barcelona2"

IFC_MODEL_DIR = Path(os.getenv("IFC_MODEL_DIR", "IFC-to-LBD Conversion/IFC model"))
_detected_ifc_files = sorted(IFC_MODEL_DIR.glob("*.ifc"))
_detected_ifc_file = _detected_ifc_files[0] if _detected_ifc_files else None
LOCAL_IFC_FILE = os.getenv(
    "LOCAL_IFC_FILE",
    str(_detected_ifc_file) if _detected_ifc_file else "",
)

# By default, ASK-BIM queries the converted local RDF/Turtle file in this repo.
# Set USE_LOCAL_RDF_FILE=false to query the GraphDB endpoint instead.
USE_LOCAL_RDF_FILE = os.getenv("USE_LOCAL_RDF_FILE", "true").lower() == "true"
LOCAL_RDF_FILE = os.getenv(
    "LOCAL_RDF_FILE",
    "IFC-to-LBD Conversion/LBD Model/model_output_geometry.ttl",
)

# Generated files for the detected IFC graph are kept together here.
# Delete this folder when switching to a different converted IFC graph.
_generated_stem = Path(LOCAL_IFC_FILE).stem if LOCAL_IFC_FILE else Path(LOCAL_RDF_FILE).stem
GENERATED_OUTPUT_DIR = os.getenv(
    "GENERATED_OUTPUT_DIR",
    str(Path("generated_ifc_data") / _generated_stem),
)
KG_CACHE_FILE = os.getenv(
    "KG_CACHE_FILE",
    str(Path(GENERATED_OUTPUT_DIR) / "kg_data.json"),
)
GRAPH_DIAGRAM_DIR = os.getenv(
    "GRAPH_DIAGRAM_DIR",
    str(Path(GENERATED_OUTPUT_DIR) / "graph_diagrams"),
)

QUERY_CLASSES_WITH_PROPERTIES = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?class (GROUP_CONCAT(DISTINCT (STRAFTER(STR(?property), "#")); separator=", ") AS ?properties)
WHERE {
  ?s rdf:type ?class .
  ?s ?property ?o .
}
GROUP BY ?class
ORDER BY ?class
"""

QUERY_PROPS_WITH_VALUES = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?property (SAMPLE(?example) AS ?examples)
WHERE {
  ?s ?property ?example .
}
GROUP BY ?property
ORDER BY ?property
"""

# Prefixes for URI simplification
PREFIXES = {
    "IFC4-PSD": "https://www.linkedbuildingdata.net/IFC4-PSD#",
    "beo": "https://pi.pauwel.be/voc/buildingelement#",
    "bot": "https://w3id.org/bot#",
    "fog": "https://w3id.org/fog#",
    "furn": "http://pi.pauwel.be/voc/furniture#",
    "geo": "https://www.opengis.net/ont/geosparql#",
    "ifc": "https://standards.buildingsmart.org/IFC/DEV/IFC2x3/TC1/OWL#",
    "inst": "https://example.domain.de/",
    "lbd": "https://linkedbuildingdata.org/LBD#",
    "mep": "http://pi.pauwel.be/voc/distributionelement#",
    "omg": "https://w3id.org/omg#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "props": "http://lbd.arch.rwth-aachen.de/props#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "smls": "https://w3id.org/def/smls-owl#",
    "unit": "http://qudt.org/vocab/unit/",
    "xsd": "https://www.w3.org/2001/XMLSchema#"
}

# Local LLM settings.
#
# By default the app uses Ollama's native local API so thinking models can be
# run with thinking disabled. Set LOCAL_LLM_API_KIND=openai_compatible for
# LM Studio, vLLM, llama.cpp server, or other /v1/chat/completions servers.
LOCAL_LLM_API_KIND = os.getenv("LOCAL_LLM_API_KIND", "ollama")
LOCAL_LLM_BASE_URL = os.getenv("LOCAL_LLM_BASE_URL", "http://127.0.0.1:11434")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "qwen3.5:0.8b")
LOCAL_LLM_API_KEY = os.getenv("LOCAL_LLM_API_KEY")
LOCAL_LLM_TIMEOUT_SECONDS = int(os.getenv("LOCAL_LLM_TIMEOUT_SECONDS", "120"))
LOCAL_LLM_TEMPERATURE = float(os.getenv("LOCAL_LLM_TEMPERATURE", "0"))
LOCAL_LLM_MAX_TOKENS = int(os.getenv("LOCAL_LLM_MAX_TOKENS", "512"))
LOCAL_LLM_THINK = os.getenv("LOCAL_LLM_THINK", "false").lower() == "true"
