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
- A **running local LLM server**, such as Ollama, LM Studio, vLLM, or llama.cpp server.
- The converted RDF/Turtle graph included in this repo:
  `IFC-to-LBD Conversion/LBD Model/model_output_geometry.ttl`

GraphDB is optional. By default, this repo reads the local `.ttl` file directly.

---

## Start From a Fresh Terminal
These steps assume you have just opened a Terminal and want to run the local model or the full ASK-BIM chatbot.

### Install Ollama on a new Linux device
Use this if the device does not already have Ollama installed.

Run all of these commands in the same Terminal:

```
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
ollama pull qwen3:0.6b
ollama run qwen3:0.6b "Say ready."
```

If the last command answers, Ollama is installed and the model is ready.

The install command is from the official Ollama Linux download page:

```
https://ollama.com/download/linux
```

For Windows or macOS, install Ollama from:

```
https://ollama.com/download
```

Then open a new Terminal and continue with the same `ollama pull ...` and `ollama run ...` commands.

### Use a different Ollama model
To use another model, pull it first:

```
ollama pull llama3.2:1b
```

Then run ASK-BIM with that model in the same Terminal:

```
cd ASK-BIM
source ASK-BIM_venv/bin/activate
LOCAL_LLM_MODEL="llama3.2:1b" python main.py
```

Replace `llama3.2:1b` with the model you want to use.

### Option A: test only the local LLM
Use this when you only want to check that the local model can answer.

If you installed Ollama directly on this device, run all of these commands in the same Terminal:

```
cd ASK-BIM
curl http://127.0.0.1:11434/api/tags
LOCAL_LLM_MODEL="qwen3:0.6b" python3 ask_llm.py "Say ready."
```

If you are using the old Docker container we created earlier, run all of these commands in the same Terminal:

```
cd ASK-BIM
docker start ask-bim-ollama
curl http://127.0.0.1:11434/api/tags
python3 ask_llm.py "Say ready."
```

If it is working, the model should answer with something short, usually `ready`.

To ask your own direct model question, replace the text inside quotes:

```
python3 ask_llm.py "Explain what an IFC file is in one sentence."
```

This tests only the chat model. It does not inspect the building file and it does not use GraphDB.

### Option B: run the full ASK-BIM chatbot
Use this when you want to ask questions about the building data.

For a first-time setup with native Ollama, run all of these commands in the same Terminal:

```
cd ASK-BIM
python3 -m venv ASK-BIM_venv
source ASK-BIM_venv/bin/activate
python -m pip install -r requirements.txt
LOCAL_LLM_MODEL="qwen3:0.6b" python main.py
```

For a first-time setup with the old Docker container, run all of these commands in the same Terminal:

```
cd ASK-BIM
docker start ask-bim-ollama
python3 -m venv ASK-BIM_venv
source ASK-BIM_venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

For later runs, when the virtual environment already exists, run all of these commands in the same Terminal:

```
cd ASK-BIM
source ASK-BIM_venv/bin/activate
LOCAL_LLM_MODEL="qwen3:0.6b" python main.py
```

Important: `main.py` is not just a model test. It uses the local model and the converted building graph.

The local LLM is served by Ollama at:

```
http://127.0.0.1:11434
```

That address means the model is running on your own computer. It is not OpenAI.

The full chatbot uses:
- the local LLM,
- the converted local RDF/Turtle building graph,
- SPARQL queries over that graph.

By default, `main.py` runs a predefined question. To change the question, open `main.py` and edit this line:

```python
user_question = "Which corridors have doors wider than 900mm?"
```

### Where the graph diagram is saved
When the preprocessed Knowledge Graph context is created, generated files are saved together under `generated_ifc_data/`.

ASK-BIM detects the first `.ifc` file in:

```
IFC-to-LBD Conversion/IFC model/
```

The generated folder is named after that IFC file. For `Barcelona.ifc`, the generated files are:

```
generated_ifc_data/Barcelona/kg_data.json
generated_ifc_data/Barcelona/graph_diagrams/kg_context_graph.svg
generated_ifc_data/Barcelona/graph_diagrams/kg_context_graph.mmd
```

If `kg_data.json` already exists in that folder, the cached KG context is reused and the diagram is not regenerated.

To reset the generated files for the active IFC graph, delete that generated folder:

```
rm -rf generated_ifc_data/Barcelona
```

The source IFC and Turtle files are not inside this generated folder, so deleting it does not remove the original building data.

---

## Direct LLM Request With Curl
If you want to talk to the local model without using Python, run:

```
curl http://127.0.0.1:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3:0.6b",
    "stream": false,
    "think": false,
    "messages": [
      {
        "role": "user",
        "content": "Say ready."
      }
    ],
    "options": {
      "temperature": 0,
      "num_predict": 128
    }
  }'
