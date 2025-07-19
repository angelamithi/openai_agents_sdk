import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner,function_tool
from pydantic import BaseModel

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environmental variables")


@function_tool
def get_weather(city: str) -> str:
    print(f"Getting weather for {city}")
    return "sunny"

@function_tool
def get_temperature(city: str) -> str:
    print(f"Getting temperature for {city}")
    return "70 degrees"

weather_agent=Agent(
    name="weather agent",
    instructions="You are the local weather agent. You are given a city and you need to tell the weather and temperature. For any unrelated queries, say I cant help with that.",
    model="gpt-4o-mini",
    tools=[get_weather,get_temperature]

)

async def main():
    response=await Runner.run(weather_agent,"Nairobi")
    print(response.final_output)
   

   
if __name__ == "__main__":
    asyncio.run(main())
