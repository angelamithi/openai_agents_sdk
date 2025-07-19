import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environmental variables")

joke_agent = Agent(
    name="Joke Agent",
    instructions="You are a joke teller. You are given a topic and you need to tell a joke about it.",
    model="gpt-4o-mini"
)
language_agent=Agent(
    name="Language Agent",
    instructions="You are a language expert. You are given a joke and you need to rewrite it in a different language.",
    model="gpt-4o-mini"

)


async def main():
    topic="Boogers"
    result = await Runner.run(joke_agent, topic)
    print(result.final_output)
    joke_result= await Runner.run(joke_agent,topic)
    translated_result=await Runner.run(language_agent,joke_result.final_output)
    print(translated_result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
