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
        user_input = body.get("prompt", "What should I know about Denver this week?")

        response = client.responses.create(
            model="gpt-4o",
            input=[{"role": "user", "content": user_input}],
            text={"format": {"type": "text"}},
            reasoning={},
            tools=[
                {
                    "type": "web_search_preview",
                    "user_location": {
                        "type": "approximate",
                        "country": "US",
                        "region": "CO",
                        "city": "Denver"
                    },
                    "search_context_size": "medium"
                }
            ],
            temperature=1,
            max_output_tokens=2048,
            top_p=1,
            store=True
        )

        return {"response": response.output[0].content}

    except Exception as e:
        return {"error": str(e)}