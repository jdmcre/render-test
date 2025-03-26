from fastapi import FastAPI, Request
from openai import OpenAI
import os

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
def root():
    return {"message": "API is up and running!"}

@app.post("/run-script/")
async def run_script(request: Request):
    try:
        body = await request.json()
        user_input = body.get("prompt")

        if not user_input:
            return {"error": "Missing 'prompt' in request body."}

        response = client.responses.create(
            model="gpt-4o",
            tools=[{ "type": "web_search_preview" }],
            input=user_input,
            text={"format": {"type": "text"}},
            reasoning={},
            temperature=1,
            top_p=1,
            max_output_tokens=2048,
            store=True
        )

        assistant_message = next(
            (item for item in response.output if item.type == "message"), None
        )

        if assistant_message:
            content_blocks = assistant_message.content
            final_text = "".join(
                block.text for block in content_blocks if block.type == "output_text"
            )
            return {"response": final_text}

        return {"error": "No assistant message returned in response."}

    except Exception as e:
        return {"error": str(e)}