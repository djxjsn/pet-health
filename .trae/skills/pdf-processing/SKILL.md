---
name: pdf-processing
description: Provides comprehensive PDF manipulation including text extraction, table extraction, document creation, merging/splitting, and form handling. Use when the user needs to work with PDF documents.
---

# PDF Processing

This skill provides comprehensive PDF manipulation capabilities, allowing Claude to work with PDF documents for various tasks.

## When to Use This Skill

Use this skill when the user:
- Needs to extract text from PDF documents
- Wants to extract tables from PDF files
- Needs to create new PDF documents
- Wants to merge or split PDF files
- Needs to work with PDF forms
- Asks about PDF manipulation or processing

## Core Capabilities

- **Text Extraction**: Extract text content from PDF documents
- **Table Extraction**: Identify and extract tables from PDF files
- **Document Creation**: Create new PDF documents from scratch
- **PDF Merging**: Combine multiple PDF files into one
- **PDF Splitting**: Split a single PDF into multiple files
- **Form Handling**: Process both fillable and non-fillable PDF forms
- **Document Analysis**: Analyze PDF document structure and metadata

## Supported Libraries

This skill leverages several PDF processing libraries:
- **pypdf**: For basic PDF operations
- **pdfplumber**: For advanced text and table extraction
- **reportlab**: For creating new PDF documents
- **qpdf**: For low-level PDF manipulation
- **pdftotext**: For text extraction

## Usage Examples

### Example 1: Extracting text
```python
from pdf_processing import extract_text

text = extract_text('document.pdf')
print(text)
```

### Example 2: Extracting tables
```python
from pdf_processing import extract_tables

tables = extract_tables('document.pdf')
for i, table in enumerate(tables):
    print(f"Table {i+1}:")
    print(table)
```

### Example 3: Merging PDFs
```python
from pdf_processing import merge_pdfs

pdfs = ['file1.pdf', 'file2.pdf', 'file3.pdf']
merge_pdfs(pdfs, 'merged.pdf')
```

### Example 4: Creating a PDF
```python
from pdf_processing import create_pdf

content = "Hello, this is a test PDF."
create_pdf(content, 'output.pdf')
```

## Form Handling

The skill supports two types of PDF forms:
1. **Fillable Forms**: PDF forms with interactive fields
2. **Non-fillable Forms**: Scanned documents or PDFs without interactive fields

For fillable forms, you can:
- Read form field values
- Set form field values
- Flatten forms

## Installation

To install the required dependencies:
```bash
pip install pypdf pdfplumber reportlab
# For qpdf and pdftotext (system-level)
# On Ubuntu/Debian: apt install qpdf poppler-utils
# On macOS: brew install qpdf poppler
# On Windows: Download from official websites
```

## Best Practices

- For large PDF files, use incremental processing to avoid memory issues
- When extracting tables, validate the extracted data
- For form processing, always test with sample forms
- Respect copyright and usage rights when processing PDF documents
- Use appropriate error handling for corrupted or password-protected PDFs
