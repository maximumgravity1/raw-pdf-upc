# extract_embedded_from_pdf.py
import sys, os
from pypdf import PdfReader

def main(pdf_path, out_dir="."):
    reader = PdfReader(pdf_path)
    root = reader.trailer["/Root"]

    # Ensure output dir exists
    os.makedirs(out_dir, exist_ok=True)

    # Embedded files live under the standard Names/EmbeddedFiles tree
    names = root.get("/Names")
    if not names or "/EmbeddedFiles" not in names:
        print("No embedded files found.")
        return

    ef_tree = names["/EmbeddedFiles"]["/Names"]
    if not ef_tree:
        print("No embedded files found.")
        return

    for i in range(0, len(ef_tree), 2):
        display_name = str(ef_tree[i])
        file_spec = ef_tree[i + 1].get_object()
        filename = file_spec.get("/F", display_name)
        embedded = file_spec["/EF"]["/F"].get_object()
        data = embedded.get_data()  # raw bytes

        out_path = os.path.join(out_dir, filename)
        with open(out_path, "wb") as f:
            f.write(data)
        print(f"Extracted: {out_path}")

if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print("Usage: python extract_embedded_from_pdf.py container.pdf [out_dir]")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else ".")
