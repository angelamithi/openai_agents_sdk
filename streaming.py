import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner,function_tool,WebSearchTool,handoff,RunContextWrapper
from pydantic import BaseModel
from openai.types.responses import ResponseTextDeltaEvent

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environmental variables")


agent = Agent(
        name="Joker",
        instructions="You are a helpful assistant.",
        model="gpt-4o-mini"
    )

async def main():   
    result=Runner.run_streamed(agent,"Please tell me 5 jokes")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
