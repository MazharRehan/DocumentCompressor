import io
import os
import zipfile
from datetime import datetime
from flask import Flask, request, send_file, render_template, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from services.image_service import (
    compress_image_to_target, compress_image_preset, convert_image_format
)
from services.pdf_service import (
    compress_pdf_preset, compress_pdf_to_target, pdf_to_images, images_to_pdf, pdf_to_pdfa
)

load_dotenv()
TINIFY_API_KEY = os.getenv("TINIFY_API_KEY")

def check_dependencies():
    """Check if required external tools are available"""
    import shutil
    import platform
    missing = []
    # Check for Ghostscript (Windows uses gswin64c, Unix uses gs)
    gs_cmd = 'gswin64c' if platform.system() == 'Windows' else 'gs'
    if not shutil.which(gs_cmd) and not shutil.which('gs'):
        missing.append('Ghostscript (gswin64c or gs)')
    if not shutil.which('magick') and not shutil.which('convert'):
        missing.append('ImageMagick (magick or convert)')
    return missing

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB
ALLOWED_EXT = {'.png', '.jpg', '.jpeg', '.webp', '.pdf'}

def ext_of(filename):
    return os.path.splitext(filename.lower())[1]

@app.route("/", methods=["GET"])
def index():
    missing_deps = check_dependencies()
    return render_template(
        "index.html", 
        tinify_enabled=bool(TINIFY_API_KEY),
        missing_deps=missing_deps
    )

@app.route("/check-dependencies", methods=["GET"])
def check_deps():
    missing = check_dependencies()
    return jsonify({"missing": missing, "ready": len(missing) == 0})

@app.route("/compress", methods=["POST"])
def compress():
    target_kb = request.form.get("target_kb", type=int)
    preset = request.form.get("preset")  # "high" | "medium" | "low"
    use_tinify = bool(request.form.get("use_tinify", type=int))
    files = request.files.getlist("files")

    outputs = []
    for f in files:
        name = secure_filename(f.filename)
        ext = ext_of(name)
        if ext not in ALLOWED_EXT:
            outputs.append({"name": name, "error": "Unsupported file type"})
            continue
        data = f.read()
        try:
            if ext in {'.png', '.jpg', '.jpeg', '.webp'}:
                if target_kb:
                    out_bytes, out_ext = compress_image_to_target(data, ext, target_kb, use_tinify, TINIFY_API_KEY)
                else:
                    out_bytes, out_ext = compress_image_preset(data, ext, preset or "medium", use_tinify, TINIFY_API_KEY)
                outputs.append({"name": os.path.splitext(name)[0] + out_ext, "bytes": out_bytes})
            elif ext == '.pdf':
                import shutil
                import platform
                gs_cmd = 'gswin64c' if platform.system() == 'Windows' else 'gs'
                if not shutil.which(gs_cmd) and not shutil.which('gs'):
                    raise Exception(f"Ghostscript not found. Please install Ghostscript and add it to PATH. Looking for: {gs_cmd}")
                if target_kb:
                    out_bytes = compress_pdf_to_target(data, target_kb)
                else:
                    out_bytes = compress_pdf_preset(data, preset or "medium")
                outputs.append({"name": name, "bytes": out_bytes})
        except Exception as e:
            outputs.append({"name": name, "error": str(e)})

    return bundle_or_single(outputs)

@app.route("/convert", methods=["POST"])
def convert():
    target_format = request.form.get("target_format")  # jpg|png|webp|pdf|images|pdfa
    files = request.files.getlist("files")
    outputs = []

    for f in files:
        name = secure_filename(f.filename)
        ext = ext_of(name)
        data = f.read()
        try:
            if target_format in {"jpg", "png", "webp"} and ext in {'.png', '.jpg', '.jpeg', '.webp'}:
                out_bytes, out_ext = convert_image_format(data, target_format)
                outputs.append({"name": os.path.splitext(name)[0] + out_ext, "bytes": out_bytes})
            elif target_format == "pdf" and ext in {'.png', '.jpg', '.jpeg', '.webp'}:
                # images -> single PDF (if multiple files, they become one PDF)
                # defer bundling until all files read
                outputs.append({"name": name, "img_bytes": data})
            elif target_format == "images" and ext == '.pdf':
                # pdf -> images (multi-page)
                import shutil
                if not shutil.which('magick') and not shutil.which('convert'):
                    raise Exception("ImageMagick not found. Please install ImageMagick and add it to PATH.")
                page_images = pdf_to_images(data)
                for idx, b in enumerate(page_images):
                    outputs.append({"name": f"{os.path.splitext(name)[0]}_page_{idx+1}.jpg", "bytes": b})
            elif target_format == "pdfa" and ext == '.pdf':
                import shutil
                import platform
                gs_cmd = 'gswin64c' if platform.system() == 'Windows' else 'gs'
                if not shutil.which(gs_cmd) and not shutil.which('gs'):
                    raise Exception(f"Ghostscript not found. Please install Ghostscript and add it to PATH. Looking for: {gs_cmd}")
                out_bytes = pdf_to_pdfa(data)
                outputs.append({"name": os.path.splitext(name)[0] + "_PDF_A.pdf", "bytes": out_bytes})
            else:
                outputs.append({"name": name, "error": f"Unsupported conversion for {ext} -> {target_format}"})
        except Exception as e:
            outputs.append({"name": name, "error": str(e)})

    # If images -> PDF:
    if target_format == "pdf":
        img_list = [o["img_bytes"] for o in outputs if "img_bytes" in o]
        if img_list:
            try:
                pdf_bytes = images_to_pdf(img_list)
                ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                return send_file(
                    io.BytesIO(pdf_bytes), 
                    mimetype="application/pdf", 
                    as_attachment=True, 
                    download_name=f"images_{ts}.pdf"
                )
            except Exception as e:
                return jsonify({"error": str(e)}), 400

    return bundle_or_single(outputs)

def bundle_or_single(outputs):
    # If exactly one file and no error -> return direct
    valid = [o for o in outputs if "bytes" in o]
    errors = [o for o in outputs if "error" in o]
    if len(valid) == 1 and not errors:
        o = valid[0]
        # Detect mimetype from extension
        fname = o["name"]
        ext = ext_of(fname)
        mimetype_map = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp'
        }
        mimetype = mimetype_map.get(ext, 'application/octet-stream')
        return send_file(
            io.BytesIO(o["bytes"]), 
            mimetype=mimetype,
            as_attachment=True, 
            download_name=fname
        )
    # Else zip everything (include errors as text)
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as z:
        for o in outputs:
            if "bytes" in o:
                z.writestr(o["name"], o["bytes"])
            else:
                z.writestr(o["name"] + ".error.txt", o.get("error", "Unknown error"))
    mem.seek(0)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return send_file(
        mem, 
        mimetype="application/zip", 
        as_attachment=True, 
        download_name=f"processed_{ts}.zip"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)