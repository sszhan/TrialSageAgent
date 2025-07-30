#preprocess.py

import fitz
import os

raw_path = "data_raw_protocols"
processed_path = "data/processed_text/"

def extract_text_from_pdf(pdf_path):
    """Extracts text from a single PDF file"""

    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None
    
def main():
    """Loops through raw PDFS and saves extracted text."""

    if not os.path.exists(processed_path):
        os.makedirs(processed_path)

    for filename in os.listdir(raw_path):
        if filename.lower().endswith("pdf"):
            print(f"Processing {filename}...")
            pdf_path = os.path.join(raw_path, filename)
            text_content = extract_text_from_pdf(pdf_path)

            if text_content:
                base_name = os.path.splitext(filename)[0]
                output_filepath = os.path.join(processed_path, f"{base_name}.txt")
                with open(output_filepath, "w", encoding='utf-8') as f:
                    f.write(text_content)

    print("Preprocessing complete.")

if __name__ == "__main__":
    main()