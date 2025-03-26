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
        user_input = body.get("prompt", "Tell me something cool.")

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        )

        return {"response": response.choices[0].message.content}

    except Exception as e:
        return {"error": str(e)}