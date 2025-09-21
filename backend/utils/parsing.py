import pdfplumber
import docx2txt
from googletrans import Translator

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_path):
    return docx2txt.process(file_path)


translator = Translator()

def normalize_text(text: str) -> str:
    # Detect & translate Hindi → English
    try:
        detection = translator.detect(text)
        if detection.lang == "hi":  # Hindi
            text = translator.translate(text, src="hi", dest="en").text
    except Exception:
        pass  # fail gracefully
    return text

def extract_text_from_pdf(file_path):
    import pdfplumber
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return normalize_text(text)

def extract_text_from_docx(file_path):
    import docx2txt
    text = docx2txt.process(file_path)
    return normalize_text(text)