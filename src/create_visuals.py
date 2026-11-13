from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"
WIDTH, HEIGHT = 1080, 1920


def tamil_font_path(bold: bool = False) -> Path:
    """Return a real Tamil-capable font; never silently fall back to a Latin-only font."""
    configured = os.getenv("TAMIL_FONT_PATH")
    candidates = ([Path(configured)] if configured else []) + [
        Path("/usr/share/fonts/truetype/noto/NotoSansTamil-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoSansTamilUI-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSansTamilUI-Regular.ttf"),
        Path("/usr/share/fonts/opentype/noto/NotoSansTamil-Bold.ttf" if bold else "/usr/share/fonts/opentype/noto/NotoSansTamil-Regular.ttf"),
        Path("C:/Windows/Fonts/NotoSansTamil-Bold.ttf" if bold else "C:/Windows/Fonts/NotoSansTamil-Regular.ttf"),
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate
    raise RuntimeError(
        "A Tamil Unicode font was not found. Install Noto Sans Tamil or set TAMIL_FONT_PATH; "
        "refusing to render broken square glyphs."
    )


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(tamil_font_path(bold)), size=size)


def _latin_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Use a Latin font for the English brand label, separate from Tamil text."""
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    raise RuntimeError("A Latin-capable font is required for the English brand label.")


def _gradient(size: tuple[int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size)
    pixels = image.load()
    for y in range(height):
        t = y / max(1, height - 1)
        color = (int(12 + 24 * t), int(22 + 12 * t), int(43 + 18 * t))
        for x in range(width):
            pixels[x, y] = color
    return image


def _temple_silhouette(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    base = y1
    gold = (190, 133, 63)
    dark = (18, 23, 39)
    draw.rectangle((x0, base - 28, x1, base), fill=dark)
    center = (x0 + x1) // 2
    draw.rectangle((center - 90, base - 190, center + 90, base - 28), fill=dark)
    for level in range(6):
        inset = level * 22
        top = base - 205 - level * 58
        half = max(18, 105 - inset)
        draw.polygon([(center - half, top + 48), (center, top), (center + half, top + 48)],
                     fill=dark, outline=gold)
        draw.line((center - half, top + 48, center + half, top + 48), fill=gold, width=3)
    for dx in (-52, 0, 52):
        draw.rectangle((center + dx - 12, base - 150, center + dx + 12, base - 28), fill=gold)
    draw.arc((x0 + 15, base - 85, x1 - 15, base + 40), 180, 360, fill=gold, width=4)


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
               max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and draw.textbbox((0, 0), candidate, font=font)[2] > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def create_visuals(draft_path: Path) -> tuple[Path, Path]:
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    title = str(draft.get("title") or draft.get("topic") or "தமிழர் வரலாறு")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = draft_path.stem
    vertical = _gradient((WIDTH, HEIGHT))
    draw = ImageDraw.Draw(vertical, "RGBA")

    for radius in (180, 260, 340):
        draw.ellipse((WIDTH // 2 - radius, 390 - radius, WIDTH // 2 + radius, 390 + radius),
                     outline=(220, 167, 93, 75), width=5)
    _temple_silhouette(draw, (150, 1050, 930, 1640))
    draw.rounded_rectangle((70, 90, 1010, 300), radius=34, fill=(7, 12, 26, 190),
                           outline=(220, 167, 93, 170), width=3)
    draw.text((105, 145), "MABOLO • TAMIL HISTORY", font=_latin_font(38, True),
              fill=(235, 194, 125, 255))
    vertical_path = OUTPUT_DIR / f"{stem}-background.png"
    vertical.save(vertical_path, optimize=True)

    thumb = _gradient((1280, 720))
    td = ImageDraw.Draw(thumb, "RGBA")
    _temple_silhouette(td, (720, 200, 1230, 690))
    td.rounded_rectangle((48, 52, 830, 668), radius=28, fill=(7, 12, 26, 205),
                         outline=(220, 167, 93, 190), width=3)
    td.text((88, 92), "தமிழர் வரலாறு", font=_font(44, True),
            fill=(236, 192, 115, 255))
    font = _font(48, True)
    lines = _wrap_text(td, title, font, 680)
    y = 190
    for line in lines[:4]:
        td.text((90, y), line, font=font, fill=(255, 255, 255, 255),
                stroke_width=2, stroke_fill=(8, 12, 22, 255))
        y += 70
    td.text((90, 610), "ஆதாரங்களுடன் அறிந்துகொள்வோம்", font=_font(27, True),
            fill=(235, 194, 125, 255))
    thumb_path = OUTPUT_DIR / f"{stem}-thumbnail.jpg"
    thumb.convert("RGB").save(thumb_path, quality=92, optimize=True)
    return vertical_path, thumb_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create original Tamil history background and thumbnail artwork.")
    parser.add_argument("--draft", type=Path, required=True)
    args = parser.parse_args()
    background, thumbnail = create_visuals(args.draft)
    print(f"Background: {background}")
    print(f"Thumbnail: {thumbnail}")


if __name__ == "__main__":
    main()
