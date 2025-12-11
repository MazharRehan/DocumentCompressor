# Local File Compression & Conversion Toolkit

A minimal Flask-based web app to compress and convert images and PDFs:
- Image compression: target-size (e.g., 100KB), presets (high/medium/low), Tinify optional
- PDF compression: Ghostscript presets + target-size via binary search
- Format conversions: PNG↔JPG, JPEG→WEBP, PDF↔images, Images→PDF, PDF→PDF/A (optional)
- Batch uploads, download per file or as ZIP
- Simple Tailwind + Dropzone frontend

## Features
- Compress images to exact target size (KB/MB) using Pillow (quality/resize + binary search)
- High-quality image compression via Tinify (TinyPNG) if `TINIFY_API_KEY` is set
- PDF compression via Ghostscript (`screen`, `ebook`, `printer`) and target-size binary search
- Conversions:
  - PNG → JPG, JPG → PNG, JPEG → WEBP
  - PDF → images, Images → PDF
  - PDF → PDF/A
  - DOCX → PDF (optional with headless LibreOffice)
- Multiple file upload, zip download

## Quick Start

### Prerequisites
- Python 3.10+
- Ghostscript (`gs`) and ImageMagick (`magick` or `convert`) installed on PATH
- Optional: LibreOffice (`soffice`) for DOCX→PDF; Tinify API Key

macOS:
```bash
brew install ghostscript imagemagick
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Ubuntu/Debian:
```bash
sudo apt-get update && sudo apt-get install -y ghostscript imagemagick libreoffice
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Windows:
- Install Ghostscript and ImageMagick; ensure they’re in PATH.
- Use `python -m venv .venv && .venv\Scripts\activate` then `pip install -r requirements.txt`.

### Environment
Copy `.env.example` to `.env` and fill optional Tinify API key:
```
TINIFY_API_KEY=YOUR_TINYPNG_API_KEY
```

### Run
```bash
flask --app app.py run
# or
python app.py
```
Open http://127.0.0.1:5000

### Docker (optional)
```bash
docker build -t local-compress .
docker run -p 5000:5000 --env TINIFY_API_KEY=YOUR_KEY local-compress
```

## Usage
- Drag-and-drop files, choose compression or conversion options.
- Download processed files individually or as ZIP.

## Extending
- Add new operations in `services/image_service.py` or `services/pdf_service.py`.
- Register endpoints in `app.py`—each operation returns file bytes + metadata.
- Frontend actions live in `static/app.js`.

## Notes
- Target-size compression uses binary search over quality and optional downscale; exact sizes are best-effort.
- For PDFs, Ghostscript presets are fast; target-size uses iterative recompress.
- ImageMagick is used for format conversions; Pillow handles in-Python compression.

## License
MIT