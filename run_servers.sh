#!/bin/bash
source ~/Documents/MCP/hireln-auto/bin/activate   # activate venv

echo "Starting GDrive MCP on port 8001..."
uvicorn mcp_server.gdrive_server:app --port 8001 --reload &

# echo "Starting Resume MCP on port 8002..."
# uvicorn mcp_server.resume_server:app --port 8002 --reload &

# echo "Starting Jobs MCP on port 8003..."
# uvicorn mcp_server.jobs_server:app --port 8003 --reload &

wait
