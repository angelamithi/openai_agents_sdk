from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)

class UserProfile(BaseModel):
    id: str
    name: str
    admin: bool

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
    model="gpt-4o-mini" # usually the guardrail agent can be cheaper than the main agent
)

@input_guardrail
async def cheat_detection_guardrail(
    ctx: RunContextWrapper[UserProfile], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    # Skip guardrail check if user is admin
    if ctx.context.admin:
        return GuardrailFunctionOutput(
            output_info=HomeworkCheatDetectionOutput(attempting_cheat=False, explanation="Admin bypass"),
            tripwire_triggered=False
        )

    detection_result = await Runner.run(homework_cheat_guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=detection_result.final_output,
        tripwire_triggered=detection_result.final_output.attempting_cheat,
    )

study_helper_agent = Agent[UserProfile](
    name="Study Helper Agent",
    instructions="You assist users in studying by explaining concepts or providing guidance, without directly solving homework or test questions.",
    input_guardrails=[cheat_detection_guardrail],
    model="gpt-4o"
)

async def main():

    profile = UserProfile(id="123", name="Alex", shopping_cart=[])
    print("You are now chatting with the shopping assistant. Type 'exit' to end the conversation.")
    convo_items: list[TResponseInputItem] = []
    while True:
        user_input = input("You: ")

        if user_input == "exit":
            print("Goodbye!")
            break

        convo_items.append({"content": user_input, "role": "user"})
        result = await Runner.run(shopping_agent, convo_items, context=profile)
        
        print(f"Shopping Assistant: {result.final_output}")
        
        convo_items = result.to_input_list()


   
if __name__ == "__main__":
    asyncio.run(main())