import os
import time
import hmac
import hashlib
import httpx
import re
from dotenv import load_dotenv

import os
from datetime import datetime

load_dotenv()

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

bot_user_id = None  # Will be set on startup


def verify_signature(body: bytes, timestamp: str, slack_signature: str) -> bool:
    if timestamp is None or slack_signature is None:
        print("Skipping signature verification (no headers present)")
        return True  # Skip verification for local testing or curl
    if abs(time.time() - int(timestamp)) > 60 * 5:
        print("Request timestamp too old.")
        return False
    sig_basestring = f"v0:{timestamp}:{body.decode()}"
    my_signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode(), sig_basestring.encode(), hashlib.sha256
    ).hexdigest()
    is_valid = hmac.compare_digest(my_signature, slack_signature)
    if not is_valid:
        print(f"Invalid signature. Expected {my_signature} got {slack_signature}")
    return is_valid


async def send_message(channel: str, text: str):
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    json_data = {"channel": channel, "text": text}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=json_data)
        data = resp.json()
        print("Slack API response:", data)
        if not data.get("ok"):
            print("Failed to send message:", data.get("error"))


async def fetch_bot_user_id():
    global bot_user_id
    url = "https://slack.com/api/auth.test"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers)
        data = resp.json()
        if data.get("ok"):
            bot_user_id = data["user_id"]
            print(f"Bot user ID: {bot_user_id}")
        else:
            print("Failed to fetch bot user ID:", data)


import io
import pdfplumber
from transformers import AutoTokenizer
from fastapi import HTTPException


import os
import time
import hmac
import hashlib
import httpx
from dotenv import load_dotenv

load_dotenv()

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

bot_user_id = None  # Will be set on startup


