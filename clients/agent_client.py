import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import ToolMessage, HumanMessage

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
model = init_chat_model("openai:gpt-4o-mini")


async def main():
    # 1. Setup MCP client (no async with!)
#     client = MultiServerMCPClient(
#     {
#         "db": {
#             "transport": "streamable_http",
#             "url": "http://127.0.0.1:8001/database/mcp/",
#         },
#         "gdrive": {
#             "transport": "streamable_http",
#             "url": "http://127.0.0.1:8001/google_drive/mcp/",
#         },
#     }
# )
    client = MultiServerMCPClient(
    {
        "db": {
            "transport": "streamable_http",
            "url": "http://103.217.247.201/database/mcp/",
        },
        "gdrive": {
            "transport": "streamable_http",
            "url": "http://103.217.247.201/google_drive/mcp/",
        },
    }
)

    # 2. Preload tools (optional but good for debugging)
    tools = await client.get_tools()

    # 3. Define call_model node
    def call_model(state: MessagesState):
        response = model.bind_tools(tools).invoke(state["messages"])
        return {"messages": response}

    # 4. Build graph
    builder = StateGraph(MessagesState)
    builder.add_node(call_model)
    builder.add_node(ToolNode(tools))
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", tools_condition)
    builder.add_edge("tools", "call_model")
    graph = builder.compile()

    # 5. Run interactive agent loop
    async def run_agent(graph):
        print("Type your query (or 'exit' to quit):")
        while True:
            query = input("\n🧑 You: ")
            if query.lower() in {"exit", "quit"}:
                print("👋 Exiting agent...")
                break

            # Wrap user input as a HumanMessage instead of plain str
            agent_response = await graph.ainvoke({"messages": [HumanMessage(content=query)]})

            messages = agent_response.get("messages", [])

            # Separate messages
            human_msgs = [m for m in messages if isinstance(m, HumanMessage)]
            tool_msgs = [m for m in messages if isinstance(m, ToolMessage)]

            if human_msgs:
                print("\n🧑 Human Messages:")
                for m in human_msgs:
                    print(f"- {m.content}")

            if tool_msgs:
                print("\n🛠 Tool Messages:")
                for m in tool_msgs:
                    print(f"- Tool: {m.name}, Output: {m.content}")

    await run_agent(graph)

    # 6. Cleanup MCP client
    if hasattr(client, "aclose"):
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
