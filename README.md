# **ASK-BIM: Building Information Tool**
A tool designed to process natural language user queries about buildings using SPARQL queries on an IFC-based Knowledge Graph.

---

## 🚀 Running the Chatbot

### Prerequisites
- Running triplestore instance with an IFC file already converted in IFC-Graph

### Process
The chatbot follows a multi-step process where it:
1. **Simplifies the question** (if necessary).
2. **Identifies relevant IFC classes** from the Knowledge Graph.
3. **Generates a SPARQL query** to fetch data.
4. **Produces a final answer** using query results.

### Run the chatbot with a test question

python main.py

By default, `main.py` runs a **predefined user query**. Modify the variable inside `main.py` to test different queries.

## 📝 Configuration
Modify `config.py` to update:
- **SPARQL endpoint** = A running triplestore instance with IFC-graph stored in it (i.e: "http://127.0.0.1:7200/repositories/Barcelona2")
- **Prefixes for the ontology** = Prefixes manually extracted from the IFC-graph
- **OpenAI API Key** = Personal openai key
