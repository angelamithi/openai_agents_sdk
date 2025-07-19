import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner,function_tool,WebSearchTool
from pydantic import BaseModel

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environmental variables")

class Tutorial(BaseModel):
    outline:str
    tutorial:str

tutorial_agent=Agent(
    name="Tutorial Agent",
    handoff_description="Used for generating a tutorial based on an outline.",
    instructions=(
        "Given a programming topic and an outline, your job is to generate code snippets for each section of the outline."
        "Format the tutorial in Markdown using a mix of text for explanation and code snippets for examples."
        "Where it makes sense, include comments in the code snippets to further explain the code."
    ),
    model="gpt-4o-mini",
    output_type=Tutorial

)

outline_agent=Agent(
    name="Outline_Agent",
    instructions="Given a particular programming topic, your job is to help come up with a tutorial. You will do that by crafting an outline."
        "After making the outline, hand it to the tutorial generator agent.",
    model="gpt-4o-mini",
    handoffs=[tutorial_agent]
)

async def main():

    response=await Runner.run(outline_agent,"Java programming")
    print(response.final_output)

   
if __name__ == "__main__":
    asyncio.run(main())
