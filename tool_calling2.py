import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner,function_tool,WebSearchTool
from pydantic import BaseModel

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environmental variables")

news_agent = Agent(
    name="News Reporter",
    instructions="You are a news reporter. Your job is to find recent news articles on the internet about US politics.",
    model="gpt-4o-mini",
    tools=[WebSearchTool()]

)


async def main():


    result = await Runner.run(news_agent, "find news")
    print(result.final_output)

   
if __name__ == "__main__":
    asyncio.run(main())
