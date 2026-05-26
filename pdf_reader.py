import re
import PyPDF2


def extract_text_from_pdf(file_path: str) -> str:
    """Extract and clean text from a PDF file."""
    text_parts = []
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception as e:
        return f"[PDF Error] {str(e)}"

    full_text = "\n".join(text_parts)
    full_text = re.sub(r'\n{3,}', '\n\n', full_text)
    full_text = re.sub(r'[ \t]+', ' ', full_text)
    return full_text.strip()