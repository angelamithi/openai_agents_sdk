import os
from dotenv import load_dotenv

load_dotenv()
api_key=os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environmental variables ")
    