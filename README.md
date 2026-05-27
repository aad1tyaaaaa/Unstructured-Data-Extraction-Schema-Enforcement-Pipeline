# Unstructured Data Extraction & Schema Enforcement Pipeline

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Pydantic](https://img.shields.io/badge/pydantic-v2-green)
![Instructor](https://img.shields.io/badge/instructor-LLM_Extraction-orange)

A robust, production-ready pipeline designed to parse complex, multi-page PDFs (such as financial invoices, medical records, or legal documents) and guarantee that the extracted data strictly adheres to a predefined JSON schema.

Instead of relying on basic LLM prompting which is prone to structural hallucinations, this project leverages **Instructor** and **Pydantic** to enforce schemas programmatically. If the Large Language Model (LLM) hallucinates or fails a validation check (e.g., math doesn't add up), the pipeline automatically catches the error and re-prompts the model with the specific validation failure to correct itself.

## 🌟 Key Features

- **Schema Guarantee**: Uses Pydantic to enforce strict data types, descriptions, and logical validations (e.g., verifying that `subtotal + tax == total`).
- **Auto-Retry & Self-Correction**: Integrates the `instructor` library to automatically handle retry logic when the LLM fails to meet a schema requirement.
- **Hybrid PDF Extraction**: 
  - **AWS Textract**: Native integration via `boto3` for highly complex documents containing nested tables and forms.
  - **Local Fallback**: Gracefully falls back to `PyMuPDF` for fast, local text extraction if AWS credentials aren't provided.
- **LLM Agnostic**: Currently configured for OpenAI (`gpt-4o-mini`), but easily adaptable for Anthropic or Gemini using the Instructor library.

## 📁 Project Structure

```text
.
├── document_processor.py   # Handles PDF text extraction (AWS Textract & PyMuPDF)
├── extraction_pipeline.py  # Core LLM interaction wrapped with Instructor
├── main.py                 # CLI entry point for processing real PDFs
├── schema_models.py        # Pydantic models defining the strict JSON schema
├── test_extraction.py      # Dummy OCR test script demonstrating retry logic
├── requirements.txt        # Project dependencies
└── .env.example            # Template for required environment variables
```

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- An OpenAI API Key (or Anthropic API key if you switch the client)
- *(Optional)* AWS Credentials for Amazon Textract

### 2. Installation

Clone the repository and install the required dependencies. It is recommended to use a virtual environment.

```bash
# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the root directory based on the provided example:

```bash
cp .env.example .env
```

Populate the `.env` file with your credentials:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional: For AWS Textract support
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
```

## 💻 Usage

### Running the Test Script (Recommended First Step)
To understand how the auto-retry logic works, run the included test script. This script feeds intentionally messy OCR data with bad math to the pipeline. You will see the pipeline catch the validation error and force the LLM to find the correct figures.

```bash
python test_extraction.py
```

### Processing a Real PDF
To run the extraction pipeline against a local PDF file, use `main.py`:

```bash
python main.py "path/to/your/document.pdf"
```

**Using AWS Textract:**
If you have configured your AWS credentials and want to extract tables/forms with high fidelity, pass the `--use-textract` flag:

```bash
python main.py "path/to/your/document.pdf" --use-textract
```

The resulting validated JSON will be printed to the console and saved alongside your original PDF file.

## 🛠️ Modifying the Schema

To adapt this pipeline for a different type of document (e.g., Medical Records instead of Invoices):
1. Open `schema_models.py`.
2. Define your new Pydantic classes with detailed `Field(description="...")` tags.
3. Add `@field_validator` methods to enforce logical relationships between extracted fields.
4. Update `extraction_pipeline.py` to use your new Pydantic model as the `response_model`.
