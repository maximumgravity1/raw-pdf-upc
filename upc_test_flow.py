import hashlib
from pathlib import Path
import subprocess, sys

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(1<<20), b''):
            h.update(chunk)
    return h.hexdigest()

# make dummy RAW
p = Path("dummy.RAW"); p.write_bytes(b'\x00\x11\x22\x33'*1024)
print(f"[STEP 1] Created {p.name} ({p.stat().st_size} bytes)")

# wrap
print("[STEP 2] Wrapping into PDF...")
subprocess.run([sys.executable, "wrap_binary_to_pdf.py", "dummy.RAW", "dummy_container.pdf"], check=True)

# extract
print("[STEP 3] Extracting from PDF...")
Path("recovered").mkdir(exist_ok=True)
subprocess.run([sys.executable, "extract_embedded_from_pdf.py", "dummy_container.pdf", "recovered"], check=True)

# verify
print("[STEP 4] Verification:")
o = sha256("dummy.RAW"); r = sha256("recovered/dummy.RAW")
print(" - Original :", o)
print(" - Recovered:", r)
print(" - MATCH ✅" if o == r else " - ❌ MISMATCH")
