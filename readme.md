
# 🕵️‍♂️ DPA Compliance Comparison Tool

This project is a legal compliance assistant built to **compare two Data Processing Agreements (DPAs)** or similar legal documents. It highlights deviations, missing clauses, added risks, and non-compliant language using LLMs like **Groq** or a **Custom LLaMa API backend**.

---

## 📁 Project Structure

```
.
├── main_server.py          # FastAPI backend for PDF comparison via API
├── main.py                 # CLI script for running comparisons locally
├── utils.py                # Utility functions (PDF, tokenization, styling, etc.)
├── llm_client.py           # LLM clients for Groq and Custom API
├── mcp_client.py           # Optional client for a document search/query API
├── prompts/                # Folder with prompt templates for specific checks
├── FINAL_REPORT.txt        # Final summarization template for merging prompt outputs
├── dpa_docs/               # Folder where downloaded PDFs are stored
├── md/                     # Folder for generated Markdown reports
├── requirements.txt        # Python dependencies
└── Dockerfile              # (Optional) Docker container setup
```

---

## ⚙️ Installation

1. **Clone the repository**

```bash
git clone https://github.com/alexanch/LegalNodesRAISE.git
cd LegalNodesRAISE
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up API keys**

Create these two files in the root directory:

- `groq_api_key.txt` — contains your Groq API key
- `api_key.txt` — contains your custom API key (if using custom mode)

---

## 🧪 How It Works

The system compares two documents (usually PDFs) using pre-written prompt templates and an LLM.

1. Each `.txt` prompt in the `prompts/` folder targets a specific compliance aspect.
2. The model generates responses for each prompt.
3. A final summarization prompt (`FINAL_REPORT.txt`) aggregates the results.
4. Output is saved as Markdown and converted to styled HTML.

---

## 🚀 Usage

### 🔧 Option 1: Command-line (CLI)

You must have two local PDF files (e.g., `dpa_dfb.pdf`, `dpa_oracle.pdf`) in the root directory.

```bash
python main.py groq
# or
python main.py custom
```

Reports will be saved under `md/` and as `report.html`.

---

### 🌐 Option 2: API Server

Start the FastAPI server:

```bash
uvicorn main_server:app --reload --port 8002
```

Send a POST request to `/compare`:

```json
POST /compare
Content-Type: application/json

{
  "pdf_url_1": "https://example.com/customer_dpa.pdf",
  "pdf_url_2": "https://example.com/vendor_dpa.pdf",
  "mode": "groq"  // or "custom"
}
```

Response:

```json
{
  "result": "Final audit output as plain text"
}
```

---

## 🧠 Prompt Design

Each prompt file in `prompts/` should contain a reusable instruction like:

```
Compare confidentiality clauses in both documents. Highlight missing, vague, or non-standard language in the vendor DPA.
```

The system fills the `{customer_doc}` and `{external_doc}` placeholders automatically.

---

## 📝 Output

- Reports are saved in `md/` with timestamps.
- HTML output is styled and saved as `report.html` for easy review.
- All outputs include a sectioned summary per prompt and a final executive summary.

---

## 🐳 Docker (optional)

```bash
docker build -t dpa-comparator .
docker run -p 8002:8002 dpa-comparator
```

---

## 📌 Notes

- Only `.txt` files in `prompts/` are used as inputs.
- Requires internet access for downloading PDFs.
- Large PDFs may exceed token limits — truncate if needed.