```

If everything is working, the response should contain a short answer from the model, usually something like `ready`.

---

## Common Errors
### `ModuleNotFoundError: No module named 'SPARQLWrapper'`
This means the Python packages have not been installed in the current Terminal session.

Run these commands together:

```
cd ASK-BIM
source ASK-BIM_venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

### `Connection refused` when running `python main.py`
The beginner setup should not require GraphDB. Make sure this value in `config.py` is still set to `true`:

```python
USE_LOCAL_RDF_FILE = os.getenv("USE_LOCAL_RDF_FILE", "true").lower() == "true"
```

If you intentionally set `USE_LOCAL_RDF_FILE=false`, then Python will use GraphDB instead. In that case, start GraphDB, make sure the Barcelona knowledge graph is loaded, and check that this value in `config.py` matches your GraphDB repository:

```python
SPARQL_ENDPOINT = "http://127.0.0.1:7200/repositories/Barcelona2"
```

You can test the endpoint from the Terminal:

```
curl http://127.0.0.1:7200/repositories/Barcelona2
```

If GraphDB is not running, this command will fail.

### `kg_data.json is empty`
If a previous run failed while GraphDB was unavailable, `kg_data.json` may have been created as an empty cache. The app now detects this and tries to rebuild it.

If you want to remove it manually, then run the chatbot again, use one Terminal box:

```
cd ASK-BIM
rm -rf generated_ifc_data/Barcelona
source ASK-BIM_venv/bin/activate
python main.py
```

---

## 📝 Configuration
Modify `config.py` to update the following settings:

- **Local RDF File**  
  The default setup reads the converted Turtle graph directly from this repo.  
  The first `.ifc` file in `IFC-to-LBD Conversion/IFC model/` is used to name generated cache and diagram folders.
  Example:
  ```
  LOCAL_IFC_FILE = "IFC-to-LBD Conversion/IFC model/Barcelona.ifc"
  USE_LOCAL_RDF_FILE = True
  LOCAL_RDF_FILE = "IFC-to-LBD Conversion/LBD Model/model_output_geometry.ttl"
  ```

- **Generated Output Folder**  
  Cache files and diagrams for the active graph are saved together.  
  Example:
  ```
  GENERATED_OUTPUT_DIR = "generated_ifc_data/Barcelona"
  KG_CACHE_FILE = "generated_ifc_data/Barcelona/kg_data.json"
  GRAPH_DIAGRAM_DIR = "generated_ifc_data/Barcelona/graph_diagrams"
  ```

- **SPARQL Endpoint**  
  Optional. Use this only if you set `USE_LOCAL_RDF_FILE=false` and want to query GraphDB instead of the local `.ttl` file.  
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

- **Local LLM Endpoint**  
  Set the local model endpoint and model name. The default setup uses Ollama's native API and disables thinking output for Qwen-style models.  
  Example:
  ```
  LOCAL_LLM_API_KIND = "ollama"
  LOCAL_LLM_BASE_URL = "http://127.0.0.1:11434"
  LOCAL_LLM_MODEL = "qwen3:0.6b"
  LOCAL_LLM_MAX_TOKENS = 512
  ```

  For local servers that expose `/v1/chat/completions`, set:
  ```
  LOCAL_LLM_API_KIND = "openai_compatible"
  LOCAL_LLM_BASE_URL = "http://127.0.0.1:<port>/v1"
  ```

---

## 🔍 Additional Notes
- Ensure your **triplestore instance is accessible** and properly configured.
- The chatbot can be extended with **additional processing steps** for improved reasoning.

---

## 📜 License
This project is open-source. 
