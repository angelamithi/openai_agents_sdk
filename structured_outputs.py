import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner
from pydantic import BaseModel

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environmental variables")

class  Recipe(BaseModel):
    title:str
    ingredients:list[str]
    cooking_time:int
    servings:int

recipe_agent = Agent(
    name="Recipe Agent", 
    instructions=("You are an agent for creating recipes. You will be given the name of a food and your job"
                  " is to output that as an actual detailed recipe. The cooking time should be in minutes."),
    output_type=Recipe
)


async def main():
    response=await Runner.run(recipe_agent, "Sasuage with Spaghetti") 
    print(response.final_output)

   
if __name__ == "__main__":
    asyncio.run(main())
