import os
import sys
import wget
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from utils import (
    load_api_key,
    extract_text_from_pdf,
    count_tokens_with_transformers,
    convert_markdown_to_styled_html,
    save_report
)
from llm_client import (
    GroqClient,
    CustomAPIClient
)

# ==== FastAPI setup ====
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# ==== Request Schema ====
class CompareRequest(BaseModel):
    pdf_url_1: str
    pdf_url_2: str
    mode: str = "groq"

# ==== Download Utility ====
def download_pdf(url: str) -> str:
    os.makedirs("dpa_docs", exist_ok=True)
    filename = os.path.join("dpa_docs", os.path.basename(url).split("?")[0] + ".pdf")
    filepath = wget.download(url, out=filename)
    return filepath

# ==== Core processing logic reused ====
def process_comparison(customer_doc: str, external_doc: str, client) -> str:
    combined_output = ""
    prompt_dir = "prompts"
    for filename in os.listdir(prompt_dir):
        if filename.endswith(".txt"):
            prompt_path = os.path.join(prompt_dir, filename)
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt = f.read()

            print(f"Running prompt from {filename}...")
            prompt_filled = prompt.format(customer_doc=customer_doc, external_doc=external_doc)
            output = client.run_prompt(prompt_filled)
            combined_output += f"\n=== Output for {filename} ===\n{output}\n"

    # Final report prompt
    with open("FINAL_REPORT.txt", "r", encoding="utf-8") as f:
        final_prompt = f.read()

    full_prompt = f"{final_prompt}\n\n=== Combined Outputs ===\n{combined_output}"
    print("Running final prompt...")
    final_output = client.run_prompt(full_prompt)

    save_report(final_output)
    convert_markdown_to_styled_html(final_output)

    return final_output

# ==== FastAPI route ====
@app.post("/compare")
async def compare(request: CompareRequest):
    try:
        print("Downloading PDFs...")
        pdf1_path = download_pdf(request.pdf_url_1)
        pdf2_path = download_pdf(request.pdf_url_2)

        print("Extracting text...")
        customer_doc = extract_text_from_pdf(pdf1_path)
        external_doc = extract_text_from_pdf(pdf2_path)

        print("Customer tokens:", count_tokens_with_transformers(customer_doc))
        print("External tokens:", count_tokens_with_transformers(external_doc))

        if request.mode == "groq":
            groq_api_key = load_api_key("groq_api_key.txt")
            client = GroqClient(api_key=groq_api_key)
        else:
            custom_api_key = load_api_key("api_key.txt")
            API_URL = 'http://95.179.250.102:3333/api/chat'
            client = CustomAPIClient(api_url=API_URL, api_key=custom_api_key)

        final_output = process_comparison(customer_doc, external_doc, client)
        return {"result": final_output}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==== CLI Entry point (optional) ====
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_server:app", host="0.0.0.0", port=8002, reload=True)
