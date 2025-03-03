# **ASK-BIM: Building Information Tool**
A tool designed to process natural language user queries about buildings using SPARQL queries on an IFC-based Knowledge Graph.

---

## IFC to LBD Graph Conversion Process
To convert an **IFC file** into a **Knowledge Graph** suitable for querying, we use the **IFCtoLBD Converter**, which can be accessed here:  
🔗 [IFCtoLBD Converter](https://github.com/jyrkioraskari/IFCtoLBD/tree/master)

The **full code** for our conversion process is available in the **"IFC to LBD Conversion"** folder in this repository.

---

## ⚙️ Prerequisites
Before running the chatbot, ensure you have:
- A **running triplestore instance** (such as GraphDB) with an **IFC file already converted** into an IFC-based Knowledge Graph.
- A valid **OpenAI API Key** for natural language processing.

---

## Running the Chatbot
The chatbot follows a structured process:
1. **Simplifies the user query** (if needed).
2. **Identifies relevant IFC classes** in the Knowledge Graph.
3. **Generates a SPARQL query** to retrieve the required data.
4. **Processes the query results** and provides a **final answer**.

### Run the chatbot with a test question
```
python main.py
```
By default, `main.py` runs a **predefined user query**. Modify the `user_question` variable inside `main.py` to test different queries.

---

## 📝 Configuration
Modify `config.py` to update the following settings:

- **SPARQL Endpoint**  
  A running **triplestore instance** where the **IFC-Graph** is stored.  
  Example:  
  ```
  SPARQL_ENDPOINT = "http://127.0.0.1:7200/repositories/Barcelona2"
  ```

- **Ontology Prefixes**  
  Prefixes manually extracted from the **IFC-Graph** for use in queries.  
  Example:
  ```
  PREFIXES = {
      "ifc": "https://standards.buildingsmart.org/IFC/DEV/IFC2x3/TC1/OWL#",
      "bot": "https://w3id.org/bot#",
      "props": "http://lbd.arch.rwth-aachen.de/props#"
  }
  ```

- **OpenAI API Key**  
  Set your **personal OpenAI API key** to enable natural language processing.  
  Example:
  ```
  OPENAI_API_KEY = "your-api-key-here"
  ```

---

## 🔍 Additional Notes
- Ensure your **triplestore instance is accessible** and properly configured.
- The chatbot can be extended with **additional processing steps** for improved reasoning.

---

## 📜 License
This project is open-source. 
