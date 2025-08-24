from fastapi import FastAPI
from mcp_server.db_server import mcp as echo_mcp
from mcp_server.gdrive_server import mcp as math_mcp

# Lifespan that properly runs MCP session managers
async def lifespan(app: FastAPI):
    async with echo_mcp.session_manager.run(), math_mcp.session_manager.run():
        yield

app = FastAPI(lifespan=lifespan)

# Mount MCP servers on paths
app.mount("/database", echo_mcp.streamable_http_app())
app.mount("/google_drive", math_mcp.streamable_http_app())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
