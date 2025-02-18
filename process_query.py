# process_query.py
from sparql_client import run_sparql_query
from utils import format_query
from prompts import *

def process_user_query(user_question, classes, nested_dict, prefixes, client):
    # Step 1: Simplify the user's question
    simplified_questions = simplify_user_question(user_question, client)
    
    sparql_queries = []
    
    # Step 2: For each simplified question, identify relevant classes
    sub_questions_and_classes = identify_relevant_classes(simplified_questions, classes, client)
    print("Sub-Questions and classes identified:", sub_questions_and_classes)
    
    result_dict = {}
    for info in sub_questions_and_classes:
        recognized_classes = info["classes"]
        question = info["question"]
        for class_name in recognized_classes:
            if class_name in nested_dict:
                result_dict[class_name] = nested_dict[class_name]
                
        # Step 3: Construct a SPARQL query using the context
        sparql_query = construct_sparql_queries(result_dict, question, prefixes, client)
        sparql_query = format_query(sparql_query)
        if sparql_query:
            sparql_queries.append(sparql_query)
    
    # Step 4: Execute each SPARQL query and collect results
    query_and_results = {}
    for query in sparql_queries:
        sparql_query_results = run_sparql_query(query)
        query_and_results[query] = sparql_query_results
    
    # Step 5: Generate an answer based on the collected results
    if query_and_results:
        final_answer = answer_based_on_query_results(user_question, query_and_results, client)
        return final_answer
    else:
        return "No valid data retrieved from the SPARQL queries."