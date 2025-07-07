import os
import json
from datetime import datetime
import requests
from groq import Groq

def load_groq_api_key(filepath="groq_api_key.txt"):
    try:
        with open(filepath, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"❌ Groq API key file '{filepath}' not found.")
        return None

class GroqClient:
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = load_groq_api_key()
        if not api_key:
            raise ValueError("Groq API key is required.")
        self.client = Groq(api_key=api_key)

    def run_prompt(self, prompt, max_tokens=10000):
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a highly experienced legal compliance auditor."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content


class CustomAPIClient:
    def __init__(self, api_url, api_key=None):
        self.api_url = api_url
        self.headers = {'Content-Type': 'application/json'}
        if api_key:
            self.headers['Authorization'] = f"Bearer {api_key}"

    def run_prompt(self, prompt, max_tokens=10000):
        payload = {
            "model": "llama3.1:8b",
            "messages": [
                {"role": "system", "content": "You are a highly experienced legal compliance auditor."},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "max_tokens": max_tokens
        }

        response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload))
        if response.status_code == 200:
            result = response.json()
            return result.get('message', {}).get('content', 'No content returned.')
        else:
            raise RuntimeError(f"❌ API Error: {response.status_code}\n{response.text}")


# 🔧 Prompt builder function (can be moved to `prompts.py`)
# def build_comparison_prompt(customer_doc, external_doc):
#     return f"""
# You are a highly experienced compliance auditor and legal analyst.

# Your task is to perform a thorough comparison between two policy or agreement documents:
# 1. The **Customer Document** (internal, expected standard).
# 2. The **External Party Document** (submitted by a vendor, client, or third-party).

# Identify and highlight any:
# - Deviations or mismatches in language, commitments, or terms.
# - Missing clauses or critical language in the external document that are present in the customer document.
# - Additional or unauthorized clauses in the external document.
# - Risky or non-compliant language.
# - Any obligations that have been shifted unfairly.

# Provide your response as a clear, structured list of findings. Be precise, legalistic, and specific.

# --- CUSTOMER DOCUMENT START ---
# {customer_doc}
# --- CUSTOMER DOCUMENT END ---

# --- EXTERNAL PARTY DOCUMENT START ---
# {external_doc}
# --- EXTERNAL PARTY DOCUMENT END ---

# List the mismatches below with detailed explanation:
# """

def build_comparison_prompt(customer_doc, external_doc, prompt_path):
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            base_prompt = f.read().strip()
    except FileNotFoundError:
        raise ValueError(f"Prompt file not found: {prompt_path}")

    return (
        f"{base_prompt}\n\n"
        f"--- Customer DPA ---\n{customer_doc}\n\n"
        f"--- Vendor's DPA ---\n{external_doc}"
    )


# 📄 Save output to Markdown (can move to `reporting.py`)
def save_report(content, prefix="compliance_report"):
    os.makedirs("md", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"./md/{prefix}_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {prefix.replace('_', ' ').title()}\n\n")
        f.write(content)
    print(f"\n✅ Report saved as '{filename}'")
    return filename
