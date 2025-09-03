# email_mcp_server.py
import logging
from typing import Optional
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from mcp_server.email_service import EmailService  # <-- your class in email_service.py

logger = logging.getLogger(__name__)

email_service = EmailService()

# Lifespan hook
@asynccontextmanager
async def app_lifespan(app):
    logger.info("🚀 Email MCP server starting up...")
    try:
        yield
    finally:
        logger.info("🛑 Email MCP server shutting down...")

# Attach lifespan to FastMCP
mcp = FastMCP("email-server", lifespan=app_lifespan)

@mcp.tool()
async def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
):
    try:
        if html_body is None:
            success = email_service.send_email(to_email, subject, body)
        else:
            success = email_service.send_email(to_email, subject, body, html_body)

        if success:
            return [TextContent(type="text", text=f"✅ Email sent successfully to {to_email}")]
        else:
            return [TextContent(type="text", text=f"❌ Failed to send email to {to_email}")]
    except Exception as e:
        logger.exception("Error while sending email")
        return [TextContent(type="text", text=f"❌ Error sending email: {str(e)}")]

# --- Expose as ASGI app ---
app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004, reload=True)
