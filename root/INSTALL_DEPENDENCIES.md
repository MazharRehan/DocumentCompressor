# Installing Required Dependencies

## Windows Installation Guide

### 1. Install Ghostscript (Required for PDF compression)

**Download:**
- Go to https://ghostscript.com/releases/gsdnld.html
- Download "Ghostscript 10.x for Windows (64 bit)" (latest version)
- File will be named something like `gs10xx_win64.exe`

**Install:**
1. Run the installer
2. **IMPORTANT:** During installation, check "Add to PATH" or manually add it
3. Default installation path: `C:\Program Files\gs\gs10.xx\bin`

**Verify Installation:**
```powershell
gs --version
```
Should show: `GPL Ghostscript 10.x.x`

**If `gs` command not found:**
Add to PATH manually:
1. Search "Environment Variables" in Windows Start
2. Click "Environment Variables"
3. Under "System variables", find "Path", click "Edit"
4. Click "New" and add: `C:\Program Files\gs\gs10.xx\bin` (replace xx with your version)
5. Click OK, restart PowerShell/terminal

---

### 2. Install ImageMagick (Required for PDF-to-image conversion)

**Download:**
- Go to https://imagemagick.org/script/download.php#windows
- Download "ImageMagick-x.x.x-Q16-x64-dll.exe" (dynamic version with Q16)

**Install:**
1. Run the installer
2. **IMPORTANT:** Check these options during installation:
   - ✅ Add application directory to your system path
   - ✅ Install legacy utilities (e.g., convert)
3. Complete installation

**Verify Installation:**
```powershell
magick --version
```
Should show: `Version: ImageMagick 7.x.x`

```powershell
convert --version
```
Should also work (legacy command)

**If `magick` command not found:**
Add to PATH manually:
1. Search "Environment Variables" in Windows Start
2. Click "Environment Variables"
3. Under "System variables", find "Path", click "Edit"
4. Click "New" and add: `C:\Program Files\ImageMagick-7.x.x-Q16-HDRI`
5. Click OK, restart PowerShell/terminal

---

## Quick Install Commands (for package managers)

### If you have Chocolatey:
```powershell
choco install ghostscript imagemagick -y
```

### If you have Scoop:
```powershell
scoop install ghostscript imagemagick
```

### If you have WinGet:
```powershell
winget install --id=Ghostscript.Ghostscript  -e
winget install --id=ImageMagick.ImageMagick  -e
```

---

## After Installation

**Restart your terminal/PowerShell**, then verify:

```powershell
gs --version
magick --version
```

Both should return version information without errors.

Then restart your Flask app:
```powershell
cd E:\Mazhar\DocumentCompresser\root
python app.py
```

---

## What Each Tool Does

- **Ghostscript (`gs`)**: 
  - Compresses PDFs
  - Converts PDFs to PDF/A format
  - Required for all PDF compression operations

- **ImageMagick (`magick`/`convert`)**: 
  - Converts PDF pages to images (JPG/PNG)
  - Required for PDF → Images conversion
  - Optional for image format conversions (Pillow handles most)

---

## Troubleshooting

### "gs is not recognized" error
- Ghostscript not in PATH
- Solution: Add `C:\Program Files\gs\gs10.xx\bin` to PATH (see above)
- Restart terminal after changing PATH

### "magick is not recognized" error
- ImageMagick not in PATH
- Solution: Add ImageMagick directory to PATH
- Restart terminal after changing PATH

### Still not working?
Run this in PowerShell to find where tools are installed:
```powershell
Get-Command gs -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
Get-Command magick -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
```

If nothing shows, the tool isn't installed or not in PATH.
