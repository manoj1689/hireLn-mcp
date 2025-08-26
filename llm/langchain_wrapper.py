from typing import List, Optional, Any, Dict
import asyncio
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.tools import BaseTool
from llm.llm_client import ask_llm


class AskLLMWrapper(BaseChatModel):
    """LangChain-compatible wrapper around ask_llm with proper tool support."""

    @property
    def _llm_type(self) -> str:
        return "ask_llm_wrapper"

    def bind_tools(self, tools: List[BaseTool], **kwargs: Any):
        """Properly bind tools to the LLM."""
        self.tools = tools
        return self

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> ChatResult:
        # Convert messages to the format expected by your ask_llm function
        conversation_lines = []
        for m in messages:
            if hasattr(m, 'type') and hasattr(m, 'content'):
                conversation_lines.append(f"{m.type}: {m.content}")
            else:
                conversation_lines.append(str(m))
        
        conversation = "\n".join(conversation_lines)
        
        # Add tool information to the system message if tools are available
        system_message = "You are a helpful assistant."
        if hasattr(self, 'tools') and self.tools:
            tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])
            system_message += f"\n\nAvailable tools:\n{tool_descriptions}"
            system_message += "\n\nIf you need to use a tool, respond with a JSON object containing 'tool' and 'tool_input' fields."

        output = await ask_llm(conversation, system_message)

        ai_message = AIMessage(content=output)
        generation = ChatGeneration(message=ai_message)
        return ChatResult(generations=[generation])

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> ChatResult:
        return asyncio.get_event_loop().run_until_complete(
            self._agenerate(messages, stop=stop, **kwargs)
        )