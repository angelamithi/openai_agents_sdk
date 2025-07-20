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

class MessageOutput(BaseModel):
    response: str

@output_guardrail
async def forbidden_words_guardrail(ctx: RunContextWrapper, agent: Agent, output: str) -> GuardrailFunctionOutput:
    print(f"Checking output for forbidden phrases: {output}")

    # Funny forbidden phrases to check
    forbidden_phrases = ["fart", "booger", "silly goose"]

    # Convert output to lowercase for case-insensitive comparison
    output_lower = output.lower()

    # Check which forbidden phrases are present in the response
    found_phrases = [phrase for phrase in forbidden_phrases if phrase in output_lower]
    trip_triggered = bool(found_phrases)

    print(f"Found forbidden phrases: {found_phrases}")

    return GuardrailFunctionOutput(
        output_info={
            "reason": "Output contains forbidden phrases.",
            "forbidden_phrases_found": found_phrases,
        },
        tripwire_triggered=trip_triggered,
    )

agent = Agent(
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    output_guardrails=[forbidden_words_guardrail],
    model="gpt-4o-mini",
)
async def main():

    # response=await Runner.run(study_helper_agent,"What 4 * 2 ?")
    # print(response.final_output)
    
    await Runner.run(agent, "Say the word fart")
    print("Guardrail didn't trip - this is unexpected")


   
if __name__ == "__main__":
    asyncio.run(main())