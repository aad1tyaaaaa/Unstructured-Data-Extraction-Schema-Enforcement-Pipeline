import argparse
import json
from dotenv import load_dotenv

from document_processor import extract_text_from_pdf
from extraction_pipeline import extract_invoice_data

def main():
    parser = argparse.ArgumentParser(description="Extract structured data from a PDF invoice.")
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file.")
    parser.add_argument("--use-textract", action="store_true", help="Try to use AWS Textract instead of local extraction.")
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Step 1: Extract Text
    print(f"Step 1: Extracting text from {args.pdf_path}")
    extracted_text = extract_text_from_pdf(args.pdf_path, use_textract=args.use_textract)
    
    if not extracted_text.strip():
        print("Error: Extracted text is empty. Could not read the PDF.")
        return

    # Step 2: Extract Structured Data
    print("\nStep 2: Sending to LLM for Schema Enforcement...")
    try:
        invoice = extract_invoice_data(extracted_text)
    except Exception as e:
        print(f"Failed to extract structured data: {e}")
        return

    # Step 3: Output Results
    print("\n=== EXTRACTION SUCCESS ===")
    print(invoice.model_dump_json(indent=2))
    
    # Optionally write to a file
    out_path = args.pdf_path + ".json"
    with open(out_path, "w") as f:
        f.write(invoice.model_dump_json(indent=2))
    print(f"\nSaved JSON result to {out_path}")

if __name__ == "__main__":
    main()
