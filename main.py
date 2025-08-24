import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

async def main():
    # Start both servers (make sure they are running separately)
    client = MultiServerMCPClient()

    # Add both servers
    await client.add_server("db", transport="sockets", host="127.0.0.1", port=8001)
    await client.add_server("gdrive", transport="sockets", host="127.0.0.1", port=8002)

    # List available tools from both
    tools = await client.list_tools()
    print("Available tools:", tools)

    # Call a tool from DB
    db_result = await client.call_tool("db.query_tool", {"query": "SELECT * FROM users;"})
    print("DB result:", db_result)

    # Call a tool from Google Drive
    gdrive_result = await client.call_tool("gdrive.list_files", {"folder_id": "root"})
    print("Google Drive result:", gdrive_result)

    await client.close()

asyncio.run(main())
