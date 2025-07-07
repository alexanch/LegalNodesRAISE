import io
import pdfplumber
from transformers import AutoTokenizer
from fastapi import HTTPException

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

import os
from datetime import datetime

def save_report(content: str, directory: str = "./md") -> str:
    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(directory, f"compliance_report_{timestamp}.md")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Compliance Review Report\n\n")
        f.write(content)

    print(f"Report saved to: {filename}")
    return filename