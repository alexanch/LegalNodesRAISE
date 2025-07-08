import os
import re
import wget
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from utils import (
    load_api_key,
    extract_text_from_pdf,
    save_report,
    verify_signature,
    send_message,
    fetch_bot_user_id,
    bot_user_id
)

from llm_client import GroqClient, CustomAPIClient

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

user_sessions = {}  # Store client and vendor URLs per user

class CompareRequest(BaseModel):
    pdf_url_1: str
    pdf_url_2: str
    mode: str = "groq"

def download_pdf(url: str) -> str:
    os.makedirs("dpa_docs", exist_ok=True)
    filename = os.path.basename(url.split("id=")[-1]) + ".pdf"
    filepath = os.path.join("dpa_docs", filename)
    return wget.download(url, out=filepath)

def process_comparison(customer_doc: str, external_doc: str, client) -> str:
    combined_output = ""
    for filename in os.listdir("prompts"):
        if filename.endswith(".txt"):
            with open(os.path.join("prompts", filename), "r", encoding="utf-8") as f:
                prompt = f.read()
            prompt_filled = prompt.format(customer_doc=customer_doc, external_doc=external_doc)
            output = client.run_prompt(prompt_filled)
            combined_output += f"\n=== Output for {filename} ===\n{output}\n"

    with open("FINAL_REPORT.txt", "r", encoding="utf-8") as f:
        final_prompt = f.read()

    full_prompt = f"{final_prompt}\n\n=== Combined Outputs ===\n{combined_output}"
    final_output = client.run_prompt(full_prompt)
    save_report(final_output)
    return final_output

@app.post("/compare")
async def compare(request: CompareRequest):
    try:
        pdf1_path = download_pdf(request.pdf_url_1)
        pdf2_path = download_pdf(request.pdf_url_2)
        customer_doc = extract_text_from_pdf(pdf1_path)
        external_doc = extract_text_from_pdf(pdf2_path)

        client = GroqClient(api_key=load_api_key("groq_api_key.txt")) if request.mode == "groq" else \
                 CustomAPIClient(api_url='http://95.179.250.102:3333/api/chat', api_key=load_api_key("api_key.txt"))

        final_output = process_comparison(customer_doc, external_doc, client)
        return {"result": final_output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during comparison: {e}")

@app.on_event("startup")
async def startup_event():
    await fetch_bot_user_id()

def extract_url(text: str) -> str:
    match = re.search(r'<(https?://[^>|]+)>', text) or re.search(r'(https?://[^\s]+)', text)
    return match.group(1) if match else ""

@app.post("/slack/events")
async def slack_events(request: Request):
    body = await request.body()
    headers = request.headers
    if not verify_signature(body, headers.get("x-slack-request-timestamp"), headers.get("x-slack-signature")):
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()

    if payload.get("type") == "url_verification":
        return {"challenge": payload["challenge"]}
    if payload.get("type") != "event_callback":
        return {"ok": True}

    event = payload.get("event", {})
    user = event.get("user")
    bot_id = event.get("bot_id")
    channel = event.get("channel")
    event_type = event.get("type")
    channel_type = event.get("channel_type")
    text = event.get("text", "")
    subtype = event.get("subtype")

    # Ignore messages from bots (including this bot)
    if user == bot_user_id or bot_id is not None or subtype is not None:
        return {"ok": True}

    if user not in user_sessions:
        user_sessions[user] = {"client": None, "vendor": None}

    lowered = text.lower()

    if event_type == "app_mention" or (event_type == "message" and channel_type == "im"):
        # Client command
        if lowered.startswith("client"):
            url = extract_url(text)
            if url:
                user_sessions[user]["client"] = url
                await send_message(channel, "✅ Client document added.")
            else:
                await send_message(channel, "⚠️ No valid URL found for client.")
            return {"ok": True}

        # Vendor command
        if lowered.startswith("vendor"):
            url = extract_url(text)
            if url:
                user_sessions[user]["vendor"] = url
                await send_message(channel, "✅ Vendor document added.")
            else:
                await send_message(channel, "⚠️ No valid URL found for vendor.")
            return {"ok": True}

        # Compare command
        if "compare" in lowered:
            client_url = user_sessions[user].get("client")
            vendor_url = user_sessions[user].get("vendor")
            if not client_url or not vendor_url:
                await send_message(channel, "❗ Please provide both client and vendor URLs before comparison.")
                return {"ok": True}

            await send_message(channel, "⏳ Processing request... Please wait.")
            try:
                pdf1_path = download_pdf(client_url)
                pdf2_path = download_pdf(vendor_url)
                customer_doc = extract_text_from_pdf(pdf1_path)
                external_doc = extract_text_from_pdf(pdf2_path)
                client = GroqClient(api_key=load_api_key("groq_api_key.txt"))
                final_output = process_comparison(customer_doc, external_doc, client)
                await send_message(channel, f"📄 Here is the result:\n{final_output}")
            except Exception as e:
                await send_message(channel, f"❌ Error during comparison: {e}")
            return {"ok": True}

        # Unknown command
        await send_message(
            channel,
            f"Hi <@{user}>, I didn't understand that command.\n\n"
            "You can use:\n"
            "- `client <url>` to upload your company document\n"
            "- `vendor <url>` to upload the vendor document\n"
            "- `compare` to start the analysis."
        )
        return {"ok": True}

    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_server:app", host="0.0.0.0", port=8000, reload=True)
