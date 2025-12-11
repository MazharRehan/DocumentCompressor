# How to Run Document Compressor Project

## Prerequisites

### 1. Install Python
- Download and install Python 3.10+ from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation

### 2. Install External Tools (Required for PDF/Image Processing)

#### **Windows (PowerShell - Run as Administrator):**

**Ghostscript (for PDF compression):**
```powershell
# Download and install Ghostscript
# Visit: https://ghostscript.com/releases/gsdnld.html
# Download: Ghostscript 10.x for Windows (64-bit)
# Install to default location (C:\Program Files\gs\)

# Verify installation:
gswin64c --version
or
gs --version
```

**ImageMagick (for image conversions and PDF to images):**
```powershell
# Download and install ImageMagick
# Visit: https://imagemagick.org/script/download.php#windows
# Download: ImageMagick-7.x.x-Q16-HDRI-x64-dll.exe
# During installation, check "Add application directory to system path"

# Verify installation:
magick --version
```

#### **If tools are not in PATH:**
After installing, manually add to PATH:
1. Search "Environment Variables" in Windows
2. Edit "System variables" → "Path"
3. Add:
   - `C:\Program Files\gs\gs10.xx.x\bin` (adjust version)
   - `C:\Program Files\ImageMagick-7.x.x-Q16-HDRI` (adjust version)
4. Restart PowerShell

---

## Quick Start (Windows PowerShell)

### Step 1: Navigate to Project
```powershell
cd E:\Mazhar\DocumentCompresser
```

### Step 2: Create Virtual Environment
```powershell
python -m venv .venv
```

### Step 3: Activate Virtual Environment
```powershell
.\.venv\Scripts\activate
```
You should see `(.venv)` prefix in your terminal.

### Step 4: Install Python Dependencies
```powershell
pip install -r .\root\requirements.txt
```

### Step 5: Setup Environment Variables (Optional)
```powershell
# Copy the example environment file
copy .\root\env.example .\root\.env

# Edit .env file to add your TinyPNG API key (optional for high-quality compression)
notepad .\root\.env
```

**To get Tinify API Key (optional):**
- Visit [tinypng.com/developers](https://tinypng.com/developers)
- Sign up for free (500 compressions/month)
- Copy your API key to `.env` file:
  ```
  TINIFY_API_KEY=your_actual_api_key_here
  ```

### Step 6: Run the Application
```powershell
cd .\root
python app.py
```

### Step 7: Open in Browser
- Open your browser and go to: **http://127.0.0.1:5000**
- You should see the compression/conversion interface

---

## Usage

### Compress Files
1. **Target Size Mode:**
   - Enter desired file size in KB (e.g., `100` for 100KB)
   - Drag & drop files
   - Click "Compress"

2. **Preset Mode:**
   - Choose preset: High/Medium/Low quality
   - Drag & drop files
   - Click "Compress"

3. **With Tinify (if API key configured):**
   - Check "Use Tinify" checkbox
   - Drag & drop files
   - Click "Compress"

### Convert Files
1. Select target format (JPG, PNG, WEBP, PDF, etc.)
2. Drag & drop files
3. Click "Convert"

### Supported Files
- **Images:** PNG, JPG, JPEG, WEBP
- **Documents:** PDF

### Download Results
- **Single file:** Downloads directly
- **Multiple files:** Downloads as ZIP

---

## Troubleshooting

### "gs is not recognized" or "magick is not recognized"
**Solution:** Ghostscript or ImageMagick not installed or not in PATH
- Verify installation: `gs --version` and `magick --version`
- Add to PATH (see Prerequisites section)
- Restart PowerShell

### "Import Error: No module named 'X'"
**Solution:** Virtual environment not activated or dependencies not installed
```powershell
.\.venv\Scripts\activate
pip install -r .\root\requirements.txt
```

### PDF compression fails
**Solution:** Ghostscript not properly installed
- Reinstall Ghostscript from official website
- Ensure `gs` command works in terminal

### PDF to Images fails
**Solution:** ImageMagick not properly installed or policy issue
- Reinstall ImageMagick
- If policy error occurs, edit ImageMagick policy file:
  - Location: `C:\Program Files\ImageMagick-7.x.x-Q16-HDRI\policy.xml`
  - Find line: `<policy domain="coder" rights="none" pattern="PDF" />`
  - Change to: `<policy domain="coder" rights="read|write" pattern="PDF" />`

### Port 5000 already in use
**Solution:** Change the port
```powershell
# Set PORT environment variable before running
$env:PORT=8080
python app.py
```

### Tinify not working
**Solution:** Check API key
- Verify your API key is correct in `.env` file
- Check you haven't exceeded monthly limit (500 free compressions)
- Tinify is optional; app works without it

---

## Stopping the Server

Press `Ctrl + C` in the terminal where Flask is running.

---

## Deactivate Virtual Environment

When you're done:
```powershell
deactivate
```

---

## Features

✅ **Image Compression:**
- Compress to exact target size (e.g., 100KB, 500KB, 1MB)
- Preset quality modes (High/Medium/Low)
- Optional Tinify integration for superior quality

✅ **PDF Compression:**
- Ghostscript presets (Printer/Ebook/Screen quality)
- Target size compression with iterative optimization
- Preserves PDF structure

✅ **Format Conversions:**
- PNG ↔ JPG
- JPEG → WEBP
- PDF → Images (extracts all pages as JPG)
- Images → PDF (combines multiple images into one PDF)
- PDF → PDF/A (archival format)

✅ **Batch Processing:**
- Upload multiple files at once
- Download as individual files or ZIP

✅ **100% Local:**
- All processing happens on your machine
- No file size limits (configurable)
- No privacy concerns

---

## Next Steps

### For GitHub
```powershell
git init
git add .
git commit -m "Initial commit - Local file compression tool"
git remote add origin https://github.com/yourusername/document-compressor.git
git push -u origin main
```

### For Docker (Optional)
See `Dockerfile.txt` in the root folder for containerization.

---

## File Structure
```
DocumentCompresser/
├── root/
│   ├── app.py              # Flask backend (main application)
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   ├── services/
│   │   ├── image_service.py  # Image compression/conversion logic
│   │   └── pdf_service.py    # PDF compression/conversion logic
│   ├── static/
│   │   └── app.js          # Frontend JavaScript (Dropzone integration)
│   └── templates/
│       └── index.html      # Web UI (Tailwind CSS)
├── .venv/                  # Virtual environment (created during setup)
└── SETUP.md               # This file
```

---

## Expanding the Project

The codebase is modular for easy expansion:

1. **Add new image formats:** Extend `services/image_service.py`
2. **Add new PDF operations:** Extend `services/pdf_service.py`
3. **Add new routes:** Add endpoints in `app.py`
4. **Add UI features:** Edit `templates/index.html` and `static/app.js`

---

## Support

For issues or questions:
1. Check Troubleshooting section above
2. Verify all prerequisites are installed
3. Check terminal output for error messages
