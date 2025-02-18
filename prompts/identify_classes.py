# Version 2
# Function to identify relevant classes for each simplified question
def identify_relevant_classes(simplified_questions, classes, client):
    relevant_classes_for_questions = []
    sub_questions_and_classes = []

    for idx, sub_question in enumerate(simplified_questions, start=1):
        second_prompt = f"""

        First, review the following information:
        
        1. List of available building element classes:
        <classes_list>
        {classes}
        </classes_list>
        
        2. User's question:
        <user_question>
        {sub_question}
        </user_question>
        
        Your goal is to identify the essential classes from the provided list that are necessary to retrieve the data needed to answer the user's question. 
        
        Please follow these steps:
        
        1. Analyze the user's question and the list of classes.
        2. Identify classes that can contain the necessary data to answer the user question.
        3. Infer any additional classes that might be necessary to provide a complete answer, even if they're not explicitly mentioned.
        4. Compile a final list of relevant classes including only the most relevant.
        
        Wrap your thought process inside <class_identification_process> tags:
        
        1. Quote relevant parts of the user's question.
        2. List potentially relevant classes with a brief explanation for each.
        3. Consider relationships between identified classes.
        4. Rank the relevance of each identified class (High, Medium, Low).
        5. Summarize the final list of relevant classes and explain your choices.
        
        Instruction for your response output:
        After completing the analysis, provide the final list of relevant classes in a comma-separated format.
        The output must be enclosed after the tag <question_analysis>.
        Ensure no additional text or explanation follows the closing tag </question_analysis>.
        Only include the class names in the comma-separated format inside the closing tag, with no additional symbols or formatting.
        
        Output format example:
        ** Class1, Class2, Class3
        
        Remember:
        - Include only classes from the provided list.
        - Take into account indirect relationships and inferred data requirements, if needed, recognizing that classes and properties within the knowledge graph may be interconnected.
        - In the final class list include only class with High relevance
        - In the last line with the classes always begin the line with "**"
        
        Now, please proceed with your analysis and provide the list of relevant classes.
        """

        # Call the LLM to determine relevant classes for each sub-question
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an AI assistant specialized in analyzing building-related queries and identifying relevant classes from a building knowledge graph. Your task is to determine which classes are of high relevance to retrieve data for answering a user's question."},
                {"role": "user", "content": second_prompt}
            ],
            model="gpt-4o-mini",
        )

        response_text = chat_completion.choices[0].message.content.strip()
        print(f"\nFull Response for Question {idx}:\n{response_text}")
        
        # Split the output into lines
        lines = response_text.splitlines()
        
        # Iterate over the lines to find the one starting with '**'
        for line in lines:
            if line.startswith('**'):
                # Extract the classes from the line, removing '**' and splitting by commas
                parsed_classes = [cls.strip() for cls in line[2:].split(',') if cls.strip()]

        # Print the sub-question with the classes inside <question_analysis> tags
        print(f"\nSub-Question {idx}:\n{sub_question}")
        print(f"Classes: ", str(parsed_classes))

        sub_questions_and_classes.append({
            "question": sub_question,
            "classes": parsed_classes
        })

    return sub_questions_and_classes