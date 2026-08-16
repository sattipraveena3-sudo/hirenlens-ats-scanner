from io import BytesIO

from pypdf import PdfReader


def extract_pdf_text(data: bytes) -> str:
    reader = PdfReader(BytesIO(data))
    text = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    if not text:
        raise ValueError("No extractable text found in PDF. Use a text-based PDF or paste the resume text.")
    return text
