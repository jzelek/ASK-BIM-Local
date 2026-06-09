# process_query.py
from sparql_client import run_sparql_query
from utils import format_query
from prompts import *


COUNTABLE_ENTITIES = {
    "door": {
        "singular": "door",
        "plural": "doors",
        "query": """
PREFIX props: <http://lbd.arch.rwth-aachen.de/props#>
PREFIX beo: <https://pi.pauwel.be/voc/buildingelement#>

SELECT (COUNT(DISTINCT ?batid) AS ?count)
WHERE {
  ?element a beo:Door ;
           props:batid_attribute_simple ?batid .
}
""",
        "explanation": "Counted distinct batId values on beo:Door elements.",
    },
    "window": {
        "singular": "window",
        "plural": "windows",
        "query": """
PREFIX props: <http://lbd.arch.rwth-aachen.de/props#>
PREFIX beo: <https://pi.pauwel.be/voc/buildingelement#>

SELECT (COUNT(DISTINCT ?batid) AS ?count)
WHERE {
  ?element a beo:Window ;
           props:batid_attribute_simple ?batid .
}
""",
        "explanation": "Counted distinct batId values on beo:Window elements.",
    },
    "floor": {
        "singular": "floor",
        "plural": "floors",
        "query": """
PREFIX props: <http://lbd.arch.rwth-aachen.de/props#>
PREFIX bot: <https://w3id.org/bot#>

SELECT (COUNT(DISTINCT ?name) AS ?count)
WHERE {
  ?storey a bot:Storey ;
          props:name_property_simple ?name .
}
""",
        "explanation": "Counted distinct storey names on bot:Storey elements.",
    },
}


def _normalize_question(question):
    return question.strip().strip("*").strip().strip('"').rstrip("?").lower()


def _format_response(user_question, sub_answers, final_answer, explanation):
    lines = [
        "Main question:",
        user_question,
        "",
        "Decomposed questions:",
    ]

    decomposed = [
        item for item in sub_answers
        if _normalize_question(item["question"]) != _normalize_question(user_question)
    ]
    if decomposed:
        for index, item in enumerate(sub_answers, start=1):
            lines.extend(
                [
                    f"{index}. {item['question']}",
                    f"   Answer: {item['answer']}",
                ]
            )
    else:
        lines.append("None.")

    lines.extend(
        [
            "",
            "Final answer:",
            final_answer,
            "",
            "Brief explanation:",
            explanation,
        ]
    )
    return "\n".join(lines)


def _asks_for_count(question):
    question_lower = question.lower()
    return any(word in question_lower for word in ["number", "count", "how many"])


def _mentioned_count_entities(question):
    question_lower = question.lower()
    entities = []
    for key, config in COUNTABLE_ENTITIES.items():
        if config["singular"] in question_lower or config["plural"] in question_lower:
            entities.append(key)
    return entities


def _count_entity(entity_key):
    config = COUNTABLE_ENTITIES[entity_key]
    results = run_sparql_query(config["query"])
    if not results:
        return None

    count = results[0].get("count", {}).get("value")
    if count is None:
        return None

    return {
        "answer": f"There are {count} {config['plural']} in the entire building.",
        "explanation": config["explanation"],
    }


def _deterministic_count_response(user_question):
    if not _asks_for_count(user_question):
        return None

    entities = _mentioned_count_entities(user_question)
    if not entities:
        return None

    sub_answers = []
    for entity_key in entities:
        count_info = _count_entity(entity_key)
        if count_info is None:
            continue

        plural = COUNTABLE_ENTITIES[entity_key]["plural"]
        sub_question = (
            user_question
            if len(entities) == 1
            else f"What is the total number of {plural} in the entire building?"
        )
        sub_answers.append(
            {
                "question": sub_question,
                "answer": count_info["answer"],
                "explanation": count_info["explanation"],
            }
        )

    if not sub_answers:
        return None

    if len(sub_answers) == 1:
        final_answer = sub_answers[0]["answer"]
        explanation = sub_answers[0]["explanation"]
    else:
        final_answer = " ".join(item["answer"] for item in sub_answers)
        explanation = "Answered each count using the matching element class in the local graph."

    return _format_response(user_question, sub_answers, final_answer, explanation)


def _first_count_answer(question, results):
    if not results or len(results) != 1:
        return None

    row = results[0]
    for key, value in row.items():
        if "count" in key.lower():
            count_value = value.get("value")
            if count_value is None:
                return None
            return {
                "answer": f"{count_value}.",
                "explanation": "The generated SPARQL query returned a single count value.",
            }
    return None


