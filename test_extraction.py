import os
from dotenv import load_dotenv
from extraction_pipeline import extract_invoice_data

def run_test():
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Skipping test: OPENAI_API_KEY not set.")
        return

    # This is a messy OCR string with an intentional math error to trigger Pydantic validation
    # Notice: 2 hrs @ 150 = 300, 5 parts @ 20 = 100. Subtotal should be 400. Tax is 40. Total should be 440.
    # We purposefully make it messy so the LLM has to figure out what went where, and we
    # set the total to 440 but say "Subtotl: 400"
    
    dummy_ocr_text = """
    INVOICE # INV-2023-001
    Date: October 14th, 2023
    
    FROM:
    Tech Solutions LLC
    123 Main St, Techville, TX 75001
    
    TO:
    Globex Corporation
    999 Business Pkwy, Metropolis, NY 10001
    
    Description Qty UnitPrice Amount
    Consulting Services 2.0 150.00 300.00
    Server Parts 5.0 20.00 100.00
    
    Subtotl: 400.00
    Tax (10%): 40.00
    Amount Due: 440.00
    """

    print("Running Extraction Pipeline Test...")
    print("-" * 40)
    
    try:
        invoice = extract_invoice_data(dummy_ocr_text)
        print("\nTest passed! Extraction successful and validated.")
        print(invoice.model_dump_json(indent=2))
    except Exception as e:
        print("\nTest failed!")
        print(e)

if __name__ == "__main__":
    run_test()
