#!/usr/bin/env python3
"""
Biox Systems — AI QR Code Generator (Optimized & Commented)
-----------------------------------------------------------
Generates a branded, layout-ready PNG containing:
  • Optional title (header)
  • Optional subtitle
  • High-error-correction QR code (safe for a small center logo)
  • Optional footer

Quick start:
  pip install qrcode pillow
  python main.py "https://your-url.com" --out qr.png --title "Biox Systems" --subtitle "AI QR Code Generator"

Key optimizations:
  1) Exact pixel sizing without resizing the QR grid (avoids blur).
  2) Modern Pillow resampling for non-QR assets (logos).
  3) Safer color parsing (hex or named colors).
  4) Clean, centered layout with optional sections and wrapped footer.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Optional, Tuple, List

from PIL import Image, ImageDraw, ImageFont, ImageColor
from PIL.Image import Resampling

import qrcode
from qrcode.constants import ERROR_CORRECT_H


# ------------------------------
# Utilities
# ------------------------------

def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """
    Best-effort load of a sans or sans-bold font; falls back to default bitmap font.
    DejaVuSans is commonly available on many systems.
    """
    candidates = [
        ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
        ("Arial Bold.ttf" if bold else "Arial.ttf"),
        ("Helvetica Bold.ttf" if bold else "Helvetica.ttf"),
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def parse_color(value: str, default_hex: str) -> str:
    """
    Validate and normalize a color string. Accepts hex ("#000", "#000000")
    or named colors ("black"). Returns a safe "#rrggbb" hex string.
    """
    if not value:
        return default_hex
    try:
        r, g, b = ImageColor.getrgb(value)
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return default_hex


@dataclass
class LayoutConfig:
    title: str = "Biox Systems"
    subtitle: str = "AI QR Code Generator"
    footer: str = "Biox Systems • AI QR Code Generator • 1994→2025"
    bg_color: str = "#FFFFFF"
    dark_color: str = "#000000"
    pad: int = 80                 # outer canvas padding
    gap_title_sub: int = 8        # gap between title and subtitle
    gap_sub_qr: int = 24          # gap between subtitle and QR
    gap_qr_footer: int = 24       # gap between QR and footer
    max_footer_width_chars: int = 60  # soft wrap width for footer


# ------------------------------
# QR Generation
# ------------------------------

def compute_box_size(target_px: int, modules: int, border: int) -> int:
    """
    Compute `box_size` such that:
        total_px = (modules + 2*border) * box_size
    is the largest value <= target_px.
    Ensures the QR is rasterized at the intended scale (no post-resize).
    """
    denom = max(1, (modules + 2 * border))
    return max(1, target_px // denom)


def build_qr_image(data: str, target_px: int, border: int,
                   dark: str, light: str) -> Image.Image:
    """
    Build a QR image close to `target_px` without resizing the QR grid.
    Returns an RGBA image. May be slightly smaller than target_px due to integer math.
    """
    # First pass: probe to learn module count
    probe = qrcode.QRCode(
        version=None,              # automatic sizing
        error_correction=ERROR_CORRECT_H,
        box_size=10,               # provisional
        border=border,
    )
    probe.add_data(data)
    probe.make(fit=True)
    modules = probe.modules_count

    # Compute a clean integer box size, then render for real
    box_size = compute_box_size(target_px, modules, border)

    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=dark, back_color=light).convert("RGBA")
    return img


def paste_center_logo(qr_img: Image.Image, logo_path: Optional[str]) -> Image.Image:
    """
    Paste a small logo at the center of the QR.
    - Scales the logo to ~18% of the QR side.
    - Adds a rounded white backing for contrast.
    """
    if not logo_path or not os.path.exists(logo_path):
        return qr_img

    qr_w, qr_h = qr_img.size
    max_side = int(min(qr_w, qr_h) * 0.18)

    logo = Image.open(logo_path).convert("RGBA")
    logo.thumbnail((max_side, max_side), resample=Resampling.LANCZOS)

    # Rounded white backing with slight padding
    pad = max(4, max(logo.size) // 12)
    bg_w, bg_h = logo.size[0] + pad * 2, logo.size[1] + pad * 2
    backing = Image.new("RGBA", (bg_w, bg_h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(backing)
    radius = min(bg_w, bg_h) // 5
    draw.rounded_rectangle([(0, 0), (bg_w - 1, bg_h - 1)], radius=radius, fill=(255, 255, 255, 235))
    backing.alpha_composite(logo, (pad, pad))

    # Center composite onto QR
    x = (qr_w - bg_w) // 2
    y = (qr_h - bg_h) // 2
    out = qr_img.copy()
    out.alpha_composite(backing, (x, y))
    return out


# ------------------------------
# Layout Composition
# ------------------------------

def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> Tuple[int, int]:
    """Return (width, height) using textbbox for reliable metrics."""
    if not text:
        return (0, 0)
    bbox = draw.textbbox((0, 0), text, font=font)
    return (bbox[2] - bbox[0], bbox[3] - bbox[1])


def compose_layout(qr_img: Image.Image, cfg: LayoutConfig) -> Image.Image:
    """
    Compose the final PNG with background, title, subtitle, QR, and footer.
    Empty strings automatically omit that section.
    """
    # Fonts
    title_font = load_font(72, bold=True)
    subtitle_font = load_font(38, bold=False)
    footer_font = load_font(28, bold=False)

    qr_w, qr_h = qr_img.size
    canvas_w = qr_w + cfg.pad * 2

    # Pre-compute estimated height for canvas
    dummy = Image.new("RGBA", (1, 1), cfg.bg_color)
    d = ImageDraw.Draw(dummy)
    est_h = cfg.pad  # top pad baseline

    if cfg.title:
        est_h += text_size(d, cfg.title, title_font)[1] + cfg.gap_title_sub
    if cfg.subtitle:
        est_h += text_size(d, cfg.subtitle, subtitle_font)[1] + cfg.gap_sub_qr

    est_h += qr_h + cfg.gap_qr_footer

    # Estimate 1–2 lines for footer; actual drawing will use same font
    if cfg.footer:
        est_h += text_size(d, "Ag", footer_font)[1] * 2 + 12

    est_h += cfg.pad  # bottom pad

    # Create canvas + draw
    canvas = Image.new("RGBA", (canvas_w, est_h), cfg.bg_color)
    draw = ImageDraw.Draw(canvas)

    y = cfg.pad // 2

    # Title
    if cfg.title:
        tw, th = text_size(draw, cfg.title, title_font)
        draw.text(((canvas_w - tw) // 2, y), cfg.title, font=title_font, fill="#000000")
        y += th + cfg.gap_title_sub

    # Subtitle
    if cfg.subtitle:
        sw, sh = text_size(draw, cfg.subtitle, subtitle_font)
        draw.text(((canvas_w - sw) // 2, y), cfg.subtitle, font=subtitle_font, fill="#333333")
        y += sh + cfg.gap_sub_qr

    # QR
    x_qr = (canvas_w - qr_w) // 2
    canvas.alpha_composite(qr_img, (x_qr, y))
    y += qr_h + cfg.gap_qr_footer

    # Footer (simple char-wrap so it's predictable)
    if cfg.footer:
        line_width = max(12, cfg.max_footer_width_chars)
        # Manual wrap without splitting words too aggressively
        words = cfg.footer.split()
        lines: List[str] = []
        current = ""
        for w in words:
            test = (current + " " + w).strip()
            if len(test) <= line_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)

        for line in lines:
            fw, fh = text_size(draw, line, footer_font)
            draw.text(((canvas_w - fw) // 2, y), line, font=footer_font, fill="#555555")
            y += fh + 4

    return canvas.convert("RGB")


# ------------------------------
# CLI
# ------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Biox Systems — AI QR Code Generator (Optimized)")
    ap.add_argument("url", help="URL to encode into the QR code")
    ap.add_argument("--out", default="qr_biox.png", help="Output PNG path (default: qr_biox.png)")
    ap.add_argument("--title", default="Biox Systems", help="Title text ('' to hide)")
    ap.add_argument("--subtitle", default="AI QR Code Generator", help="Subtitle text ('' to hide)")
    ap.add_argument("--footer", default="Biox Systems • AI QR Code Generator • 1994→2025", help="Footer text ('' to hide)")
    ap.add_argument("--logo", default=None, help="Optional PNG logo to place at QR center")
    ap.add_argument("--dark", default="#000000", help="Dark (QR) color; hex or name")
    ap.add_argument("--light", default="#FFFFFF", help="Light (background) color; hex or name")
    ap.add_argument("--size", type=int, default=1024, help="Target QR pixel size (default 1024)")
    ap.add_argument("--border", type=int, default=4, help="QR border/quiet zone modules (default 4)")
    ap.add_argument("--pad", type=int, default=80, help="Outer canvas padding in pixels (default 80)")
    args = ap.parse_args()

    # Normalize colors
    dark = parse_color(args.dark, "#000000")
    light = parse_color(args.light, "#FFFFFF")

    # Build QR at target size (no post-resize)
    qr_img = build_qr_image(args.url, target_px=args.size, border=args.border, dark=dark, light=light)

    # Optional center logo
    qr_img = paste_center_logo(qr_img, args.logo)

    # Compose final poster
    cfg = LayoutConfig(
        title=args.title,
        subtitle=args.subtitle,
        footer=args.footer,
        bg_color=light,
        dark_color=dark,
        pad=args.pad,
    )
    final_img = compose_layout(qr_img, cfg)

    # Save PNG
    final_img.save(args.out, format="PNG")
    print(f"✅ Saved: {args.out}")


if __name__ == "__main__":
    main()
