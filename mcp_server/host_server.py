from fastapi import FastAPI
from mcp_server.db_server import mcp as db_mcp
from mcp_server.gdrive_server import mcp as gdrive_mcp

# Lifespan: ensures both session managers are started/stopped properly
async def lifespan(app: FastAPI):
    async with db_mcp.session_manager.run(), gdrive_mcp.session_manager.run():
        yield

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Mount MCP servers on paths
app.mount("/database", db_mcp.streamable_http_app())
app.mount("/google_drive", gdrive_mcp.streamable_http_app())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
