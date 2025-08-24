import asyncio
import json
import re
from mcp import ClientSession, types
from mcp.client.stdio import stdio_client, StdioServerParameters
from llm.llm_client import ask_llm  # your helper that queries LLM

# MCP server params (make sure gdrive_server.py is running with "uv run")
server_params = StdioServerParameters(
    command="uv",
    args=["run", "mcp_server/gdrive_server.py", "stdio"],
)

async def run():
    # User query
    user_query = input("Ask something about Google Drive (files, search, metadata): ")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Step 1: LLM decides which tool to use
            tool_choice = await ask_llm(
                f"User query: '{user_query}'.\n"
                "Decide which tool to use: "
                "- 'list_files' (list files in a folder), "
                "- 'search_files' (search by name), "
                "- 'get_file_metadata' (file details).\n"
                "Reply with only the tool name."
            )

            tool_choice = tool_choice.strip().lower()
            print(f"LLM chose tool: {tool_choice}")

            # Step 2: LLM decides tool arguments
            tool_args = await ask_llm(
                f"User query: '{user_query}'.\n"
                f"Chosen tool: {tool_choice}.\n"
                "Reply with valid JSON for the tool arguments.\n"
                "Example:\n"
                "- list_files: {\"folder_id\": \"1QEstxWHH0JuVgPHF8HfYan1aicTHzKzn\", \"limit\": 5}\n"
                "- search_files: {\"folder_id\": \"1QEstxWHH0JuVgPHF8HfYan1aicTHzKzn\", \"query\": \"resume\"}\n"
                "- get_file_metadata: {\"folder_id\": \"1QEstxWHH0JuVgPHF8HfYan1aicTHzKzn\", \"file_id\": \"FILE123\"}"
            )

            print(f"LLM suggested args: {tool_args}")
            # Clean up LLM output
            clean_args = re.sub(r"^```(?:json)?|```$", "", tool_args.strip(), flags=re.MULTILINE).strip()

            try:
                tool_args_json = json.loads(clean_args)
            except Exception as e:
                print(f"⚠️ Failed to parse tool args: {e}, defaulting.")
                tool_args_json = {"folder_id": "1QEstxWHH0JuVgPHF8HfYan1aicTHzKzn"}

            # Step 3: Call MCP tool
            result = await session.call_tool(tool_choice, tool_args_json)

            content = result.content[0]
            tool_output = content.text if isinstance(content, types.TextContent) else str(content)
            print("Tool raw output:\n", tool_output)

            # Step 4: Summarize final answer with LLM
            final_answer = await ask_llm(
                f"User asked: {user_query}\n"
                f"Tool output: {tool_output}\n\n"
                "Give a clear and helpful response."
            )

            print("\n🤖 Assistant Response:\n", final_answer)

if __name__ == "__main__":
    asyncio.run(run())
