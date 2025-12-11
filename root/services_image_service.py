import io
import os
import subprocess
from PIL import Image

try:
    import tinify
except Exception:
    tinify = None

def _init_tinify(api_key):
    if tinify and api_key:
        tinify.key = api_key
        return True
    return False

def _pil_load(img_bytes):
    im = Image.open(io.BytesIO(img_bytes))
    # Convert to RGB for JPEG/WEBP
    if im.mode in ("RGBA", "P"):
        im = im.convert("RGB")
    return im

def _pil_save(im, fmt, quality=85):
    buf = io.BytesIO()
    params = {}
    if fmt.lower() in ["jpeg", "jpg", "webp"]:
        params["quality"] = quality
        if fmt.lower() == "webp":
            params["method"] = 6
    im.save(buf, format=fmt.upper(), **params)
    return buf.getvalue()

def convert_image_format(img_bytes, target_fmt):
    im = _pil_load(img_bytes)
    target_fmt = target_fmt.lower()
    if target_fmt == "jpg":
        out = _pil_save(im, "JPEG", quality=90)
        return out, ".jpg"
    if target_fmt == "png":
        # PNG is lossless, allow optimize
        buf = io.BytesIO()
        im.save(buf, format="PNG", optimize=True)
        return buf.getvalue(), ".png"
    if target_fmt == "webp":
        out = _pil_save(im, "WEBP", quality=85)
        return out, ".webp"
    raise ValueError(f"Unsupported target format: {target_fmt}")

def _tinify_bytes(img_bytes):
    source = tinify.from_buffer(img_bytes)
    return source.to_buffer()

def compress_image_preset(img_bytes, ext, preset, use_tinify, api_key):
    preset_map = {"high": 85, "medium": 70, "low": 50}
    quality = preset_map.get(preset, 70)
    im = _pil_load(img_bytes)
    fmt = "JPEG" if ext in [".jpg", ".jpeg"] else ("PNG" if ext == ".png" else "WEBP")
    out = _pil_save(im, fmt, quality=quality)
    if use_tinify and _init_tinify(api_key):
        try:
            out = _tinify_bytes(out)
        except Exception:
            pass
    final_ext = ".jpg" if fmt == "JPEG" else (".png" if fmt == "PNG" else ".webp")
    return out, final_ext

def compress_image_to_target(img_bytes, ext, target_kb, use_tinify, api_key, max_downscale_steps=3):
    target = target_kb * 1024
    im = _pil_load(img_bytes)
    fmt = "JPEG" if ext in [".jpg", ".jpeg"] else ("PNG" if ext == ".png" else "WEBP")
    # Binary search on quality
    lo, hi = 30, 95
    best = None
    for _ in range(8):
        mid = (lo + hi) // 2
        out = _pil_save(im, fmt, quality=mid)
        if len(out) <= target:
            best = out
            lo = mid + 1
        else:
            hi = mid - 1
    if best is None:
        best = _pil_save(im, fmt, quality=lo)
    # Optional downscale if still too large
    step = 0
    while len(best) > target and step < max_downscale_steps:
        w, h = im.size
        im = im.resize((int(w * 0.9), int(h * 0.9)), Image.LANCZOS)
        best = _pil_save(im, fmt, quality=lo)
        step += 1
    if use_tinify and _init_tinify(api_key):
        try:
            tb = _tinify_bytes(best)
            if len(tb) <= len(best):
                best = tb
        except Exception:
            pass
    final_ext = ".jpg" if fmt == "JPEG" else (".png" if fmt == "PNG" else ".webp")
    return best, final_ext