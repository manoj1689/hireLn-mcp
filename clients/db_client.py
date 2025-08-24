
import asyncio
from mcp import ClientSession, types
from mcp.client.stdio import stdio_client, StdioServerParameters
from llm.llm_client import ask_llm  # helper to call LLM

server_params = StdioServerParameters(
    command="uv",
    args=["run", "mcp_server/db_server.py", "stdio"],
)

async def run():
    user_query = input("Ask something (about users or candidates): ")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 🔹 Step 1: Ask LLM which tool to use
            tool_choice = await ask_llm(
                f"User query: '{user_query}'. "
                "Decide which tool to use: 'get_users' (for general users) or 'get_candidate_info' (for candidates). "
                "Reply with only the tool name."
            )

            tool_choice = tool_choice.strip().lower()
            print(f"LLM chose tool: {tool_choice}")

            # 🔹 Step 2: Call the appropriate MCP tool
            if "candidate" in tool_choice:
                result = await session.call_tool("get_candidate_info")
            else:
                result = await session.call_tool("get_users")

            content = result.content[0]
            tool_output = content.text if isinstance(content, types.TextContent) else str(content)
            print("Tool raw output:\n", tool_output)

            # 🔹 Step 3: Summarize final answer with LLM
            final_answer = await ask_llm(
                f"User asked: {user_query}\n"
                f"Tool output: {tool_output}\n\n"
                "Give a clear and helpful response."
            )

            print("\n🤖 Assistant Response:\n", final_answer)

if __name__ == "__main__":
    asyncio.run(run())
