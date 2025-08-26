"""
Example MCP server for Google Sheets integration with lifespan support.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

# Google API
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


@dataclass
class AppContext:
    """Application context with typed Google Sheets client."""

    sheets_service: Any


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Setup Google Sheets client on startup and cleanup on shutdown."""

    # Use Service Account JSON credentials
    creds = Credentials.from_service_account_file(
        "hirelnresumes-85a2a49bc362.json",  # put your JSON key here
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )

    sheets_service = build("sheets", "v4", credentials=creds)

    try:
        yield AppContext(sheets_service=sheets_service)
    finally:
        # No explicit close method, but clean up if needed
        pass


# Init MCP with lifespan
mcp = FastMCP("Google Sheets MCP", lifespan=app_lifespan)

# Replace with your Sheet ID
SPREADSHEET_ID = "1bPLfgh4jUo0rPK9M-X3H-cDOTaqs4W2eslBbnP6SkIw"


@mcp.tool()
async def read_sheet(ctx: Context[ServerSession, AppContext], range_: str = "Sheet1!A:D"):
    """
    Read a range of values from the Google Sheet.
    :param range_: A1 notation range (e.g., "Users!A:D")
    """
    result = (
        ctx.request_context.lifespan_context.sheets_service.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=range_)
        .execute()
    )
    return result.get("values", [])


@mcp.tool()
async def append_row(ctx: Context[ServerSession, AppContext], values: list[str]):
    """
    Append a new row to the Google Sheet.
    :param values: list of cell values, e.g. ["John Doe", "john@example.com", "Software Developer"]
    """
    body = {"values": [values]}
    result = (
        ctx.request_context.lifespan_context.sheets_service.spreadsheets()
        .values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range="Sheet1!A1:D10",
            valueInputOption="RAW",
            body=body,
        )
        .execute()
    )
    return {"updates": result}


@mcp.tool()
async def update_cell(ctx: Context[ServerSession, AppContext], range_: str, value: str):
    """
    Update a specific cell in the Google Sheet.
    :param range_: A1 notation (e.g., "Sheet1!B2")
    :param value: New value for the cell
    """
    body = {"values": [[value]]}
    result = (
        ctx.request_context.lifespan_context.sheets_service.spreadsheets()
        .values()
        .update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_,
            valueInputOption="RAW",
            body=body,
        )
        .execute()
    )
    return {"updated": result}


if __name__ == "__main__":
    mcp.run()


#uv run mcp dev mcp_server/gdrive_server.py
#uv run mcp_server/excelsheet_server.py