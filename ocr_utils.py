from PyPDF2 import PdfReader
import re

# 📄 Extract text from PDF
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()

    return text

# 🔍 Extract metadata
def extract_metadata(text):
    metadata = {}

    # Year கண்டுபிடிக்க
    year_match = re.search(r"\b(19|20)\d{2}\b", text)
    if year_match:
        metadata["year"] = year_match.group()

    # Title (first 200 chars)
    metadata["title"] = text[:200]

    return metadata

# ✅ Validation
def validate_text(text):
    return {
        "is_valid": len(text.strip()) > 50
    }