#!/bin/bash
source ~/.zshrc
source /Users/sam.onuallain/Klaviyo-Dev-MCP/.env
cd $BASE_DIR
export PYTHONPATH=$BASE_DIR

source .venv/bin/activate

uv run src/mcp_server/main.py \
    --confluence \
    --confluence_path index/confluence_pages_index \
    --guidebook \
    --guidebook_path index/eng_handbook_index \
    --top_k 5