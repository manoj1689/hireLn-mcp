"""
Example MCP server for Google Drive integration with lifespan support.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
import json
import os
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

# Google API
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Load environment variables from a .env file
from dotenv import load_dotenv
load_dotenv()


@dataclass
class AppContext:
    """Application context with typed Google Drive client."""
    drive_service: Any


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Setup Google Drive client on startup and cleanup on shutdown."""

    SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

    # Load credentials JSON from .env
    creds_info = json.loads(os.getenv("GOOGLE_CREDENTIALS"))

    # Use service account info (dict, not file)
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)

    drive_service = build("drive", "v3", credentials=creds)

    try:
        yield AppContext(drive_service=drive_service)
    finally:
        # googleapiclient build() doesn't require explicit close
        pass


# Init MCP with lifespan
mcp = FastMCP("Google Drive MCP", lifespan=app_lifespan)


@mcp.tool()
async def list_files(ctx: Context[ServerSession, AppContext], folder_id: str = None, limit: int = 10):
    """
    List files from Google Drive.
    :param folder_id: (optional) ID of a Google Drive folder. If None, lists from My Drive root.
    :param limit: number of files to return
    """
    query = f"'{folder_id}' in parents" if folder_id else None

    results = (
        ctx.request_context.lifespan_context.drive_service.files()
        .list(
            q=query,
            pageSize=limit,
            fields="files(id, name, mimeType, modifiedTime)",
        )
        .execute()
    )

    files = results.get("files", [])
    if not files:
        return "No files found."

    return "\n".join(
        [f"{f['name']} ({f['id']}) - {f['mimeType']} - modified {f['modifiedTime']}" for f in files]
    )


@mcp.tool()
async def search_files(ctx: Context[ServerSession, AppContext], query: str, folder_id: str = None):
    """
    Search files in Google Drive by name.
    :param query: text to search in file names
    :param folder_id: (optional) restrict search to this folder
    """
    q = f"name contains '{query}'"
    if folder_id:
        q += f" and '{folder_id}' in parents"

    results = (
        ctx.request_context.lifespan_context.drive_service.files()
        .list(q=q, fields="files(id, name, mimeType, modifiedTime)")
        .execute()
    )

    files = results.get("files", [])
    if not files:
        return f"No files found for query '{query}'."

    return "\n".join(
        [f"{f['name']} ({f['id']}) - {f['mimeType']} - modified {f['modifiedTime']}" for f in files]
    )


@mcp.tool()
async def get_file_metadata(ctx: Context[ServerSession, AppContext], file_id: str):
    """
    Fetch metadata for a specific file.
    """
    file = (
        ctx.request_context.lifespan_context.drive_service.files()
        .get(
            fileId=file_id,
            fields="id, name, mimeType, size, createdTime, owners, modifiedTime",
        )
        .execute()
    )

    return {
        "id": file["id"],
        "name": file["name"],
        "type": file["mimeType"],
        "size": file.get("size", "unknown"),
        "created": file.get("createdTime"),
        "modified": file.get("modifiedTime"),
        "owner": file["owners"][0]["emailAddress"] if "owners" in file else "unknown",
    }
print("✅ GDrive MCP server running on port 8001")
# Run server with streamable_http transport
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
    
#uv run mcp dev mcp_server/gdrive_server.py
#uv run mcp_server/excelsheet_server.py