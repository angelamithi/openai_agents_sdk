from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, Runner, TResponseInputItem, input_guardrail
from pydantic import BaseModel
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environmental variables")

class HomeworkCheatDetectionOutput(BaseModel):
    attempting_cheat: bool
    explanation: str

homework_cheat_guardrail_agent = Agent(
    name="Homework Cheat Detector",
    instructions=(
        "Determine if the user's query resembles a typical homework assignment or exam question, indicating an attempt to cheat. General questions about concepts are acceptable. "
        " Cheating: 'Fill in the blank: The capital of France is ____.',"
        " 'Which of the following best describes photosynthesis? A) Cellular respiration B) Conversion of light energy C) Evaporation D) Fermentation.'"
        " Not-Cheating: 'What is the capital of France?', 'Explain photosynthesis.'"
    ),
    output_type=HomeworkCheatDetectionOutput,
    model="gpt-4o-mini"
)

@input_guardrail
async def cheat_detection_guardrail(
        ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput :
    
    detection_result = await Runner.run(homework_cheat_guardrail_agent, input)

    return GuardrailFunctionOutput(
        tripwire_triggered=detection_result.final_output.attempting_cheat,
        output_info=detection_result.final_output
    )

study_helper_agent = Agent(
    name="Study Helper Agent",
    instructions="You assist users in studying by explaining concepts or providing guidance, without directly solving homework or test questions.",
    model="gpt-4o",
    input_guardrails=[cheat_detection_guardrail]
)
async def main():

    # response=await Runner.run(study_helper_agent,"What 4 * 2 ?")
    # print(response.final_output)
    response=await Runner.run(study_helper_agent,"What  are the main causes of American civil war?")
    print(response.final_output)


   
if __name__ == "__main__":
    asyncio.run(main())
