"""Eksik sahne görsellerini Gemini API ile üretir (yerelde çalıştırılır, anahtar bilgisayarda kalır).

Kullanım:
  python -m pipeline.gemini_images <slug> --limit 3        # önce deneme
  python -m pipeline.gemini_images <slug>                  # kalanların hepsi
  python -m pipeline.gemini_images <slug> --only s01_03,s01_11 --force

Anahtar GEMINI_API_KEY ortam değişkeninden okunur; ücretli (faturalandırması açık) bir projenin anahtarı
olmalıdır. Görseller episodes/<slug>/images/<id>.png olarak kaydedilir; dosyası olan sahne atlanır.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
PRICE = {"gemini-3.1-flash-image": 0.067, "gemini-3.1-flash-lite-image": 0.0336}  # USD/görsel, 1K, resmi liste
TAIL = (" Wide 16:9 landscape composition, keep heads and important objects away from the top and bottom edges. "
        "Absolutely no text, letters, numbers or signs with writing anywhere in the image.")
MAIN_CHAR = "brown 1970s suit jacket"  # {SEN} karakterinin istemdeki ayırt edici ifadesi
REF_NOTE = (" Use the attached image ONLY as a style and character reference: same line weight, same flat "
            "retro colors, same white-ball-head figures; the mustached man in the brown jacket is the "
            "recurring main character. Draw the new scene described above, do not copy the reference.")


def call(model: str, key: str, prompt: str, ref: bytes | None) -> bytes:
    parts = [{"text": prompt + (REF_NOTE if ref else "")}]
    if ref:
        parts.append({"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(ref).decode()}})
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9"}}}
    last = ""
    for attempt in range(5):
        try:
            r = requests.post(API.format(model=model), headers={"x-goog-api-key": key}, json=body, timeout=180)
        except requests.RequestException as e:
            last = f"bağlantı hatası: {e}"
            time.sleep(5 * (attempt + 1))
            continue
        if r.status_code == 200:
            for cand in r.json().get("candidates", []):
                for p in cand.get("content", {}).get("parts", []):
                    d = p.get("inlineData") or p.get("inline_data")
                    if d and d.get("data"):
                        return base64.b64decode(d["data"])
            raise RuntimeError("yanıtta görsel yok: " + r.text[:300])
        last = f"{r.status_code}: {r.text[:400]}"
        if r.status_code in (400, 401, 403, 404):
            raise RuntimeError(last)  # yeniden denemek sonucu değiştirmez
        time.sleep(min(60, 8 * 2 ** attempt))  # 429 / 5xx
    raise RuntimeError(last)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--model", default="gemini-3.1-flash-image")
    ap.add_argument("--limit", type=int, default=0, help="en fazla kaç görsel üretilsin (0 = hepsi)")
    ap.add_argument("--only", default="", help="virgülle ayrılmış sahne kimlikleri")
    ap.add_argument("--force", action="store_true", help="dosyası olan sahneyi de yeniden üret")
    ap.add_argument("--ref", default="", help="stil/karakter referans görseli (varsayılan: images/s01_04.png)")
    ap.add_argument("--no-ref", action="store_true")
    a = ap.parse_args()

    kf = ROOT / "gemini_key.txt"  # .gitignore'da; depoya gönderilmez
    key = (kf.read_text(encoding="utf-8").strip() if kf.exists() else "") or os.environ.get("GEMINI_API_KEY") \
        or sys.exit("Anahtar yok: proje klasörüne gemini_key.txt dosyası koy ya da GEMINI_API_KEY tanımla")
    ep = ROOT / "episodes" / a.slug
    rows = json.loads((ep / "gorsel_istemleri.json").read_text(encoding="utf-8"))
    out = ep / "images"
    out.mkdir(exist_ok=True)
    only = {x for x in a.only.split(",") if x}

    def have(i):
        return any((out / f"{i}{e}").exists() for e in (".png", ".jpg", ".jpeg", ".webp"))

    todo = [r for r in rows if (not only or r["id"] in only) and (a.force or not have(r["id"]))]
    if a.limit:
        todo = todo[:a.limit]
    ref = None
    if not a.no_ref:
        rp = Path(a.ref) if a.ref else out / "s01_04.png"
        if rp.exists():
            ref = rp.read_bytes()
    unit = PRICE.get(a.model)
    est = f"≈ {len(todo) * unit:.2f} USD (liste fiyatı)" if unit else "fiyat bilinmiyor"
    print(f"model: {a.model} | üretilecek: {len(todo)} görsel | tahmini: {est} | referans: {'var' if ref else 'yok'}",
          flush=True)

    ok, fail = 0, []
    for n, r in enumerate(todo, 1):
        try:
            # Referans yalnızca ana karakterin (bıyıklı memur) geçtiği sahnelere eklenir; yoksa model onu
            # ilgisiz sahnelere de çiziyor. Referans sahnenin kendisi referanssız üretilir.
            use_ref = ref if (MAIN_CHAR in r["istem"] and r["id"] != "s01_04") else None
            img = call(a.model, key, r["istem"], use_ref)
            (out / f"{r['id']}.png").write_bytes(img)
            ok += 1
            print(f"[{n}/{len(todo)}] {r['id']} tamam", flush=True)
        except Exception as e:  # tek sahne hatası işi durdurmasın
            fail.append(r["id"])
            print(f"[{n}/{len(todo)}] {r['id']} HATA: {e}", flush=True)
            if any(s in str(e) for s in ("401", "403", "API key", "billing", "PERMISSION")):
                sys.exit("Anahtar/faturalandırma sorunu — durduruldu. Ücretli projenin anahtarını kullandığından emin ol.")
    print(f"bitti: {ok} üretildi, {len(fail)} başarısız {fail if fail else ''}", flush=True)


if __name__ == "__main__":
    main()
