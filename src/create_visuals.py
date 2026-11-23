from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"
WIDTH, HEIGHT = 1080, 1920


def tamil_font_path(bold: bool = False) -> Path:
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
    raise RuntimeError("Noto Sans Tamil is required; install it or set TAMIL_FONT_PATH.")


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(tamil_font_path(bold)), size=size)


def _latin_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    raise RuntimeError("A Latin-capable font is required for the English brand label.")


def _gradient() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        color = (int(10 + 22*t), int(19 + 18*t), int(38 + 28*t))
        for x in range(WIDTH):
            pixels[x, y] = color
    return image


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and draw.textbbox((0, 0), candidate, font=font)[2] > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _draw_scene(draw: ImageDraw.ImageDraw, topic: str, scene_index: int) -> str:
    """Create abstract editorial visuals that do not pretend to depict real events or places."""
    gold, pale = (218, 165, 82, 255), (225, 210, 178, 255)
    labels = ["முக்கிய கருத்து", "பின்னணி", "எப்படி செயல்படுகிறது?", "நினைவில் கொள்ளுங்கள்"]
    cx, cy = WIDTH // 2, 1330
    if scene_index == 0:
        # A central idea with connected supporting points.
        draw.ellipse((cx-180, cy-180, cx+180, cy+180), outline=gold, width=22)
        draw.ellipse((cx-95, cy-95, cx+95, cy+95), fill=(45, 82, 112, 255), outline=pale, width=10)
        for x, y in ((250, 1050), (830, 1050), (250, 1610), (830, 1610)):
            draw.line((cx, cy, x, y), fill=(105, 154, 178, 255), width=14)
            draw.ellipse((x-55, y-55, x+55, y+55), fill=(67, 105, 126, 255), outline=gold, width=10)
    elif scene_index == 1:
        # Layered cards suggest context and comparison, not factual evidence.
        for offset, fill in ((0, (54, 82, 105, 255)), (90, (75, 104, 122, 255)), (180, (99, 124, 132, 255))):
            draw.rounded_rectangle((180+offset, 1000+offset, 900-offset, 1370+offset),
                                   radius=38, fill=fill, outline=gold, width=9)
        for y in (1130, 1210, 1290):
            draw.line((340, y, 740, y), fill=pale, width=15)
    elif scene_index == 2:
        # A simple process path with four abstract stages.
        points = [(190, 1370), (420, 1080), (660, 1370), (890, 1080)]
        draw.line(points, fill=(103, 166, 184, 255), width=24, joint="curve")
        for x, y in points:
            draw.ellipse((x-75, y-75, x+75, y+75), fill=(49, 89, 111, 255), outline=gold, width=12)
    else:
        # A neutral takeaway / highlight frame.
        draw.rounded_rectangle((150, 980, 930, 1660), radius=60,
                               fill=(26, 48, 70, 255), outline=gold, width=14)
        draw.ellipse((cx-125, 1060, cx+125, 1310), outline=pale, width=18)
        draw.line((cx-65, 1190, cx-5, 1250, cx+105, 1110), fill=gold, width=24)
        for y in (1390, 1470, 1550):
            draw.line((300, y, 780, y), fill=(170, 190, 193, 255), width=14)
    return labels[scene_index]

def create_scene_visuals(draft_path: Path) -> list[Path]:
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    topic = str(draft.get("topic") or draft.get("title") or "")
    stem = draft_path.stem
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for index in range(4):
        image = _gradient()
        draw = ImageDraw.Draw(image, "RGBA")
        # Atmospheric light rings add depth while each topic gets four distinct illustrations.
        draw.ellipse((180-index*18, 330+index*35, 900+index*18, 1050+index*35),
                     outline=(220, 167, 93, 65), width=5)
        scene_label = _draw_scene(draw, topic, index)
        draw.rounded_rectangle((55, 70, 1025, 260), radius=28, fill=(5, 10, 22, 205),
                               outline=(220, 167, 93, 190), width=3)
        draw.text((90, 105), "MABOLO • TAMIL SHORTS", font=_latin_font(34, True),
                  fill=(235, 194, 125, 255))
        draw.text((90, 175), scene_label, font=_font(38, True), fill=(255, 255, 255, 255))
        path = OUTPUT_DIR / f"{stem}-scene-{index+1}.png"
        image.save(path, optimize=True)
        paths.append(path)
    return paths


def create_visuals(draft_path: Path) -> tuple[Path, Path]:
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    title = str(draft.get("title") or draft.get("topic") or "தமிழ் குறும்படம்")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = draft_path.stem
    scenes = create_scene_visuals(draft_path)
    vertical_path = scenes[0]
    thumb = ImageOps.fit(Image.open(scenes[0]).convert("RGB"), (1280, 720), method=Image.Resampling.LANCZOS)
    td = ImageDraw.Draw(thumb, "RGBA")
    td.rounded_rectangle((36, 36, 900, 684), radius=26, fill=(7, 12, 26, 218),
                         outline=(220, 167, 93, 220), width=4)
    td.text((76, 76), "MABOLO • TAMIL SHORTS", font=_latin_font(42, True), fill=(236, 192, 115, 255))
    font = _font(48, True)
    y = 165
    for line in _wrap(td, title, font, 760)[:5]:
        td.text((78, y), line, font=font, fill=(255, 255, 255, 255),
                stroke_width=2, stroke_fill=(8, 12, 22, 255))
        y += 76
    td.text((78, 625), "புதிய கோணத்தில் தெரிந்துகொள்வோம்", font=_font(25, True),
            fill=(235, 194, 125, 255))
    thumb_path = OUTPUT_DIR / f"{stem}-thumbnail.jpg"
    thumb.convert("RGB").save(thumb_path, quality=92, optimize=True)
    return vertical_path, thumb_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create original topic-neutral Tamil Short scene illustrations and a thumbnail.")
    parser.add_argument("--draft", type=Path, required=True)
    args = parser.parse_args()
    background, thumbnail = create_visuals(args.draft)
    print(f"First scene: {background}")
    print(f"Thumbnail: {thumbnail}")


if __name__ == "__main__":
    main()
