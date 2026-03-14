# Ruhvaan Bot - Watermark Module

import os
import asyncio
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from config import WATERMARK_TEXT, WATERMARK_LOGO

def _safe_font(px):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
              "arial.ttf"]:
        try: return ImageFont.truetype(p, px)
        except: pass
    return ImageFont.load_default()

def wm_image(inp: str, out: str, text: str = None, logo: str = None) -> bool:
    """Add watermark to image. Returns True on success."""
    text = text or WATERMARK_TEXT
    logo = logo or (WATERMARK_LOGO if WATERMARK_LOGO and os.path.exists(WATERMARK_LOGO) else None)
    try:
        with Image.open(inp).convert("RGBA") as base:
            w, h = base.size
            layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(layer)
            # Logo
            if logo and os.path.exists(logo):
                try:
                    lg = Image.open(logo).convert("RGBA")
                    th = max(48, int(h * 0.12))
                    lg = lg.resize((int(lg.width * (th / lg.height)), th), Image.Resampling.LANCZOS)
                    base.alpha_composite(lg, (20, h - lg.height - 20))
                except: pass
            # Text
            font = _safe_font(max(20, int(h * 0.04)))
            bb = draw.textbbox((0, 0), text, font=font)
            tw, th2 = bb[2] - bb[0], bb[3] - bb[1]
            x, y = w - tw - 24, h - th2 - 24
            draw.rectangle([x-8, y-8, x+tw+8, y+th2+8], fill=(0, 0, 0, 160))
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 240))
            Image.alpha_composite(base, layer).convert("RGB").save(out, "JPEG", quality=92)
            return True
    except Exception as ex:
        print(f"[WM_IMG] {ex}")
    return False

def _has_ffmpeg():
    try: subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True); return True
    except: return False

def wm_video(inp: str, out: str, text: str = None, logo: str = None) -> bool:
    """Add watermark to video using ffmpeg. Returns True on success."""
    if not _has_ffmpeg(): return False
    text = text or WATERMARK_TEXT
    logo = logo or (WATERMARK_LOGO if WATERMARK_LOGO and os.path.exists(WATERMARK_LOGO) else None)
    try:
        t = text.replace(":", r"\:").replace("'", r"\'")
        if logo and os.path.exists(logo):
            fc = (f"[1:v]scale=-1:80[lg];[0:v][lg]overlay=W-w-20:H-h-60[b];"
                  f"[b]drawtext=fontcolor=white:fontsize=26:box=1:boxcolor=black@0.6:"
                  f"boxborderw=8:text='{t}':x=W-tw-20:y=H-th-20[o]")
            cmd = ["ffmpeg", "-y", "-i", inp, "-i", logo, "-filter_complex", fc,
                   "-map", "[o]", "-map", "0:a?", "-c:v", "libx264",
                   "-preset", "veryfast", "-crf", "23", "-c:a", "copy", out]
        else:
            vf = (f"drawtext=fontcolor=white:fontsize=26:box=1:boxcolor=black@0.6:"
                  f"boxborderw=8:text='{t}':x=W-tw-20:y=H-th-20")
            cmd = ["ffmpeg", "-y", "-i", inp, "-vf", vf, "-c:v", "libx264",
                   "-preset", "veryfast", "-crf", "23", "-c:a", "copy", out]
        subprocess.run(cmd, check=True, capture_output=True, timeout=600)
        return True
    except subprocess.CalledProcessError as ex:
        print(f"[WM_VID_FF] {ex.stderr.decode(errors='ignore')[:300]}")
    except Exception as ex:
        print(f"[WM_VID] {ex}")
    return False

async def apply_watermark(inp: str, text: str = None) -> str:
    """
    Apply watermark to file at `inp`.
    Returns path to watermarked file, or original path if not applicable.
    """
    ext = Path(inp).suffix.lower()
    stem = Path(inp).stem
    parent = str(Path(inp).parent)

    if ext in [".jpg", ".jpeg", ".png", ".webp"]:
        out = os.path.join(parent, f"wm_{stem}.jpg")
        ok = await asyncio.to_thread(wm_image, inp, out, text)
        if ok and os.path.exists(out):
            return out
    elif ext in [".mp4", ".mov", ".mkv", ".avi", ".webm"]:
        out = os.path.join(parent, f"wm_{stem}.mp4")
        ok = await asyncio.to_thread(wm_video, inp, out, text)
        if ok and os.path.exists(out):
            return out

    return inp  # passthrough for other file types
