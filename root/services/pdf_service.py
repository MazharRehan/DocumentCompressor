import io
import os
import subprocess
import tempfile
import platform
from PIL import Image

def _get_gs_command():
    """Get the appropriate Ghostscript command for the current platform"""
    if platform.system() == 'Windows':
        return 'gswin64c'
    return 'gs'

def compress_pdf_preset(pdf_bytes, preset):
	preset_map = {"low": "screen", "medium": "ebook", "high": "printer"}
	gs_preset = preset_map.get(preset, "ebook")
	return _ghostscript_compress(pdf_bytes, gs_preset)

def compress_pdf_to_target(pdf_bytes, target_kb):
	target = target_kb * 1024
	for p in ["printer", "ebook", "screen"]:
		out = _ghostscript_compress(pdf_bytes, p)
		if len(out) <= target:
			return out
		pdf_bytes = out
	quality_flags = [
		("-dDownsampleColorImages=true", "-dColorImageResolution=120"),
		("-dColorImageDownsampleType=/Average", "-dColorImageResolution=100"),
		("-dJPEGQ=60",),
		("-dJPEGQ=50",),
	]
	cur = pdf_bytes
	for flags in quality_flags:
		cur = _ghostscript_compress(cur, "ebook", extra_flags=list(flags))
		if len(cur) <= target:
			return cur
	return cur

def _ghostscript_compress(pdf_bytes, preset, extra_flags=None):
	with tempfile.TemporaryDirectory() as td:
		inp = os.path.join(td, "in.pdf")
		outp = os.path.join(td, "out.pdf")
		with open(inp, "wb") as f:
			f.write(pdf_bytes)
		gs_cmd = _get_gs_command()
		cmd = [
			gs_cmd, "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
			"-dNOPAUSE", "-dQUIET", "-dBATCH",
			f"-dPDFSETTINGS=/{preset}",
			"-sOutputFile=" + outp, inp
		]
		if extra_flags:
			cmd[1:1] = extra_flags
		subprocess.run(cmd, check=True)
		with open(outp, "rb") as f:
			return f.read()

def pdf_to_images(pdf_bytes, dpi=150):
	with tempfile.TemporaryDirectory() as td:
		inp = os.path.join(td, "in.pdf")
		outp = os.path.join(td, "out_%03d.jpg")
		with open(inp, "wb") as f:
			f.write(pdf_bytes)
		cmd = ["magick", "-density", str(dpi), inp, "-quality", "85", outp]
		try:
			subprocess.run(cmd, check=True)
		except FileNotFoundError:
			cmd = ["convert", "-density", str(dpi), inp, "-quality", "85", outp]
			subprocess.run(cmd, check=True)
		imgs = []
		for name in sorted(os.listdir(td)):
			if name.startswith("out_") and name.endswith(".jpg"):
				with open(os.path.join(td, name), "rb") as f:
					imgs.append(f.read())
		return imgs

def images_to_pdf(image_bytes_list):
	pil_images = []
	for b in image_bytes_list:
		im = Image.open(io.BytesIO(b)).convert("RGB")
		pil_images.append(im)
	base = pil_images[0]
	buf = io.BytesIO()
	base.save(buf, format="PDF", save_all=True, append_images=pil_images[1:])
	return buf.getvalue()

def pdf_to_pdfa(pdf_bytes):
	with tempfile.TemporaryDirectory() as td:
		inp = os.path.join(td, "in.pdf")
		outp = os.path.join(td, "out_pdfa.pdf")
		with open(inp, "wb") as f:
			f.write(pdf_bytes)
		cmd = [
			"gs",
			"-dPDFA=2", "-dBATCH", "-dNOPAUSE", "-dQUIET",
			"-sProcessColorModel=DeviceRGB",
			"-sDEVICE=pdfwrite",
			"-sOutputFile=" + outp,
			"-dPDFACompatibilityPolicy=1",
			inp
		]
		subprocess.run(cmd, check=True)
		with open(outp, "rb") as f:
			return f.read()
