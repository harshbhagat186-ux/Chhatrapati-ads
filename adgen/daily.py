"""Makes one day's ads: a festival greeting if the date is in calendar.json, else the weekday's regular ad.

Usage: python3 daily.py [YYYY-MM-DD] [out_dir] [--afternoon | --evening]   (date defaults to today in India)
--afternoon / --evening make that greeting instead (numbered from 11 / 21 so they sit after the morning files).
Writes <out_dir>/<date>/ with 1080x1920 photos and 8 s animated reels with music, in Gujarati, Hindi and English.
Needs node + playwright (Chromium) and ffmpeg; the design lives in template.html.
"""
import json, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import music
from shop import BANK, LANDLINES, MOBILES, SHOP

HERE = Path(__file__).resolve().parent
LANGS = [("gu", "gujarati"), ("hi", "hindi"), ("en", "english")]
# Calendar themes (by their old RGB "inner" colour) -> background palettes.
PALETTES = {
    (150, 30, 20): ("#6b0f1a", "#160204"),  # maroon
    (90, 20, 110): ("#3f1060", "#0e0317"),  # royal purple
    (20, 70, 90): ("#0b4a55", "#02161a"),   # teal
    (30, 100, 50): ("#0d4a33", "#021710"),  # emerald
    (190, 90, 10): ("#7a3a06", "#1c0b02"),  # saffron
    (30, 40, 120): ("#13306e", "#040b1e"),  # navy
}
REEL_SECONDS = 8


# On-request greetings for later in the day: titles, English subtitle, decoration, first file number.
SLOTS = {
    "afternoon": ({"gu": "શુભ બપોર", "hi": "शुभ दोपहर", "en_page": "Good Afternoon"}, "Good Afternoon",
                  "Have a pleasant afternoon", "coins", 10),
    "evening": ({"gu": "શુભ સંધ્યા", "hi": "शुभ संध्या", "en_page": "Good Evening"}, "Good Evening",
                "Have a peaceful evening", "diyas", 20),
}


def slot_plan(day, slot):
    titles, en, subtitle, decor, _ = SLOTS[slot]
    cal = json.loads((HERE / "calendar.json").read_text())
    entry = json.loads(json.dumps(cal["daily"][datetime.strptime(day, "%Y-%m-%d").weekday()]))
    entry.update(date=day, slug="good-" + slot, decor=decor, en=en)
    for lang in ("gu", "hi", "en_page"):
        entry[lang]["title"] = titles[lang]
    entry["en_page"]["subtitle"] = subtitle
    return [entry]


def plan(day):
    """Today's festival (or the weekday's regular ad), plus festivals of the next 2 days so they can go out early."""
    cal = json.loads((HERE / "calendar.json").read_text())
    d = datetime.strptime(day, "%Y-%m-%d")
    fest = [f for f in cal["festivals"] if f["date"] == day]
    if not fest:
        entry = dict(cal["daily"][d.weekday()], date=day, slug="good-morning")
        fest = [entry]
    soon = {(d + timedelta(days=k)).strftime("%Y-%m-%d") for k in (1, 2)}
    return fest + [f for f in cal["festivals"] if f["date"] in soon]


def render(spec, photo, reel, wav):
    """Photo + animated reel via headless Chromium (render.js), plus the reel's poster frame for the app."""
    spec_file = photo.with_suffix(".json")
    spec_file.write_text(json.dumps(spec, ensure_ascii=False))
    subprocess.run(["node", str(HERE / "render.js"), str(spec_file), str(photo), str(reel), str(wav), str(REEL_SECONDS)], check=True)
    spec_file.unlink()
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", "4", "-i", str(reel), "-frames:v", "1",
                    "-vf", "scale=540:-2", "-q:v", "4", str(reel.with_suffix(".thumb.jpg"))], check=True)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    slot = next((a[2:] for a in sys.argv[1:] if a[2:] in SLOTS), None)
    ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    day = args[0] if args else ist.strftime("%Y-%m-%d")
    out = Path(args[1] if len(args) > 1 else "out") / day
    out.mkdir(parents=True, exist_ok=True)
    wav = out / "music.wav"
    music.write(REEL_SECONDS, wav, seed=int(day.replace("-", "")) + (SLOTS[slot][4] if slot else 0))
    n = SLOTS[slot][4] if slot else 0
    for entry in (slot_plan(day, slot) if slot else plan(day)):
        for lang, lname in LANGS:
            n += 1
            when = datetime.strptime(entry["date"], "%Y-%m-%d")
            bg1, bg2 = PALETTES.get(tuple(entry["theme"]["inner"]), PALETTES[(150, 30, 20)])
            # English pages keep their texts under "en_page" ("en" is the English subtitle of the other pages).
            text = entry["en_page"] if lang == "en" else entry[lang]
            spec = {"lang": lang, "title": text["title"], "en": text.get("subtitle", entry["en"]), "lines": text["lines"],
                    "offer": text.get("offer", ""), "decor": entry["decor"],
                    "date_label": f"{when.day:02d} · {when.strftime('%B').upper()} · {when.year}",
                    "palette": {"bg1": bg1, "bg2": bg2, "glow": "rgba(255,170,60,.30)"},
                    "shop": SHOP[lang], "mobiles": MOBILES, "landlines": LANDLINES, "labels": {"office": "Ph."},
                    "bank": BANK, "seed": n + int(day.replace("-", "")) % 1000}
            photo = out / f"photo{n:02d}-{entry['slug']}-{lname}.jpg"
            render(spec, photo, out / f"reel{n:02d}-{entry['slug']}-{lname}.mp4", wav)
            print(photo)
    wav.unlink()


if __name__ == "__main__":
    main()
