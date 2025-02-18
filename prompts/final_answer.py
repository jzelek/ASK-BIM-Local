# VERSION 3
# Function to execute SPARQL queries and generate an answer with LLM assistance
def answer_based_on_query_results(user_question, sparql_query_results, client):
    
    #print("Sparql Query Results i am passing as context to answer the Question: " + str(sparql_query_results))

    prompt = f"""
        Your task is to answer user questions about buildings using data retrieved from a knowledge graph via SPARQL queries.

        Here is the user's question:  
        
        <user_question>  
        {user_question}  
        </user_question>  
        
        Below is the dictionary containing each query along with its results:  
        
        <sparql_query_results>  
        {sparql_query_results}  
        </sparql_query_results>  
        
        ### **Instructions**:
        
        - The `sparql_query_results` is a dictionary where each key is a SPARQL query and the value is the corresponding result from the knowledge graph.  
        - When analyzing the results, use both the queries and the returned data to understand the elements being retrieved and their relationships.  
        
        ### **Simplified Steps**:
        
        1) **Understand the User's Question and Query Results:**  
           - Interpret the user's intent and the structure of the returned data.  
           - Assume the results are relevant and comprehensive.  
           - If an expected attribute is missing, assume the list is already filtered by that criterion or an equivalent.
        
        2) **Interpret and Define the Returned Elements:**  
           - Identify each element type based on the IFC schema.  
           - Recognize associations such as spatial containment, composition, connectivity, and property references (e.g., material assignments).  
           - Treat entries with the same `props:batid_attribute_simple` as referring to the same real-world object to avoid duplication.  
        
        3) **Answer the Question by Reasoning or Displaying the Data:**  
           - If the question requests a list or value, use the provided data directly if already filtered and complete.  
           - Perform additional filtering or calculations only if necessary to derive the final answer.
        
        4) **Check Completeness and Accuracy:**  
           - Verify if the results cover all aspects required to answer the question.  
           - If the data is incomplete or ambiguous, mention any limitations and provide partial answers if possible.
        
        5) **Formulate the Final Answer:**  
           - Provide a concise answer that fully addresses the user's question.  
           - Ensure the format matches the request (e.g., listing elements if a list is requested).
        
        ### **Important Considerations:**  
        - Do not mention the SPARQL queries or structure of the data unless explicitly requested by the user.  
        - Use your IFC schema knowledge to interpret relationships and attributes in the data.  
        - Assume that the queries provide relevant entities and attributes needed to answer the question.
        
        ### **Output Format:**  
        
        <data_interpretation>  
        User's question: [Restate the user's question]  
        Key data points from the SPARQL results:  
        1. [Data point 1] - Definition: [IFC schema definition] - Relevance to question: [Explanation]  
        2. [Data point 2] - Definition: [IFC schema definition] - Relevance to question: [Explanation]  
        ...  
        Calculations: [Any relevant calculations]  
        Data assessment: [Comments on completeness/reliability]  
        Potential limitations: [List any ambiguities or limitations in the data]  
        </data_interpretation>  
        
        <answer>  
        [Concise answer to the user's question based on the analysis]  
        </answer>  
        
        ### **Example:**  
        **User's Question:** "List all doors on the first floor."  
        
        **SPARQL Results:** A list of doors with their attributes (including `label` and `batId`, but missing `level`).  
        
        **Answer Logic:**  
        - If the `level` attribute is missing, assume the list is pre-filtered by the level and display all elements.  
        - If the `level` is present but unfiltered, apply filtering in the reasoning step to list only first-floor doors.  
        - Always check for duplicate entries by comparing `props:batid_attribute_simple` and consider them as the same object if IDs match.  

    """
        
    # Ask the LLM to generate the final answer using the query results
    promptOLD = f"""
        Your task is to answer user questions about buildings using data retrieved from a knowledge graph via SPARQL queries.

        Here is the user's question:
        
        <user_question>
        {user_question}
        </user_question>
        
        Below is the dictionary containing each query along with its results: :
        
        <sparql_query_results>
        {sparql_query_results}
        </sparql_query_results>
        
        Your goal is to provide a concise and complete answer to the user's question based on the SPARQL query results. Follow these steps:
        
        Simplified Instructions:
        - Understand the User's Question and the SPARQL Results:
        
        Interpret the user's intent and the structure of the returned data.
        - Assume the results are a comprehensive and relevant set of data designed to answer the question.
        - If the results do not explicitly include an attribute, assume the list is already filtered by that criterion or an equivalent.
        
        Interpret and Define the Returned Elements:
        
        - Identify the type of each element based on the IFC schema.
        - Recognize relationships and associations (e.g., spatial containment, composition, connectivity, and references like material assignments).
        - Handle cases where multiple entries refer to the same real-world object by using unique IDs or labels to avoid duplication.
        
        Answer the Question by Reasoning or Displaying the Data:
        
        - If the question asks for a list or a specific value, use the provided data directly if it is already filtered and complete.
        - If additional steps (like filtering or calculations) are needed, use the provided attributes to reason and derive the final answer.
        
        Check Completeness and Accuracy:
        
        - Verify if the results cover all necessary aspects to answer the question.
        - If the data is incomplete or ambiguous, state any limitations and provide partial answers if possible.
        
        Formulate the Final Answer:
        
        - Provide a response that fully addresses the user's question.
        - Ensure the response matches the expected format (e.g., listing elements if a list is requested).
        
        Important Considerations:
        
        - Do not mention the SPARQL query results or the structure of the data unless explicitly requested by the user.
        - If the results are incomplete, explain the limitations.
        - Use your IFC schema knowledge to reason through the relationships and attributes in the data.
        - Assume the query results provide the relevant entities and attributes needed to answer the question.
        - The same ID for an object in the results indicates the same real-world object; therefore, you should consider multiple lines with the same ID as duplicates.
        
        Output Format:
        
        <data_interpretation>
        User's question: [Restate the user's question]
        Key data points from the SPARQL results :
        
        [Data point 1] - Definition: [IFC schema definition] - Relevance to question: [Explanation]
        [Data point 2] - Definition: [IFC schema definition] - Relevance to question: [Explanation]
        ...
        Calculations: [Any relevant calculations]
        Data assessment: [Comments on completeness/reliability]
        Potential limitations: [List any ambiguities or limitations in the data]
        </data_interpretation>
        <answer> [Concise answer to the user's question based on the analysis] </answer>
        
        Example:
        User's Question: "List all doors on the first floor."
        
        SPARQL Results: A list of doors with their attributes (including label, batId, but missing level).
        
        Answer Logic:
        - If the level attribute is not present, assume the list is already filtered by the level and display all the elements. 
        - If the level is present but unfiltered, apply the filtering in the reasoning step to list only the first-floor doors.
        - Always check if an entity in the results as the same Id, and if yes consider them as the same object.
        """

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are assisting in answering user queries based on data retrieved from a building knowledge graph."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o-mini",
    )

    final_answer = chat_completion.choices[0].message.content.strip()
    print(f"\nFinal Answer: {final_answer}")
    return final_answer
    

# Helper function to format SPARQL query results into a readable string
def format_sparql_results(results):
    formatted_results = []
    for result in results:
        formatted_result = ", ".join([f"{k}: {v['value']}" for k, v in result.items()])
        formatted_results.append(f"({formatted_result})")
    return "\n".join(formatted_results)