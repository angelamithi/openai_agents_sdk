from flask import Flask, request, Response, jsonify
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
        self.output_data = None
        self.final_output = ""

    async def on_text_created(self, text):
        await self._queue.put(text)
        self.final_output += text

    async def on_tool_end(self, tool_call_id, output):
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
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing required field: user_id"}), 400

    # Fetch or initialize conversation
    convo = get_context(user_id, thread_id, "convo") or []
    convo.append({"role": "user", "content": user_message})

    handler = RawStreamingHandler()

    try:
        result = await triage_agent.run(convo, event_handler=handler)

        # Update the convo with model response and save
        convo = result.to_input_list()
        set_context(user_id, thread_id, "convo", convo)

        # Optionally save other stateful context
        if isinstance(handler.output_data, dict):
            if "destination" in handler.output_data:
                set_context(user_id, thread_id, "last_flight_destination", handler.output_data["destination"])
            if "origin" in handler.output_data:
                set_context(user_id, thread_id, "last_flight_origin", handler.output_data["origin"])

        return Response(handler.astream(), content_type="text/event-stream")

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/history", methods=["GET"])
def get_history():
    user_id = request.args.get("user_id")
    thread_id = request.args.get("thread_id", "default")

    if not user_id:
        return jsonify({"error": "Missing required parameter: user_id"}), 400

    convo = get_context(user_id, thread_id, "convo") or []
    return jsonify({"history": convo})
