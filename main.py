from fastapi import FastAPI, Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from openai import OpenAI
import os

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/summarize-email/")
async def summarize_email():
    try:
        creds = Credentials(
            token=None,
            refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        )
        service = build("gmail", "v1", credentials=creds)

        # Get total unread count
        profile = service.users().labels().get(userId='me', id='INBOX').execute()
        unread_count = profile.get('messagesUnread', 0)

        # Fetch up to 5 unread email snippets
        results = service.users().messages().list(userId='me', labelIds=['UNREAD'], maxResults=5).execute()
        messages = results.get('messages', [])

        email_bodies = []
        for msg in messages:
            msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            snippet = msg_detail.get('snippet', '')
            email_bodies.append(snippet)

        if not email_bodies:
            return {"summary": "No unread emails to summarize.", "unread_count": unread_count}

        prompt = f"""You are an assistant that reads and summarizes a user's unread email snippets.
The user has {unread_count} unread emails. Here are the most recent {len(email_bodies)} snippets:

{chr(10).join(f"- {s}" for s in email_bodies)}

Give a concise summary of the key messages and tone. Be helpful, brief, and include overall themes."""

        response = client.responses.create(
            model="gpt-4o",
            input=prompt,
            text={"format": {"type": "text"}},
            reasoning={},
            tools=[],
            temperature=0.7,
            max_output_tokens=1024,
            top_p=1,
            store=False
        )

        # Extract the output text
        assistant_message = next(
            (item for item in response.output if item.type == "message"), None
        )

        if assistant_message:
            content_blocks = assistant_message.content
            final_text = "".join(
                block.text for block in content_blocks if block.type == "output_text"
            )
            return {
                "summary": final_text,
                "unread_count": unread_count
            }

        return {"error": "No message output found from GPT."}

    except Exception as e:
        return {"error": str(e)}

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