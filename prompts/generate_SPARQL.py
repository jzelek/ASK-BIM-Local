import re
# Version 3 January 25
# Function to construct SPARQL queries based on recognized classes, properties, and example values using LLM
def construct_sparql_queries(classes_and_properties, question, prefixes, client):
    # Construct the prompt for the LLM to generate the SPARQL query, including the example query
    prompt = f"""
    Your task is to create a valid SPARQL query based only on the provided classes, properties, and prefixes to retrieve the necessary data from the building knowledge graph to answer the user’s question.

    Here is the structure of the knowledge graph:
    
    <classes_and_properties>
    {classes_and_properties}
    </classes_and_properties>
    
    Prefixes to be used:
    
    <prefixes> {prefixes} </prefixes>
    
    The user’s question:
    
    <question> {question} </question>
    
    Instructions:
    
    - Your primary goal is to create a simple and general SPARQL query that retrieves a comprehensive set of data related to the question. 
    - Avoid directly answering the question in the query. Instead, retrieve a relevant set of values that can be interpreted later to provide the answer.
    
    Before constructing the final query, think through the process carefully inside <query_planning> tags:
    
    - Key Concepts and Relationships: Identify the essential entities and relationships in the question.
    - Relevant Classes and Properties: List the provided classes and properties that correspond to these concepts.
    
    Query Structure:
    
    - There is no fixed structure for constructing the query; adapt the query based on the user’s question and the available data.
    - Always include DISTINCT on props:batid_attribute_simple when querying elements to ensure unique real-world objects are returned and avoid duplications.
    - Construct the query to interpret and represent abstract concepts (e.g., relationships, dependencies, or inferred data) as needed, ensuring that the data retrieved can support answering the original question comprehensively.
    
    Review:
    
    - Ensure only the provided classes, properties, and prefixes are used, and use as few of them as possible. 
      You do not need to use all classes if they are not necessary—prefer using a single provided class with its attributes whenever possible.
    - Verify that the query follows valid syntax for the SPARQL endpoint.
    
    Important Notes:
    
    - Prioritize Simplicity: Prefer simple queries that retrieve broader sets of data over complex queries that attempt to directly compute or filter the answer.
    - Include Identifiers: Always include the props:batid_attribute_simple for every element in the query.
    - Include Prefixes: always include the right prefixes from the prefixes list.
    - Avoid Over-Filtering: Add constraints only when essential to keep the query results relevant but comprehensive.
    - Always return a broad set of attributes in the query that can provide sufficient context to reason and answer the question, avoiding queries that return only a limited number of attributes.

    Finally, generate the SPARQL query within triple quotes, following this format:

    ``` Your Generated Query ```
    
    """

    # Call the LLM to generate the SPARQL query
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a SPARQL query generator for a building knowledge graph."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o-mini",
        #model="o1",
    )
    
    response = chat_completion.choices[0].message.content.strip()
    print("-----" * 10 )
    print(f"\nGenerated SPARQL Query for question: {question}:\n{response}")
    print("-----" * 10 )

    # Extracting the text after the </query_planning> tag
    match = re.search(r"</query_planning>\s*(.+)", response, re.DOTALL)
    sparql_query = match.group(1).strip() if match else None
    
    return sparql_query