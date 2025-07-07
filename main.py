import sys
import os


from utils import (
    load_api_key,
    extract_text_from_pdf,
    count_tokens_with_transformers,
    convert_markdown_to_styled_html
)
from llm_client import (
    GroqClient,
    CustomAPIClient,
    build_comparison_prompt,
    save_report
)

# Load API keys
groq_api_key = load_api_key("groq_api_key.txt")
custom_api_key = load_api_key("api_key.txt")

# Load and extract PDFs
customer_doc = extract_text_from_pdf('dpa_dfb.pdf')
external_doc = extract_text_from_pdf('dpa_oracle.pdf')

# Print token counts
print(f"Customer doc tokens: {count_tokens_with_transformers(customer_doc)}")
print(f"External doc tokens: {count_tokens_with_transformers(external_doc)}")

def main():
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "groq"

    # Initialize client
    if mode == "groq":
        print("Using Groq API:")
        client = GroqClient(api_key=groq_api_key)
    else:
        print("Using Custom API:")
        API_URL = 'http://95.179.250.102:3333/api/chat'
        client = CustomAPIClient(api_url=API_URL, api_key=custom_api_key)

    # Step 1: Process all prompts in the 'prompt' folder
    combined_output = ""

    prompt_dir = "prompts"
    for filename in os.listdir(prompt_dir):
        if filename.endswith(".txt"):
            prompt_path = os.path.join(prompt_dir, filename)
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt = f.read()
            
            print(f"Running prompt from {filename}...")
            output = client.run_prompt(prompt)
            combined_output += f"\n=== Output for {filename} ===\n{output}\n"

    # Step 2: Load final prompt and append combined_output
    with open("FINAL_REPORT.txt", "r", encoding="utf-8") as f:
        final_prompt = f.read()

    full_prompt = f"{final_prompt}\n\n=== Combined Outputs ===\n{combined_output}"

    # Step 3: Run final combined prompt
    print("Running final prompt...")
    final_output = client.run_prompt(full_prompt)

    # Step 4: Save the final report
    save_report(final_output)
    convert_markdown_to_styled_html(final_output)

if __name__ == "__main__":
    main()
