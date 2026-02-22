import sys
import subprocess

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import pypdf
except ImportError:
    print("Installing pypdf...")
    install("pypdf")
    import pypdf

try:
    reader = pypdf.PdfReader("c:/Projects/tournees/projet_FM.pdf")
    text = ""
    for i, page in enumerate(reader.pages):
        text += f"--- Page {i+1} ---\n"
        text += page.extract_text() + "\n"
    with open("c:/Projects/tournees/pdf_content.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("PDF content written to pdf_content.txt")
except Exception as e:
    print(f"Error reading PDF: {e}")

