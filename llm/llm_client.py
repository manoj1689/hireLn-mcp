import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client once
llm = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
print(type(llm))
async def ask_llm(prompt: str, system_message: str = "You are a helpful assistant."):
    """Call the LLM with a user prompt and return its response text"""
    response = await llm.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
