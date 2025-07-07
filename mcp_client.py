import requests

class MCPClient:
    def __init__(self, api_key: str, base_url: str = "http://217.69.0.109:3000/mcp"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def upload_document(self, url, document_name, document_type="pdf", context=""):
        payload = {
            "document_url": url,
            "document_name": document_name,
            "document_type": document_type,
            "context": context
        }
        resp = requests.post(f"{self.base_url}/uploadDocument", json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()["result"]["document_id"]

    def query_document(self, document_id, query_text):
        payload = {
            "document_id": document_id,
            "query": query_text
        }
        resp = requests.post(f"{self.base_url}/query-document", json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()["result"]["result"]

    def get_full_document_text(self, document_id):
        # Generic query to get full text
        query = "Please provide the full text of the document."
        return self.query_document(document_id, query)
