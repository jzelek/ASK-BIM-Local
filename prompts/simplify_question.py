# VERSION 4
# Function to simplify a complex user question into simpler parts if necessary
def simplify_user_question(user_question, client):
    # Prompt to simplify the question without losing content
    first_prompt = f"""
        Based on the user's question, your task is to divide it into simpler, independent sub-questions if necessary.

        User Question:  
        {user_question}
        
        ---
        
        ### Instructions:
        
        1) **Simplify the Question if Needed:**  
           - If the original question involves details about **multiple types of building elements**, break it into **the fewest possible sub-questions**, each focusing on a distinct building element.  
           - Each sub-question should retrieve **a broad set of data** that contributes to answering the original question.  
           - Sub-questions should be simple enough to be answered using a straightforward SPARQL query.  
        
        2) **Handle Single-Element Questions:**  
           - If the question involves details about **only one type of building element** (e.g., only doors), return the question as a single sub-question.  
        
        3) **Avoid Overlap and Redundancy:**  
           - Sub-questions must be self-contained and independent, without relying on or duplicating the results of other sub-questions.  
           - Do not create multiple sub-questions for the same type of building element.  
           - For example, if a sub-question retrieves information about windows, no other sub-question should request additional details about windows.  
        
        4) **Focus on Distinct Building Elements:**  
           - Create a separate sub-question for each distinct type of building element (e.g., walls, windows, floors).  
           - Avoid combining different building elements in one sub-question (e.g., do not mix walls and windows in a single sub-question).  
        
        5) **Single Building Context:**  
           - Assume the question refers to a single building unless explicitly stated otherwise.  
        
        6) **Avoid Reasoning-Based Sub-Questions:**  
           - Sub-questions should focus on retrieving general data from the knowledge graph, not performing calculations or making interpretations.  
           - Each sub-question should return broad, relevant data that will be used in a later reasoning step to answer the original question.

        5) **Exclude External Knowledge:**  
           - The sub-questions should only include data that can be extracted from the knowledge graph, which represents the building's IFC file.  
           - If part of the user's question involves external knowledge that does not require additional building data beyond what is covered in the sub-questions, 
           remove that part from the sub-questions entirely.
        
        ---
        
        ### **Key Points:**  
        - Construct the **minimum number of sub-questions** needed to retrieve all required data.  
        - Do not split the question if there is a dependency between elements (e.g., one element being contained in another or any other relationship) to ensure the dependency is preserved in the data retrieval.
        - Prefer sub-questions that retrieve **broad sets of data** (e.g., lists of elements) rather than specific values.  
        - Ensure sub-questions focus on different building elements without redundancy.  
        - Sub-questions must be simple, self-contained, and answerable with basic SPARQL queries.  
        - All references to objects, entities, or properties pertain to those in the building knowledge graph.

        REMEMBER:
        - Always exclude from the output the sub-questions that rely solely on external knowledge and do not involve data retrieval from the specific building represented in the knowledge graph.
        
        ---
        
        ### **Output Format**:
        - If the question involves a single type of building element:  
          **Question 1**: Return the original question.  
        
        - If the question involves multiple types of building elements:  
          **Question 1**: [Simplified Sub-Question 1]  
          **Question 2**: [Simplified Sub-Question 2]
        
        ---
        
        ### **Example 1:**  
        **Original Question**: "What are the heights of all doors and the total area of all walls?"  
        **Sub-Questions**:  
        **Question 1**: "What are the heights of all doors?"  
        **Question 2**: "What is the total area of all walls?"  
        
        ### **Example 2:**  
        **Original Question**: "How many windows are on the second floor, and what are their heights?"  
        **Sub-Questions**:  
        **Question 1**: "How many windows are on the second floor, and what are their heights?"  


    """

    # Call the LLM to divide the question into simpler questions
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a question simplifier for a building knowledge graph."},
            {"role": "user", "content": first_prompt}
        ],
        model="gpt-4o-mini",
    )

    response_simplified = chat_completion.choices[0].message.content.strip()
    print(f"\nSimplified Questions: {response_simplified}")

    # Parse the simplified questions from the response
    simplified_questions = []
    for line in response_simplified.split("\n"):
        if line.startswith("**Question"):
            question_text = line.split(":")[1].strip()
            if question_text != "No simplification needed.":
                simplified_questions.append(question_text)

    return simplified_questions