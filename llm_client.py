import os
import json
from datetime import datetime
import requests
from groq import Groq

# Prompt template moved outside
COMPLIANCE_PROMPT_TEMPLATE = """
You are a highly experienced compliance auditor and legal analyst.

Your task is to perform a thorough comparison between two policy or agreement documents:
1. The **Customer Document** (internal, expected standard).
2. The **External Party Document** (submitted by a vendor, client, or third-party).

Identify and highlight any:
- Deviations or mismatches in language, commitments, or terms.
- Missing clauses or critical language in the external document that are present in the customer document.
- Additional or unauthorized clauses in the external document.
- Risky or non-compliant language.
- Any obligations that have been shifted unfairly.

Provide your response as a clear, structured list of findings. Be precise, legalistic, and specific.

--- CUSTOMER DOCUMENT START ---
{customer_doc}
--- CUSTOMER DOCUMENT END ---

--- EXTERNAL PARTY DOCUMENT START ---
{external_doc}
--- EXTERNAL PARTY DOCUMENT END ---

List the mismatches below with detailed explanation:
"""

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

    def compare_documents(self, customer_doc, external_doc, max_tokens=1024):
        prompt = COMPLIANCE_PROMPT_TEMPLATE.format(customer_doc=customer_doc, external_doc=external_doc)
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a highly experienced legal compliance auditor."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
        )
        report = response.choices[0].message.content
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"./md/compliance_report_{timestamp}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("# Compliance Review Report\n\n")
            f.write(report)
        print(f"\n✅ Report saved as '{filename}'")
        return report, filename

class CustomAPIClient:
    def __init__(self, api_url, api_key=None):
        self.api_url = api_url
        self.headers = {'Content-Type': 'application/json'}
        if api_key:
            self.headers['Authorization'] = f"Bearer {api_key}"

    def compare_documents(self, customer_doc, external_doc, max_tokens=1024):
        prompt = COMPLIANCE_PROMPT_TEMPLATE.format(customer_doc=customer_doc, external_doc=external_doc)
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
            try:
                report = result.get('message', {}).get('content', 'No content returned.')
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"./md/compliance_report_{timestamp}.md"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("# Compliance Review Report\n\n")
                    f.write(report)
                print(f"\n✅ Report saved as '{filename}'")
                return report, filename
            except Exception as e:
                print("❌ Error extracting or saving report:", e)
                return None, None
        else:
            print(f"❌ API Error: {response.status_code}\n{response.text}")
            return None, None
