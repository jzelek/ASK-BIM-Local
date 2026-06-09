# Version 2
from config import LOCAL_LLM_MODEL, LOCAL_LLM_TEMPERATURE


def _parse_relevant_classes(response_text, available_classes, question):
    available_set = set(available_classes)
    parsed_classes = []

    for line in response_text.splitlines():
        if line.strip().startswith("**"):
            raw_classes = line.strip()[2:].split(",")
            for class_name in raw_classes:
                cleaned_class = class_name.strip().strip("*`.:; ")
                if cleaned_class in available_set and cleaned_class not in parsed_classes:
                    parsed_classes.append(cleaned_class)

    if parsed_classes:
        return parsed_classes

    for class_name in available_classes:
        if class_name in response_text and class_name not in parsed_classes:
            parsed_classes.append(class_name)

    if parsed_classes:
        return parsed_classes

    question_lower = question.lower()
    keyword_fallbacks = {
        "door": ["beo:Door", "ifc:IfcOpeningElement"],
        "doors": ["beo:Door", "ifc:IfcOpeningElement"],
        "floor": ["bot:Storey", "beo:Slab-FLOOR"],
        "storey": ["bot:Storey", "beo:Slab-FLOOR"],
        "level": ["bot:Storey"],
        "wall": ["beo:Wall"],
        "window": ["beo:Window"],
        "stair": ["beo:Stair", "beo:StairFlight"],
        "column": ["beo:Column"],
    }
    for keyword, fallback_classes in keyword_fallbacks.items():
        if keyword in question_lower:
            for class_name in fallback_classes:
                if class_name in available_set and class_name not in parsed_classes:
                    parsed_classes.append(class_name)

    return parsed_classes


# Function to identify relevant classes for each simplified question
def identify_relevant_classes(simplified_questions, classes, client):
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
            model=LOCAL_LLM_MODEL,
            temperature=LOCAL_LLM_TEMPERATURE,
        )

        response_text = chat_completion.choices[0].message.content.strip()
        
        parsed_classes = _parse_relevant_classes(response_text, classes, sub_question)

        sub_questions_and_classes.append({
            "question": sub_question,
            "classes": parsed_classes
        })

    return sub_questions_and_classes
