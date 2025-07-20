from agents import Agent, Runner, handoff, RunContextWrapper
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
)

import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environmental variables")

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide assistance with math queries. Explain your reasoning at each step and include examples"
)

def on_math_handoff(ctx: RunContextWrapper[None]):
    print("Handing off to math tutor agent")

# This agent has the capability to handoff to either the history or math tutor agent
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question." +
    "If neither agent is relevant, provide a general response.",
    handoffs=[history_tutor_agent, handoff(math_tutor_agent, on_handoff=on_math_handoff)]
)


async def main():


    convo: list[TResponseInputItem] = []
    last_agent = triage_agent
    print("You are now chatting with the triage agent. Type 'exit' to end the conversation.")
    while True:
        user_input = input("You: ")
        print("You: " + user_input)

        if user_input == "exit":
            print("Goodbye!")
            break

        convo.append({"content": user_input, "role": "user"})
        result = await Runner.run(last_agent, convo)

        convo = result.to_input_list()
        last_agent = result.last_agent

        print(f"{last_agent.name}: {result.final_output}\n")
 


   
if __name__ == "__main__":
    asyncio.run(main())