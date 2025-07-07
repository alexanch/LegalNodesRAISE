import sys
from utils import load_api_key
from llm_client import GroqClient, CustomAPIClient

try:
    groq_api_key = load_api_key("groq_api_key.txt")
    custom_api_key = load_api_key("api_key.txt")

except FileNotFoundError:
    pass



customer_doc = """
Data Handling Policy – Internal Standard

All third-party vendors must encrypt customer data both at rest and in transit using AES-256 encryption.
Vendors are prohibited from sharing customer data with any subcontractors without prior written approval.
All data must be stored within the geographic boundaries of the EU in compliance with GDPR.
Access to sensitive information must be restricted to authorized personnel only, with two-factor authentication enforced.
A quarterly audit must be performed and results shared with the compliance team.
"""

external_doc = """
Third-Party Data Management Policy

Customer data should be encrypted during transfer. Rest encryption is encouraged but not mandatory.
Subcontractors may be used to manage customer data, provided they adhere to equivalent standards.
Data may be stored in any region with appropriate privacy controls.
Authorized team members may access the data, but two-factor authentication is not mandatory.
Audits will be conducted annually and provided upon request.
"""


def main():
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "groq"

    if mode == "groq":
        print("Using Groq API:")
        client = GroqClient(api_key=groq_api_key)
    else:
        print("Using Custom API:")
        API_URL = 'http://95.179.250.102:3333/api/chat'
        client = CustomAPIClient(api_url=API_URL)

    client.compare_documents(customer_doc, external_doc)

if __name__ == "__main__":
    main()
