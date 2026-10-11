"""Üretilmiş sahne görsellerinin kontakt sayfası: python -m pipeline.sheet <slug> <çıktı.jpg>"""
import sys
from pathlib import Path

from PIL import Image

from .common import ROOT


def main(slug: str, out: str, cols: int = 12, w: int = 320, h: int = 214):
    d = ROOT / "episodes" / slug / "build" / "images"
    files = sorted(d.glob("*.png"))
    if not files:
        sys.exit("görsel yok")
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * h), "black")
    for i, f in enumerate(files):
        try:
            im = Image.open(f).convert("RGB").resize((w, h))
        except Exception:
            continue
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    sheet.save(out, quality=85)
    stamped = sum(1 for f in files if f.with_suffix(".hash").exists())
    print(f"[pipeline] kontakt sayfası: {len(files)} görsel ({stamped} tamamlanmış) → {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
