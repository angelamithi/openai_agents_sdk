from flask import Flask, request, Response
from openai import AssistantEventHandler, AsyncOpenAI
import asyncio
from agents.triage_agent import triage_agent
from utils.context import set_context, get_context
from models.flight_models import SearchFlightOutput

app = Flask(__name__)
openai_client = AsyncOpenAI()

class RawStreamingHandler(AssistantEventHandler):
    def __init__(self):
        self._queue = asyncio.Queue()
        self.output_data = None  # For structured response

    async def on_text_created(self, text):
        await self._queue.put(text)

    async def on_tool_end(self, tool_call_id, output):
        # Capture output from tool call
        self.output_data = output
        await super().on_tool_end(tool_call_id, output)

    async def astream(self):
        while True:
            chunk = await self._queue.get()
            if chunk is None:
                break
            yield f"data: {chunk}\n\n"

    async def finish(self):
        await self._queue.put(None)

@app.route("/chat", methods=["POST"])
async def chat():
    data = await request.get_json()
    user_message = data.get("message")
    thread_id = data.get("thread_id") or "default"

    handler = RawStreamingHandler()
    try:
        await triage_agent.chat(
            message=user_message,
            thread_id=thread_id,
            event_handler=handler
        )

        # 👇 After the streaming finishes, inspect the output
        if isinstance(handler.output_data, dict) and "destination" in handler.output_data:
            # Store context after a flight search
            set_context(thread_id, "last_flight_destination", handler.output_data["destination"])
            set_context(thread_id, "last_flight_origin", handler.output_data["origin"])

        return Response(handler.astream(), content_type="text/event-stream")
    except Exception as e:
        return {"error": str(e)}, 500
