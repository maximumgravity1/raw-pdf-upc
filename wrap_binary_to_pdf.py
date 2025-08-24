import sys, json, hashlib, datetime, os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from pypdf import PdfReader, PdfWriter

def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1<<20), b''):
            h.update(chunk)
    return h.hexdigest()

def make_manifest_pdf(tmp_pdf_path, meta):
    c = canvas.Canvas(tmp_pdf_path, pagesize=LETTER)
    text = c.beginText(50, 720)
    text.textLine("Universal PDF Container — Manifest")
    text.textLine("")
    for k, v in meta.items():
        text.textLine(f"{k}: {v}")
    c.drawText(text)
    c.showPage()
    c.save()

def main(inp, outp):
    st = os.stat(inp)
    meta = {
        "filename": os.path.basename(inp),
        "bytes": st.st_size,
        "sha256": sha256(inp),
        "created": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "mime_hint": "application/octet-stream",
    }

    # 1) Create the one-page manifest PDF
    tmp = outp + ".manifest.pdf"
    make_manifest_pdf(tmp, meta)

    # 2) Reopen with pypdf and attach original + sidecar JSON
    reader = PdfReader(tmp)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    # attach original binary (from file path)
    with open(inp, "rb") as f:
        writer.add_attachment(os.path.basename(inp), f.read())

    # attach sidecar JSON (from bytes)
    sidecar_bytes = json.dumps(meta, indent=2).encode("utf-8")
    writer.add_attachment("manifest.json", sidecar_bytes)

    with open(outp, "wb") as f:
        writer.write(f)

    os.remove(tmp)

    print(
        f"Created {outp}\n"
        f"- embedded: {meta['filename']} ({meta['bytes']} bytes)\n"
        f"- sha256: {meta['sha256']}"
    )

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python wrap_binary_to_pdf.py input.bin output.pdf")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