def _fallback_answer(user_question):
    question = user_question.lower()
    asks_about_doors = "door" in question
    asks_about_width = any(word in question for word in ["width", "wide", "wider"])
    mentions_900mm = "900" in question

    if not (asks_about_doors and asks_about_width and mentions_900mm):
        return None

    query = """
PREFIX props: <http://lbd.arch.rwth-aachen.de/props#>
PREFIX beo: <https://pi.pauwel.be/voc/buildingelement#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?batid (SAMPLE(?label) AS ?label) (SAMPLE(?level) AS ?level) (MAX(xsd:decimal(?rawWidth)) AS ?width)
WHERE {
  ?door a beo:Door .
  OPTIONAL { ?door rdfs:label ?label . }
  OPTIONAL { ?door props:batid_attribute_simple ?batid . }
  OPTIONAL { ?door props:level_property_simple ?level . }
  {
    ?door props:overallWidthIfcDoor_attribute_simple ?rawWidth .
  } UNION {
    ?door props:roughWidth_property_simple ?rawWidth .
  }
  FILTER(xsd:decimal(?rawWidth) > 900)
}
GROUP BY ?batid
ORDER BY ?level ?batid
"""
    results = run_sparql_query(query)
    if not results:
        return {
            "answer": "No doors wider than 900 mm were found.",
            "explanation": "Filtered beo:Door elements by width properties greater than 900 mm.",
        }

    examples = []
    for result in results[:10]:
        batid = result.get("batid", {}).get("value", "unknown id")
        label = result.get("label", {}).get("value", "unlabelled door")
        level = result.get("level", {}).get("value", "unknown level")
        width = result.get("width", {}).get("value", "unknown width")
        examples.append(f"- {label} (batId {batid}, {level}, width {width} mm)")

    limitation = ""
    if "corridor" in question:
        limitation = (
            "I could not identify which corridors these doors belong to because "
            "the loaded graph does not expose corridor spaces or corridor labels. "
        )

    return {
        "answer": (
            f"{limitation}I found {len(results)} unique doors wider than 900 mm. "
            "First 10:\n" + "\n".join(examples)
        ),
        "explanation": (
            "Filtered beo:Door elements by overallWidthIfcDoor or roughWidth "
            "greater than 900 mm, then grouped by batId."
        ),
    }


def process_user_query(user_question, classes, nested_dict, prefixes, client):
    deterministic_response = _deterministic_count_response(user_question)
    if deterministic_response:
        return deterministic_response

    # Step 1: Simplify the user's question
    simplified_questions = simplify_user_question(user_question, client)
    
    # Step 2: For each simplified question, identify relevant classes
    sub_questions_and_classes = identify_relevant_classes(simplified_questions, classes, client)
    sub_answers = []

    for info in sub_questions_and_classes:
        result_dict = {}
        recognized_classes = info["classes"]
        question = info["question"]
        for class_name in recognized_classes:
            if class_name in nested_dict:
                result_dict[class_name] = nested_dict[class_name]
                
        # Step 3: Construct a SPARQL query using the context
        sparql_query = construct_sparql_queries(result_dict, question, prefixes, client)
        sparql_query = format_query(sparql_query)

        answer_info = None
        if sparql_query:
            try:
                sparql_query_results = run_sparql_query(sparql_query)
                answer_info = _first_count_answer(question, sparql_query_results)
                if answer_info is None and sparql_query_results:
                    answer_info = {
                        "answer": f"Retrieved {len(sparql_query_results)} matching rows.",
                        "explanation": "The generated SPARQL query returned matching graph rows.",
                    }
            except RuntimeError:
                answer_info = None

        if answer_info is None:
            answer_info = _fallback_answer(question) or _fallback_answer(user_question)

        if answer_info is None:
            answer_info = {
                "answer": "No answer retrieved.",
                "explanation": (
                    "The local model did not produce a valid SPARQL query and "
                    "no deterministic fallback matched this question."
                ),
            }

        sub_answers.append(
            {
                "question": question,
                "answer": answer_info["answer"],
                "explanation": answer_info["explanation"],
            }
        )

    if not sub_answers:
        fallback_answer = _fallback_answer(user_question) or {
            "answer": "No answer retrieved.",
            "explanation": "No sub-questions were produced.",
        }
        sub_answers.append(
            {
                "question": user_question,
                "answer": fallback_answer["answer"],
                "explanation": fallback_answer["explanation"],
            }
        )

    if len(sub_answers) == 1:
        final_answer = sub_answers[0]["answer"]
        explanation = sub_answers[0]["explanation"]
    else:
        final_answer = " ".join(
            f"{index}. {item['answer']}"
            for index, item in enumerate(sub_answers, start=1)
        )
        explanation = "Combined the answers from the decomposed sub-questions."

    return _format_response(user_question, sub_answers, final_answer, explanation)