def load_api_key(filename):
    try:
        with open(filename, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def extract_text_from_pdf(pdf_path):
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
    return full_text

def count_tokens_with_transformers(text, model_name="bert-base-uncased"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokens = tokenizer.encode(text, truncation=False)
    return len(tokens)

# # Example usage
# pdf_path = "dpa_dfb.pdf"
# text = extract_text_from_pdf(pdf_path)
# token_count = count_tokens_with_transformers(text)

# print(f"Token count using Transformers: {token_count}")


import markdown
from bs4 import BeautifulSoup

def convert_markdown_to_styled_html(md_path, html_output_path="report.html", title="Compliance Report"):
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Convert markdown to basic HTML
    raw_html = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

    # Add styles and structure
    soup = BeautifulSoup(raw_html, "html.parser")
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
            body {{
                font-family: 'Segoe UI', sans-serif;
                background-color: #f7fafc;
                color: #2d3748;
                margin: 2rem auto;
                max-width: 850px;
                line-height: 1.6;
                padding: 2rem;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.05);
            }}
            h1, h2, h3 {{
                color: #2b6cb0;
            }}
            code, pre {{
                background: #edf2f7;
                padding: 0.2em 0.4em;
                border-radius: 4px;
                font-family: monospace;
            }}
            pre {{
                padding: 1em;
                overflow-x: auto;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 1rem;
            }}
            th, td {{
                border: 1px solid #cbd5e0;
                padding: 0.5em;
                text-align: left;
            }}
            th {{
                background-color: #ebf8ff;
            }}
            blockquote {{
                border-left: 4px solid #4299e1;
                padding-left: 1em;
                color: #4a5568;
                background: #f0f4f8;
                margin: 1em 0;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        {str(soup)}
    </body>
    </html>
    """

    # Write output
    with open(html_output_path, "w", encoding="utf-8") as out_file:
        out_file.write(html_template)
    print(f"✅ Markdown converted and saved to: {html_output_path}")


# def download_pdf(url: str) -> str:
#     try:
#         os.makedirs("dpa_docs", exist_ok=True)
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"dpa_docs/document_{timestamp}.pdf"
#         wget.download(url, out=filename)
#         return filename
#     except Exception as e:
#         raise Exception(f"Failed to download PDF from {url}: {e}")
    
import requests

# def download_pdf(url: str) -> str:
#     os.makedirs("dpa_docs", exist_ok=True)
#     filename = os.path.basename(url.split("id=")[-1]) + ".pdf"
#     filepath = os.path.join("dpa_docs", filename)
#     print(filepath)

#     # If already downloaded, skip
#     if os.path.exists(filepath):
#         return filepath

#     # Stream download
#     with requests.get(url, stream=True) as r:
#         r.raise_for_status()
#         with open(filepath, 'wb') as f:
#             for chunk in r.iter_content(chunk_size=8192):
#                 f.write(chunk)

#     return filepath

def download_pdf(url: str) -> str:
    try:
        os.makedirs("dpa_docs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dpa_docs/document_{timestamp}.pdf"
        wget.download(url, out=filename)
        return filename
    except Exception as e:
        raise Exception(f"Failed to download PDF from {url}: {e}")

    
def extract_text_from_pdf(pdf_bytes_io: io.BytesIO) -> str:
    try:
        with pdfplumber.open(pdf_bytes_io) as pdf:
            texts = [page.extract_text() or "" for page in pdf.pages]
            return "\n".join(texts).strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text from PDF: {e}")

def get_client(mode: str):
    groq_api_key = None
    try:
        with open("groq_api_key.txt", "r") as f:
            groq_api_key = f.read().strip()
    except FileNotFoundError:
        pass

    if mode == "groq" and groq_api_key:
        return GroqClient(api_key=groq_api_key)
    else:
        # Use your custom API URL here
        API_URL = 'http://95.179.250.102:3333/api/chat'
        # If you have an API key for this, load it similarly
        custom_api_key = None
        try:
            with open("api_key.txt", "r") as f:
                custom_api_key = f.read().strip()
        except FileNotFoundError:
            pass
        return CustomAPIClient(api_url=API_URL, api_key=custom_api_key)



def save_report(content: str, directory: str = "./md") -> str:
    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(directory, f"compliance_report_{timestamp}.md")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Compliance Review Report\n\n")
        f.write(content)

    print(f"Report saved to: {filename}")
    return filename





def verify_signature(body: bytes, timestamp: str, slack_signature: str) -> bool:
    if timestamp is None or slack_signature is None:
        print("Skipping signature verification (no headers present)")
        return True  # Skip verification for local testing or curl
    if abs(time.time() - int(timestamp)) > 60 * 5:
        print("Request timestamp too old.")
        return False
    sig_basestring = f"v0:{timestamp}:{body.decode()}"
    my_signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode(), sig_basestring.encode(), hashlib.sha256
    ).hexdigest()
    is_valid = hmac.compare_digest(my_signature, slack_signature)
    if not is_valid:
        print(f"Invalid signature. Expected {my_signature} got {slack_signature}")
    return is_valid


async def send_message(channel: str, text: str):
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    json_data = {"channel": channel, "text": text}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=json_data)
        data = resp.json()
        print("Slack API response:", data)
        if not data.get("ok"):
            print("Failed to send message:", data.get("error"))


async def fetch_bot_user_id():
    global bot_user_id
    url = "https://slack.com/api/auth.test"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers)
        data = resp.json()
        if data.get("ok"):
            bot_user_id = data["user_id"]
            print(f"Bot user ID: {bot_user_id}")
        else:
            print("Failed to fetch bot user ID:", data)


# def beautify_output(text: str, client) -> str:
#     prompt = (
#         "Please take the following legal compliance audit report and reformat it to be clean, well-structured, "
#         "and suitable for sharing in a Slack message. Use clear sections, bold headings, and bullet points where appropriate.\n\n"
#         f"{text}"
#     )
#     return client.run_prompt(prompt)


# def beautify_output(text: str, client) -> str:
#     prompt = (
#         "Take the following legal compliance report and reformat it in a style that works best for Slack messages:\n"
#         "- Use *bold* for section headers\n"
#         "- Use bullet points (- or •) for lists\n"
#         "- Avoid large Markdown headers (like ### or ===)\n"
#         "- Avoid code blocks\n"
#         "- Ensure it's clean, readable, and Slack-compatible\n\n"
#         "Report:\n\n"
#         f"{text}"
#     )
#     return client.run_prompt(prompt)

# def beautify_output(text: str, client) -> str:
#     prompt = (
#         "Take the following legal compliance report and reformat it in a style perfect for Slack messages:\n"
#         "- Use *bold* for section headers\n"
#         "- Use bullet points (- or •) for lists\n"
#         "- Add relevant emojis for sections, statuses, and highlights (e.g., 📊, ✅, 🚩, 🔒, 📝)\n"
#         "- Avoid large Markdown headers (like ### or ===)\n"
#         "- Avoid code blocks\n"
#         "- Make it clean, readable, visually engaging, and Slack-compatible\n\n"
#         "Report:\n\n"
#         f"{text}"
#     )
#     return client.run_prompt(prompt)

def beautify_output(text: str, client) -> str:
    prompt = (
        "Take the following legal compliance report and reformat it perfectly for Slack messages:\n"
        "- Use *bold* for section headers (e.g. *Formal Article 28 Compliance*)\n"
        "- Use _italic_ sparingly for emphasis where appropriate\n"
        "- Remove redundant or nested markdown (e.g. replace '* **Text**' or '**_Text_**' with just '*Text*' or '_Text_')\n"
        "- Use bullet points (- or •) for lists\n"
        "- Add relevant emojis for sections, statuses, and highlights (e.g., 📊, ✅, 🚩, 🔒, 📝)\n"
        "- Avoid large markdown headers (### or ===) and code blocks\n"
        "- Ensure the text is clean, readable, visually engaging, and Slack-compatible\n\n"
        "Report:\n\n"
        f"{text}"
    )
    return client.run_prompt(prompt)
