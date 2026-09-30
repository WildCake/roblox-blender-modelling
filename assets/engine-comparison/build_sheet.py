"""Lay out two unchanged native Roblox captures and recorded agent metrics."""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
RESULTS = json.loads((ROOT / "results.json").read_text(encoding="utf-8"))
FONT_ROOT = Path("C:/Windows/Fonts")
INK = "#26332e"
MUTED = "#65736b"
ACCENT = "#586b44"
PAPER = "#f6f7f3"


def font(size, bold=False):
    return ImageFont.truetype(str(FONT_ROOT / ("seguisb.ttf" if bold else "segoeui.ttf")), size)


def main():
    page = Image.new("RGB", (2400, 1400), PAPER)
    draw = ImageDraw.Draw(page)
    draw.text((86, 58), "ROBLOX  /  ENGINE CONCEPT STUDY", fill=ACCENT, font=font(27, True))
    draw.text((82, 101), "Same concept. Two modelling workflows.", fill=INK, font=font(63, True))
    draw.text((86, 188), "GPT-6.1 Sol  ·  High reasoning  ·  Independent agents  ·  30 September 2026", fill=MUTED, font=font(29))

    for index, variant in enumerate(RESULTS["variants"]):
        x = 84 + index * 1154
        draw.rounded_rectangle((x, 269, x + 1078, 1362), radius=24, fill="white", outline="#dde2d9", width=2)
        title = "A  /  Without skill" if index == 0 else "B  /  With modelling skill"
        draw.text((x + 36, 301), title, fill=INK, font=font(38, True))

        source = Image.open(ROOT / f"engine-{'a' if index == 0 else 'b'}-roblox.png").convert("RGB")
        if source.size != (1920, 819):
            raise ValueError(f"Unexpected native capture size: {source.size}")
        # Identical crop and scale retain the native model pixels and relative size.
        crop = source.crop((500, 150, 1400, 760))
        crop = crop.resize((1006, 682), Image.Resampling.LANCZOS)
        page.paste(crop, (x + 36, 365))

        draw.line((x + 36, 1068, x + 1042, 1068), fill="#e4e7e0", width=2)
        count_text = f"{variant['mesh_parts']} MeshParts   /   {variant['triangles']:,} triangles"
        draw.text((x + 36, 1090), count_text, fill=INK, font=font(38, True))
        seconds = round(variant["duration_ms"] / 1000)
        draw.text((x + 36, 1152), f"Agent time    {seconds // 60} min {seconds % 60:02d} s", fill=INK, font=font(29))
        draw.text((x + 36, 1201), f"Total tokens    {variant['total_tokens']:,}", fill=INK, font=font(29))
        draw.text((x + 36, 1248), f"Cached input    {variant['cached_input_tokens']:,}", fill=MUTED, font=font(27))
        draw.text((x + 36, 1294), f"Uncached input + output    {variant['uncached_input_plus_output_tokens']:,}", fill=MUTED, font=font(27))

    page.save(ROOT / "comparison-sheet.png", optimize=True)
    page.save(ROOT / "comparison-sheet.pdf", "PDF", resolution=205)
    print("Saved comparison-sheet.png and printable comparison-sheet.pdf")


if __name__ == "__main__":
    main()
