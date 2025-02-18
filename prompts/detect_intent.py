# Function to interact with OpenAI's chat completions API for intent classification
def detect_intent(user_question, client):
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a query intent classifier for a building information system."},
            {
                "role": "user",
                "content": f"""
                You can access two different functionalities and use them as singular modules or combine them to answer the question.
                
                One is to run sparql queries on the Knowledge graph representing a building and get some results to answer the question:
                Example: Question: What is the smallest window in the building? Intent: SPARQL_AGGREGATION (because to extract the smallest window is needed to compute the dimensions of all the windows)

                One is to answer general questions about construction or building:
                Example: Question: What are the most used materials to be recycled in a building? Intent: GENERAL_QUESTION

                The combination of the two functionalities can be:
                Example: Question: Is the number of windows enough for this building? Intent: SPARQL_AGGREGATION + GENERAL_QUESTION (the query requires retrieving data from the graph and combining it with general knowledge)

                Your task is to classify the user's question into one of the following intents:
                - SPARQL_AGGREGATION: The question requires aggregated data or calculations involving multiple building elements to retrieve from the knowledge graph.
                - GENERAL_QUESTION: The question requires general knowledge.
                - SPARQL_AGGREGATION + GENERAL_QUESTION: The question requires both querying the knowledge graph and applying general knowledge.

                User Question: {user_question}
                
                Your response has to be just the intent value without nothing else.
                """
            }
        ],
        model="gpt-4o-mini",
    )
    
    response = chat_completion.choices[0].message.content.strip()
    print(f"\nDetected Intent: {response}")
    return response