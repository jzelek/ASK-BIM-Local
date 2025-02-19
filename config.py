import os

# SPARQL endpoint and queries
SPARQL_ENDPOINT = "http://127.0.0.1:7200/repositories/Barcelona2"

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

# OpenAI API key – ideally set this via an environment variable for security
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
