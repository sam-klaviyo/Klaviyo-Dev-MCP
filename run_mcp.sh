#!/bin/bash
source ~/.zshrc
pyenv activate kvyo-mcp

cd /Users/sam.onuallain/Klaviyo-Dev-MCP/kvyo-mcp
uv run src/engineering_guidebook.py