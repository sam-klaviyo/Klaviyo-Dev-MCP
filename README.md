# Klaviyo Developer MCP
An MCP that provides Cursor/Claude/etc with any Klaviyo confluence spaces you desire and the engineering handbook. All data is kept locally and not sent anywhere except to the MCP client, and a local, open-source embedding model is used for accurate information retrieval. Data is indexed and retrieved using contextual embeddings, enhancing retrieval based on user intent and context.

The code is set up to be extensible and easy to add new data sources, using the base platform of open-source AI models for information retrieval and secure local data storage. Potential future additions using this MCP server: providing your chatbot with semantic search over previous App and Fender PRs, search over google docs (RFCs, roadmap docs, etc), etc.


## Installation and Setup
First, make sure uv is installed and you are using python version 3.12.9

```bash
pip install uv
pyenv activate 3.12.9
```

Next, install dependencies
```bash
uv venv && uv sync
```

### Confluence Setup
For accessing confluence data, you must first have a confluence API token. To make one, [click here](https://id.atlassian.com/manage-profile/security/api-tokens)
Click on create an API Token, not the token with scopes option

Copy this confluence API token and your Klaviyo email into a .env file in this repo's root directory:
```bash
CONFLUENCE_API_TOKEN=<your API token>
KLAVIYO_EMAIL=<your klaviyo email>
BASE_DIR=<the absolute path to this repo>
```

### Eng Handbook Setup
Make sure you have the eng handbook in the correct place (Klaviyo/Repos/eng-handbook), and that it is up to date!

## Building the Indices (Indexes?)

### Confluence
```bash
python src/retrieval_stuff/build_confluence_index.py.py \
  --sentence_num 10 \
  --chunk_size 1024 \
  --hf_name "avsolatorio/GIST-small-Embedding-v0" \
  --dimension 384 \
  --confluence_spaces "ResDev" "EN" \
  --env_path .env
```

More info about these settings in retrieval_stuff/README.md. You can specify how documents are chunked, what embedding model to use for retrieval, and which confluence spaces to pull from (here it pulls the R&D and Engineering spaces).

### Eng Handbook
```bash
python src/retrieval_stuff/build_eng_handbook_index.py \
  --handbook_path <path to your eng handbook repo> \
  --sentence_num 10 \
  --chunk_size 1024 \
  --hf_name "avsolatorio/GIST-small-Embedding-v0" \
  --dimension 384
```
This will take longer than the confluence one. Larger chunk sizes (5,000 - 10,000) will reduce the indexing time and speed up retrieval if needed.

## MCP Inspector
To run the [MCP inspector tool](https://modelcontextprotocol.io/docs/tools/inspector) to debug any changes:
```bash
npx @modelcontextprotocol/inspector bash run_mcp.sh
```

## Setting up the MCP server
TBD