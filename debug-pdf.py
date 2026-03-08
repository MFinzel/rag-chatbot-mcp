import fitz  # PyMuPDF
from pathlib import Path

DATA_PATH = "data"

pdf_files = list(Path(DATA_PATH).glob("*.pdf"))

print(f"{len(pdf_files)} PDFs gefunden\n")

for pdf_file in pdf_files:
    print("=" * 80)
    print(f"Datei: {pdf_file.name}")

    try:
        doc = fitz.open(pdf_file)
        print(f"Seiten: {len(doc)}")

        total_text = ""

        for page_number, page in enumerate(doc):
            text = page.get_text()
            total_text += text

            print(f"\n--- Seite {page_number+1} ---")
            print(f"Zeichen extrahiert: {len(text)}")

            # ersten Teil anzeigen
            preview = text[:500].replace("\n", " ")
            print(f"Preview: {preview}")

        print("\nGesamter extrahierter Text:")
        print(total_text[:1000])

    except Exception as e:
        print(f"Fehler beim Lesen: {e}")

print("\nFertig.")