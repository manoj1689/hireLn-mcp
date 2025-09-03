"""Example showing lifespan support for startup/shutdown with strong typing."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession
from mcp_server.database import Database
from fastapi.middleware.cors import CORSMiddleware
@dataclass
class AppContext:
    """Application context with typed dependencies."""

    db: Database


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context."""
    # Initialize on startup
    db = await Database.connect()
    try:
        yield AppContext(db=db)
    finally:
        # Cleanup on shutdown
        await db.disconnect()


# Pass lifespan to server
mcp = FastMCP("My Database", lifespan=app_lifespan)


# Access type-safe lifespan context in tools
@mcp.tool()
async def get_users(ctx: Context[ServerSession, AppContext]):
    """Get first 5 users from PostgreSQL."""
    rows = await ctx.request_context.lifespan_context.db.query("SELECT id, email FROM users LIMIT 5;")
    return ", ".join([row["email"] for row in rows])

@mcp.tool()
async def get_candidate_info(ctx: Context[ServerSession, dict]):
    """
    Fetch candidate information (name, email, and technical skills).
    """
    rows = await ctx.request_context.lifespan_context.db.query(
        "SELECT name, email, \"technicalSkills\" FROM candidates LIMIT 5;"
    )

    candidates = []
    for row in rows:
        candidates.append(
            f"Name: {row['name']}, Email: {row['email']}, Skills: {row['technicalSkills']}"
        )

    return "\n".join(candidates)


# Run server with streamable_http transport
# if __name__ == "__main__":
#     mcp.run(transport="streamable-http")


# --- Expose as ASGI app ---
app = mcp.streamable_http_app()

# Add CORS support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # add your frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)