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
    """Create original, topic-matched illustrative scenes; not documentary site photographs."""
    key = topic.lower()
    gold, pale, dark = (218, 165, 82, 255), (225, 210, 178, 255), (13, 20, 34, 255)
    cx = WIDTH // 2
    if any(word in key for word in ("கீழடி", "keeladi", "அகழ")):
        labels = ["அகழாய்வு", "மண்பாண்டங்கள்", "பழங்கால வாழ்விடம்", "தொல்லியல் சான்றுகள்"]
        if scene_index == 0:
            draw.rectangle((100, 1030, 980, 1600), fill=(92, 65, 45, 255), outline=gold, width=8)
            for y in (1160, 1300, 1440):
                draw.line((150, y, 930, y+35), fill=(191, 145, 93, 255), width=18)
            draw.line((180, 1000, 900, 1580), fill=pale, width=12)
        elif scene_index == 1:
            for x, y, r in ((300, 1320, 115), (560, 1200, 150), (800, 1370, 95)):
                draw.ellipse((x-r, y-r, x+r, y+r), fill=(139, 76, 43, 255), outline=gold, width=10)
                draw.ellipse((x-r//2, y-r//2, x+r//2, y+r//2), outline=pale, width=8)
        elif scene_index == 2:
            draw.rectangle((180, 1240, 900, 1600), fill=dark, outline=gold, width=8)
            for x in (270, 470, 670, 830):
                draw.rectangle((x, 1100, x+35, 1600), fill=(151, 110, 72, 255))
            draw.polygon([(150, 1120), (540, 900), (930, 1120)], fill=(92, 72, 52, 255), outline=gold)
        else:
            for x, y in ((300, 1250), (540, 1380), (770, 1190)):
                draw.ellipse((x-70, y-70, x+70, y+70), outline=gold, width=14)
                draw.line((x-45, y, x+45, y), fill=pale, width=8)
        return labels[scene_index]
    if any(word in key for word in ("கடல்", "வாணிப", "பூம்புகார்", "poompuhar", "maritime")):
        labels = ["பண்டைய துறைமுகம்", "கடல் பயணம்", "வணிகப் பொருட்கள்", "கடல்வழி தொடர்புகள்"]
        if scene_index == 0:
            draw.rectangle((0, 1430, WIDTH, HEIGHT), fill=(24, 80, 111, 255))
            draw.rectangle((120, 1210, 960, 1450), fill=(125, 83, 49, 255))
            for x in (220, 450, 680, 880):
                draw.rectangle((x, 1050, x+25, 1430), fill=gold)
        elif scene_index == 1:
            draw.rectangle((0, 1320, WIDTH, HEIGHT), fill=(22, 83, 124, 255))
            draw.polygon([(170, 1370), (890, 1370), (760, 1570), (310, 1570)], fill=(113, 67, 39, 255), outline=gold)
            draw.line((540, 780, 540, 1370), fill=pale, width=18)
            draw.polygon([(520, 820), (520, 1280), (250, 1280)], fill=(224, 205, 165, 255))
            draw.polygon([(560, 900), (560, 1260), (820, 1260)], fill=(195, 164, 119, 255))
        elif scene_index == 2:
            for x, y in ((270, 1320), (540, 1250), (800, 1370)):
                draw.rectangle((x-85, y-90, x+85, y+90), fill=(139, 85, 47, 255), outline=gold, width=8)
                draw.arc((x-55, y-60, x+55, y+55), 0, 180, fill=pale, width=8)
        else:
            draw.ellipse((130, 950, 950, 1770), outline=(71, 153, 186, 255), width=18)
            for angle in range(0, 360, 45):
                import math
                x = cx + int(310 * math.cos(math.radians(angle)))
                y = 1360 + int(310 * math.sin(math.radians(angle)))
                draw.ellipse((x-28, y-28, x+28, y+28), fill=gold)
        return labels[scene_index]
    if any(word in key for word in ("நீர்", "அணை", "ஏரி", "கால்வாய்", "water")):
        labels = ["நீர்த்தேக்கம்", "கால்வாய் அமைப்பு", "அணை பொறியியல்", "விவசாயப் பயன்பாடு"]
        if scene_index == 0:
            draw.rectangle((0, 1250, WIDTH, HEIGHT), fill=(24, 100, 145, 255))
            draw.polygon([(0, 1180), (250, 850), (830, 850), (WIDTH, 1180)], fill=(73, 93, 71, 255))
            draw.line((180, 1180, 900, 1180), fill=gold, width=28)
        elif scene_index == 1:
            draw.rectangle((0, 1300, WIDTH, HEIGHT), fill=(25, 100, 145, 255))
            for y in (1200, 1330, 1460):
                draw.line((90, y, 990, y+80), fill=(108, 168, 180, 255), width=24)
            for x in (220, 500, 780):
                draw.line((x, 1000, x, 1580), fill=gold, width=12)
        elif scene_index == 2:
            draw.polygon([(100, 1000), (980, 1000), (900, 1570), (180, 1570)], fill=(105, 105, 97, 255), outline=gold)
            for y in (1130, 1280, 1430):
                draw.line((180, y, 900, y), fill=pale, width=12)
        else:
            for x in (220, 470, 720, 900):
                draw.line((x, 1200, x-40, 1640), fill=(76, 135, 75, 255), width=16)
                draw.ellipse((x-100, 1120, x+40, 1280), fill=(70, 139, 78, 255))
            draw.rectangle((0, 1510, WIDTH, HEIGHT), fill=(93, 73, 43, 255))
        return labels[scene_index]
    labels = ["பழங்கால நகரம்", "கட்டிடக்கலை", "அன்றாட வாழ்க்கை", "வரலாற்றுச் சான்றுகள்"]
    if scene_index == 0:
        draw.rectangle((120, 1180, 960, 1620), fill=dark, outline=gold, width=8)
        for x in range(200, 900, 150):
            draw.rectangle((x, 1280, x+80, 1460), fill=(110, 83, 59, 255), outline=pale, width=5)
    elif scene_index == 1:
        draw.polygon([(150, 1200), (540, 900), (930, 1200)], fill=(100, 74, 50, 255), outline=gold)
        draw.rectangle((200, 1200, 880, 1600), fill=(89, 71, 54, 255), outline=gold, width=8)
        for x in (350, 540, 730):
            draw.rectangle((x-35, 1320, x+35, 1600), fill=pale)
    elif scene_index == 2:
        for x, y in ((300, 1370), (540, 1250), (780, 1370)):
            draw.ellipse((x-65, y-65, x+65, y+65), fill=(154, 91, 53, 255), outline=gold, width=8)
            draw.rectangle((x-80, y+55, x+80, y+110), fill=(154, 91, 53, 255))
    else:
        draw.rectangle((180, 1110, 900, 1600), fill=(75, 69, 57, 255), outline=gold, width=8)
        for x in (300, 540, 780):
            draw.line((x, 1160, x, 1550), fill=pale, width=10)
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
        draw.text((90, 105), "MABOLO • TAMIL HISTORY", font=_latin_font(34, True),
                  fill=(235, 194, 125, 255))
        draw.text((90, 175), scene_label, font=_font(38, True), fill=(255, 255, 255, 255))
        path = OUTPUT_DIR / f"{stem}-scene-{index+1}.png"
        image.save(path, optimize=True)
        paths.append(path)
    return paths


def create_visuals(draft_path: Path) -> tuple[Path, Path]:
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    title = str(draft.get("title") or draft.get("topic") or "தமிழர் வரலாறு")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = draft_path.stem
    scenes = create_scene_visuals(draft_path)
    vertical_path = scenes[0]
    thumb = ImageOps.fit(Image.open(scenes[0]).convert("RGB"), (1280, 720), method=Image.Resampling.LANCZOS)
    td = ImageDraw.Draw(thumb, "RGBA")
    td.rounded_rectangle((36, 36, 900, 684), radius=26, fill=(7, 12, 26, 218),
                         outline=(220, 167, 93, 220), width=4)
    td.text((76, 76), "தமிழர் வரலாறு", font=_font(42, True), fill=(236, 192, 115, 255))
    font = _font(48, True)
    y = 165
    for line in _wrap(td, title, font, 760)[:5]:
        td.text((78, y), line, font=font, fill=(255, 255, 255, 255),
                stroke_width=2, stroke_fill=(8, 12, 22, 255))
        y += 76
    td.text((78, 625), "ஆதாரங்களுடன் அறிந்துகொள்வோம்", font=_font(25, True),
            fill=(235, 194, 125, 255))
    thumb_path = OUTPUT_DIR / f"{stem}-thumbnail.jpg"
    thumb.convert("RGB").save(thumb_path, quality=92, optimize=True)
    return vertical_path, thumb_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create original Tamil history scene illustrations and a thumbnail.")
    parser.add_argument("--draft", type=Path, required=True)
    args = parser.parse_args()
    background, thumbnail = create_visuals(args.draft)
    print(f"First scene: {background}")
    print(f"Thumbnail: {thumbnail}")


if __name__ == "__main__":
    main()
