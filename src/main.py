
"""
Biox Systems — AI QR Code Generator
Usage (CLI):
  python biox_qr.py "https://your-url.com" --out qr.png --title "Biox Systems" --subtitle "AI QR Code Generator"

Options:
  --out <file>             Output PNG path (default: qr_biox.png)
  --title <text>           Header/title above the QR (default: "Biox Systems")
  --subtitle <text>        Subtitle below header (default: "AI QR Code Generator")
  --footer <text>          Footer at the bottom (default: "Biox Systems • AI QR Code Generator • 1994→2025")
  --logo <path>            Optional logo PNG with transparent background to place at QR center
  --dark "#000000"         Dark color for QR (default black)
  --light "#FFFFFF"        Light color/background for QR (default white)
  --size 1024              QR box pixel size (default 1024) — final canvas is larger to fit text margins
"""

import argparse
from PIL import Image, ImageDraw, ImageFont
import qrcode
from qrcode.constants import ERROR_CORRECT_H
import os, textwrap

def load_font(size: int):
    # Try to load a nice sans font; fall back to default if not available.
    # DejaVuSans is usually present in many environments.
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def make_qr(data: str, box_size: int = 18, border: int = 4, fill_color="#000000", back_color="#FFFFFF"):
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H, # high error correction for center logo
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")
    return img

def paste_logo(center_img: Image.Image, logo_path: str):
    if not logo_path or not os.path.exists(logo_path):
        return center_img
    logo = Image.open(logo_path).convert("RGBA")
    # scale logo to ~18% of QR size
    qr_w, qr_h = center_img.size
    target = int(min(qr_w, qr_h) * 0.18)
    logo.thumbnail((target, target))
    # optional white circle behind logo for contrast
    circle = Image.new("RGBA", logo.size, (255,255,255,0))
    draw = ImageDraw.Draw(circle)
    r = min(logo.size)//2
    draw.ellipse([(0,0),(logo.size[0], logo.size[1])], fill=(255,255,255,235))
    # center positions
    x = (qr_w - logo.size[0])//2
    y = (qr_h - logo.size[1])//2
    # paste circle then logo
    center_img.alpha_composite(circle, (x, y))
    center_img.alpha_composite(logo, (x, y))
    return center_img

def compose_layout(qr_img: Image.Image, title="Biox Systems", subtitle="AI QR Code Generator",
                   footer="Biox Systems • AI QR Code Generator • 1994→2025",
                   bg="#FFFFFF", margin=80):
    # Create a tall canvas to host title, subtitle, QR, and footer
    qr_w, qr_h = qr_img.size
    # Heuristic canvas size
    canvas_w = qr_w + margin*2
    canvas_h = qr_h + margin*2 + 260  # extra vertical room for texts

    canvas = Image.new("RGBA", (canvas_w, canvas_h), bg)
    draw = ImageDraw.Draw(canvas)

    # Fonts
    title_font = load_font(72)
    subtitle_font = load_font(36)
    footer_font = load_font(28)

    # Title
    title_w, title_h = draw.textbbox((0,0), title, font=title_font)[2:4]
    title_x = (canvas_w - title_w)//2
    y_cursor = margin//2
    draw.text((title_x, y_cursor), title, font=title_font, fill="#000000")

    # Subtitle
    y_cursor += title_h + 8
    subtitle_w, subtitle_h = draw.textbbox((0,0), subtitle, font=subtitle_font)[2:4]
    subtitle_x = (canvas_w - subtitle_w)//2
    draw.text((subtitle_x, y_cursor), subtitle, font=subtitle_font, fill="#333333")

    # QR
    y_cursor += subtitle_h + 24
    qr_x = (canvas_w - qr_w)//2
    canvas.alpha_composite(qr_img, (qr_x, y_cursor))
    y_cursor += qr_h + 24

    # Footer
    # If footer is long, wrap it
    wrap_width = max(28, int(canvas_w/28))  # rough
    lines = textwrap.wrap(footer, width=50)
    for i, line in enumerate(lines):
        fw, fh = draw.textbbox((0,0), line, font=footer_font)[2:4]
        fx = (canvas_w - fw)//2
        draw.text((fx, y_cursor + i*(fh+4)), line, font=footer_font, fill="#555555")

    return canvas.convert("RGB")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="URL to encode")
    ap.add_argument("--out", default="qr_biox.png", help="output PNG path")
    ap.add_argument("--title", default="Biox Systems")
    ap.add_argument("--subtitle", default="AI QR Code Generator")
    ap.add_argument("--footer", default="Biox Systems • AI QR Code Generator • 1994→2025")
    ap.add_argument("--logo", default=None, help="optional PNG logo to center")
    ap.add_argument("--dark", default="#000000")
    ap.add_argument("--light", default="#FFFFFF")
    ap.add_argument("--size", type=int, default=1024, help="QR pixel size; final canvas is larger")
    args = ap.parse_args()

    # Determine a box_size that yields about args.size width for QR area
    # box_size * modules + 2*border*box_size ~= size. We'll approximate with box_size= int(size/45)
    # but better: try box_size and resize QR to target.
    base = make_qr(args.url, box_size=20, border=4, fill_color=args.dark, back_color=args.light)
    # Resize precisely to requested size while keeping sharp edges via nearest neighbor
    qr_img = base.resize((args.size, args.size), resample=Image.NEAREST)

    if args.logo:
        qr_img = paste_logo(qr_img, args.logo)

    final_img = compose_layout(qr_img, title=args.title, subtitle=args.subtitle, footer=args.footer, bg=args.light)
    final_img.save(args.out, format="PNG")
    print(f"Saved: {args.out}")

if __name__ == "__main__":
    main()
