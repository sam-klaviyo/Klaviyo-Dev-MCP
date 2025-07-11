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

#### Useful Confluence spaces
- KLAV - Klaviyo Wiki
- EN - Engineering Wiki
- ResDev - R&D Wiki

### Eng Handbook Setup
Make sure you have the eng handbook cloned and up to date. The setup script defaults to `/Users/sam.onuallain/Klaviyo/Repos/eng-handbook`, but you can specify a custom path with `--handbook_path`.

## Building the Indexes

Use the setup script to build your indexes. The script will automatically handle environment setup, create necessary directories, and build the specified indexes.

### Basic Usage

```bash
# Build confluence index for specific spaces
python setup_index.py --confluence ResDev EN

# Build handbook index
python setup_index.py --handbook

# Build both indexes
python setup_index.py --confluence --handbook ResDev EN KLAV
```

### Advanced Configuration

```bash
# Use custom embedding model
python setup_index.py --confluence --embed_model sentence-transformers/all-MiniLM-L6-v2 ResDev EN

# Custom chunk size and dimension
python setup_index.py --confluence --chunk_size 4096 --dimension 768 ResDev EN

# Custom handbook path
python setup_index.py --handbook --handbook_path /path/to/your/eng-handbook
```

### Available Options

- `--confluence`: Enable building confluence index
- `--handbook`: Enable building handbook index  
- `--embed_model`: Embedding model to use (default: avsolatorio/GIST-small-Embedding-v0)
- `--chunk_size`: Size of document chunks (default: 2048)
- `--dimension`: Embedding dimension (default: 384)
- `--handbook_path`: Path to engineering handbook (default: /Users/sam.onuallain/Klaviyo/Repos/eng-handbook)
- `--env_path`: Path to .env file (default: .env)

Run `python setup_index.py --help` for full documentation.

**Note:** Larger chunk sizes (4000-8000) will reduce indexing time and speed up retrieval, but may reduce precision for specific queries.

## MCP Inspector
To run the [MCP inspector tool](https://modelcontextprotocol.io/docs/tools/inspector) to debug any changes:
```bash
npx @modelcontextprotocol/inspector bash run_mcp.sh
```

## Setting up the MCP server
Put this in whatever MCP config you need to:
```json
"mcpServers": {
      "klaviyo_dev_mcp": {
        "command": "bash",
        "args": [
          "<path to run_mcp.sh>"
        ]
      }
    }
```