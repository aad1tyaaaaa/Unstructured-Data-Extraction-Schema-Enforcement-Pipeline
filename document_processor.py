import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def extract_text_from_pdf(file_path: str, use_textract: bool = False) -> str:
    """
    Extracts text from a local PDF file. 
    If use_textract is True, tries to use AWS Textract.
    Otherwise, uses PyMuPDF for local extraction.
    """
    if use_textract:
        try:
            return _extract_text_textract(file_path)
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(f"AWS credentials not found: {e}. Falling back to local extraction.")
            return _extract_text_local(file_path)
        except Exception as e:
            print(f"Error using AWS Textract: {e}. Falling back to local extraction.")
            return _extract_text_local(file_path)
    else:
        return _extract_text_local(file_path)

def _extract_text_local(file_path: str) -> str:
    """Uses PyMuPDF to extract text locally."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF is not installed. Please install it using `pip install PyMuPDF`.")

    print(f"Extracting text locally from {file_path} using PyMuPDF...")
    doc = fitz.open(file_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text("text") + "\n"
    
    return text

def _extract_text_textract(file_path: str) -> str:
    """Uses AWS Textract to extract text locally by uploading bytes."""
    print(f"Extracting text from {file_path} using AWS Textract...")
    
    textract = boto3.client('textract')
    
    with open(file_path, 'rb') as document:
        imageBytes = bytearray(document.read())

    # Call Amazon Textract
    # Note: AnalyzeDocument is best for invoices, but DetectDocumentText is simpler for raw text.
    # We will use AnalyzeDocument with 'FORMS' to ensure we capture table/form relationships well.
    response = textract.analyze_document(
        Document={'Bytes': imageBytes},
        FeatureTypes=["TABLES", "FORMS"]
    )
    
    # Simple assembly of the lines detected.
    # Textract provides richer JSON; here we just grab the raw text blocks for the LLM.
    extracted_text = ""
    for item in response.get("Blocks", []):
        if item["BlockType"] == "LINE":
            extracted_text += item.get("Text", "") + "\n"
            
    return extracted_text
