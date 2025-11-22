import pypdf
import sys

def extract_text(pdf_path):
    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    pdf_path = "Ryan Coble-Neal Thesis Final (1).pdf"
    with open("thesis_text.txt", "w", encoding="utf-8") as f:
        f.write(extract_text(pdf_path))
    print("Extraction complete. Saved to thesis_text.txt")
