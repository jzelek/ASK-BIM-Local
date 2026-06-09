# **ASK-BIM: Building Information Tool**
A tool designed to process natural language user queries about buildings using SPARQL queries on an IFC-based Knowledge Graph. This repo modifies the original ASK-BIM to allow it to work with local models instead of the original OpenAI setup. It also provides a systematic approach to handle IFC files of any name.

---

## IFC to LBD Graph Conversion Process
To convert an **IFC file** into a **Knowledge Graph** suitable for querying, we use the **IFCtoLBD Converter**, which can be accessed here:  
🔗 [IFCtoLBD Converter](https://github.com/jyrkioraskari/IFCtoLBD/tree/master)

The **full code** for our conversion process is available in the **"IFC to LBD Conversion"** folder in this repository.

---

## ⚙️ Prerequisites
Before running the chatbot, ensure you have:
- A **running local LLM server** — this guide uses Ollama installed directly on the DGX (no sudo required).
- The converted RDF/Turtle graph included in this repo:
  `IFC-to-LBD Conversion/LBD Model/model_output_geometry.ttl`

GraphDB is optional. By default, this repo reads the local `.ttl` file directly.

---

## Start From a Fresh Terminal

These steps assume you have just opened a Terminal on the **NVIDIA DGX Spark** and want to run the local model or the full ASK-BIM chatbot.

> **Note:** The DGX Spark runs ARM64 (aarch64). You do not have sudo access, so Ollama is installed to your home directory instead of system directories.

---

### Install Ollama on the DGX Spark (first time only)

The standard Ollama install script requires sudo and will fail on the DGX. Use this manual install instead.

Run all of these commands in the same Terminal:

```bash
# Create local bin and lib directories, and add bin to PATH
mkdir -p ~/.local/bin ~/.local/lib
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Download Ollama for ARM64
curl -L "https://ollama.com/download/ollama-linux-arm64.tar.zst" -o ~/ollama-linux-arm64.tar.zst

# Extract the archive
tar -I zstd -xvf ~/ollama-linux-arm64.tar.zst -C ~/

# Move binary and support libraries into place
mv ~/bin/ollama ~/.local/bin/ollama
mv ~/lib/ollama ~/.local/lib/ollama
chmod +x ~/.local/bin/ollama

# Tell Ollama where its libraries are
echo 'export OLLAMA_LIB_PATH="$HOME/.local/lib/ollama"' >> ~/.bashrc
source ~/.bashrc

# Clean up the downloaded archive
rm ~/ollama-linux-arm64.tar.zst

# Verify the install
ollama --version
```

If `ollama --version` prints a version number, the install succeeded.

> **Why not `curl -fsSL https://ollama.com/install.sh | sh`?**  
> That script writes to `/usr/local` and requires sudo, which is not available on the DGX. The manual install above puts everything under `~/.local` instead.

---

### Pull a model (first time only)

Start the Ollama server, then pull the model you want to use:

```bash
ollama serve &
sleep 2
ollama pull qwen3:30b
```

To verify the model is ready:

```bash
ollama run qwen3:30b "Say ready."
```

If the model replies, it is installed and working.

> **Note on qwen3:235b:** This model requires ~135 GB of RAM to load. The DGX Spark has ~121 GB, which is not enough. Use `qwen3:30b` or a smaller quantization instead.

---

### Start Ollama on a fresh Terminal

Every time you open a new Terminal, start the Ollama server before running ASK-BIM:

```bash
pgrep ollama > /dev/null || ollama serve > ~/.ollama/server.log 2>&1 &
sleep 2
```

The `pgrep` check prevents launching a duplicate server if one is already running.

To check if the server is already running:

```bash
curl http://127.0.0.1:11434
```

If it responds, the server is up and you can skip the `ollama serve` step.

---

### Use a different Ollama model

To use another model, pull it first:

```bash
ollama pull llama3.2:1b
```

Then run ASK-BIM with that model in the same Terminal:

```bash
cd ASK-BIM
source ASK-BIM_venv/bin/activate
LOCAL_LLM_MODEL="llama3.2:1b" python main.py
```

Replace `llama3.2:1b` with the model you want to use.

---

### Option A: Test only the local LLM

Use this when you only want to check that the local model can answer.

Run all of these commands in the same Terminal:

```bash
pgrep ollama > /dev/null || ollama serve > ~/.ollama/server.log 2>&1 &
sleep 2
cd ASK-BIM
curl http://127.0.0.1:11434/api/tags
LOCAL_LLM_MODEL="qwen3:30b" python3 ask_llm.py "Say ready."
```

If it is working, the model should answer with something short, usually `ready`.

To ask your own direct model question, replace the text inside quotes:

```bash
python3 ask_llm.py "Explain what an IFC file is in one sentence."
```

This tests only the chat model. It does not inspect the building file and it does not use GraphDB.

---

### Option B: Run the full ASK-BIM chatbot

Use this when you want to ask questions about the building data.

**First-time setup:**

```bash
pgrep ollama > /dev/null || ollama serve > ~/.ollama/server.log 2>&1 &
sleep 2
cd ASK-BIM
python3 -m venv ASK-BIM_venv
source ASK-BIM_venv/bin/activate
python -m pip install -r requirements.txt
LOCAL_LLM_MODEL="qwen3:30b" python main.py
```

**Later runs** (virtual environment already exists):

```bash
pgrep ollama > /dev/null || ollama serve > ~/.ollama/server.log 2>&1 &
sleep 2
cd ASK-BIM
source ASK-BIM_venv/bin/activate
LOCAL_LLM_MODEL="qwen3:30b" python main.py
```

Important: `main.py` is not just a model test. It uses the local model and the converted building graph.

The local LLM is served by Ollama at:

```
http://127.0.0.1:11434
```

That address means the model is running on the DGX itself. It is not OpenAI.

The full chatbot uses:
- the local LLM,
- the converted local RDF/Turtle building graph,
- SPARQL queries over that graph.

By default, `main.py` runs a predefined question. To change the question, open `main.py` and edit this line:

```python
user_question = "Which corridors have doors wider than 900mm?"
```

---

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

To reset the generated files for the active IFC graph:

```bash
rm -rf generated_ifc_data/Barcelona
```

The source IFC and Turtle files are not inside this generated folder, so deleting it does not remove the original building data.

---

## Direct LLM Request With Curl

If you want to talk to the local model without using Python, run:

```bash
curl http://127.0.0.1:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3:30b",
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

### `DanielH is not in the sudoers file`
The standard Ollama install script requires sudo. On the DGX you do not have sudo access. Follow the manual install instructions at the top of this README instead.

### `ollama: command not found`
Either Ollama has not been installed yet, or `~/.local/bin` is not on your PATH in this Terminal session. Run:

```bash
source ~/.bashrc
```

If it still fails, follow the manual install instructions from the top of this README.

### `Error: listen tcp 127.0.0.1:11434: bind: address already in use`
An Ollama server is already running. This is fine — you do not need to start another one. Continue with your `ollama run` or `python main.py` command.

To confirm it is running:

```bash
curl http://127.0.0.1:11434
```

### `llama-server process has terminated: signal: killed`
The model is too large for available RAM. This happens with `qwen3:235b`, which requires ~135 GB but the DGX Spark only has ~121 GB. Use `qwen3:30b` instead:

```bash
ollama pull qwen3:30b
ollama run qwen3:30b
```

### `cannot execute binary file: Exec format error`
You downloaded the wrong architecture. The DGX Spark is ARM64. Make sure you used the `arm64` URL:

```
https://ollama.com/download/ollama-linux-arm64.tar.zst
```

Do not use the `amd64` version — that is for Intel/AMD machines.

### `ModuleNotFoundError: No module named 'SPARQLWrapper'`
The Python packages have not been installed in the current Terminal session. Run:

```bash
cd ASK-BIM
source ASK-BIM_venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

### `Connection refused` when running `python main.py`
Make sure `USE_LOCAL_RDF_FILE` in `config.py` is set to `true`:

```python
USE_LOCAL_RDF_FILE = os.getenv("USE_LOCAL_RDF_FILE", "true").lower() == "true"
```

If you intentionally set `USE_LOCAL_RDF_FILE=false`, Python will try to use GraphDB instead. In that case, start GraphDB, make sure the Barcelona knowledge graph is loaded, and check that this value in `config.py` matches your GraphDB repository:

```python
SPARQL_ENDPOINT = "http://127.0.0.1:7200/repositories/Barcelona2"
```

You can test the endpoint from the Terminal:

```bash
curl http://127.0.0.1:7200/repositories/Barcelona2
```

If GraphDB is not running, this command will fail.

### `kg_data.json is empty`
If a previous run failed, `kg_data.json` may have been created as an empty cache. The app now detects this and tries to rebuild it. To remove it manually and rerun:

```bash
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
  ```
  LOCAL_IFC_FILE = "IFC-to-LBD Conversion/IFC model/Barcelona.ifc"
  USE_LOCAL_RDF_FILE = True
  LOCAL_RDF_FILE = "IFC-to-LBD Conversion/LBD Model/model_output_geometry.ttl"
  ```

- **Generated Output Folder**  
  Cache files and diagrams for the active graph are saved together.
  ```
  GENERATED_OUTPUT_DIR = "generated_ifc_data/Barcelona"
  KG_CACHE_FILE = "generated_ifc_data/Barcelona/kg_data.json"
  GRAPH_DIAGRAM_DIR = "generated_ifc_data/Barcelona/graph_diagrams"
  ```

- **SPARQL Endpoint**  
  Optional. Use this only if you set `USE_LOCAL_RDF_FILE=false` and want to query GraphDB instead of the local `.ttl` file.
  ```
  SPARQL_ENDPOINT = "http://127.0.0.1:7200/repositories/Barcelona2"
  ```

- **Ontology Prefixes**  
  Prefixes manually extracted from the IFC-Graph for use in queries.
  ```
  PREFIXES = {
      "ifc": "https://standards.buildingsmart.org/IFC/DEV/IFC2x3/TC1/OWL#",
      "bot": "https://w3id.org/bot#",
      "props": "http://lbd.arch.rwth-aachen.de/props#"
  }
  ```

- **Local LLM Endpoint**  
  Set the local model endpoint and model name. The default setup uses Ollama's native API and disables thinking output for Qwen-style models.
  ```
  LOCAL_LLM_API_KIND = "ollama"
  LOCAL_LLM_BASE_URL = "http://127.0.0.1:11434"
  LOCAL_LLM_MODEL = "qwen3:30b"
  LOCAL_LLM_MAX_TOKENS = 512
  ```

  For local servers that expose `/v1/chat/completions`, set:
  ```
  LOCAL_LLM_API_KIND = "openai_compatible"
  LOCAL_LLM_BASE_URL = "http://127.0.0.1:<port>/v1"
  ```

---

## 🔍 Additional Notes
- Ensure your **triplestore instance is accessible** and properly configured if using GraphDB.
- The chatbot can be extended with **additional processing steps** for improved reasoning.
- Models are stored in `~/.ollama/models`. On the DGX, make sure your home directory has enough disk space before pulling large models.

---

## 📜 License
This project is open-source.
