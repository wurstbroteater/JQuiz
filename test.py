from pypdf import PdfReader

reader = PdfReader("example.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

