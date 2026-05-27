import os
import instructor
from openai import OpenAI
from schema_models import Invoice
from pydantic import ValidationError

def get_instructor_client():
    """
    Initializes the OpenAI client and patches it with Instructor.
    Expects OPENAI_API_KEY environment variable.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")
    
    # Patch the OpenAI client to add the `response_model` argument.
    client = instructor.from_openai(OpenAI(api_key=api_key))
    return client

def extract_invoice_data(text: str, max_retries: int = 3) -> Invoice:
    """
    Given the unstructured text of an invoice, use an LLM via Instructor to 
    extract the data into the structured `Invoice` Pydantic model.
    """
    client = get_instructor_client()
    
    print(f"Extracting structured data from {len(text)} characters of text...")
    
    try:
        invoice: Invoice = client.chat.completions.create(
            model="gpt-4o-mini", # or gpt-4o, depending on complexity
            response_model=Invoice,
            max_retries=max_retries,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict, highly accurate document extraction system. "
                        "Your job is to read unstructured text from invoices and perfectly map "
                        "the data into the requested JSON schema. If numbers like tax and subtotal "
                        "do not match the total_amount, try to find the correct figures from the text."
                    )
                },
                {
                    "role": "user",
                    "content": f"Extract the invoice data from the following text:\n\n{text}"
                }
            ]
        )
        return invoice
    except Exception as e:
        print(f"Extraction failed after {max_retries} retries.")
        raise e
