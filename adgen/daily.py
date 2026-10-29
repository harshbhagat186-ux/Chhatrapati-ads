"""Makes one day's ads: a festival greeting if the date is in calendar.json, else the weekday's regular ad.

Usage: python3 daily.py [YYYY-MM-DD] [out_dir]   (date defaults to today in India)
Writes <out_dir>/<date>/ with 1080x1920 photos and 8 s reels with music, in Gujarati and Hindi.
"""
import json, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import generate
import music

HERE = Path(__file__).resolve().parent
LANGS = [("gu", "gujarati"), ("hi", "hindi")]
DECOR = {
    "coins": {"coins": [[200, 760, 70], [880, 760, 70, True], [150, 960, 50, True], [930, 960, 50], [540, 820, 150]]},
    "diyas": {"coins": [[540, 820, 140]],
              "diyas": [[180, 1215, 70], [380, 1240, 85], [700, 1240, 85], [900, 1215, 70], [540, 1180, 100]]},
    "both": {"coins": [[200, 760, 70], [880, 760, 70, True], [540, 820, 150, True]],
             "diyas": [[180, 1215, 70], [380, 1240, 85], [700, 1240, 85], [900, 1215, 70], [540, 1180, 100]]},
    "plain": {"coins": [[540, 820, 150]], "diyas": []},
}
REEL_SECONDS = 8


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


def reel(photo, wav, out):
    vf = ("scale=2160:3840,zoompan=z='min(1+0.0009*on,1.15)':x='iw/2-(iw/zoom/2)':y='ih/3-(ih/zoom/3)'"
          f":d={REEL_SECONDS * 30}:s=1080x1920:fps=30,fade=t=in:st=0:d=0.8,"
          f"fade=t=out:st={REEL_SECONDS - 0.8}:d=0.8,format=yuv420p")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-i", str(photo), "-i", str(wav),
                    "-vf", vf, "-t", str(REEL_SECONDS), "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    # Poster frame for the app's grid.
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", "1.5", "-i", str(out), "-frames:v", "1",
                    "-vf", "scale=540:-2", "-q:v", "4", str(out.with_suffix(".thumb.jpg"))], check=True)


def main():
    ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    day = sys.argv[1] if len(sys.argv) > 1 else ist.strftime("%Y-%m-%d")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "out") / day
    out.mkdir(parents=True, exist_ok=True)
    wav = out / "music.wav"
    music.write(REEL_SECONDS, wav, seed=int(day.replace("-", "")))
    n = 0
    for entry in plan(day):
        for lang, lname in LANGS:
            n += 1
            label = datetime.strptime(entry["date"], "%Y-%m-%d").strftime("%d %B %Y")
            ev = {"date": day, "lang": lang, "en": entry["en"], "theme": entry["theme"], "date_label": label,
                  **entry[lang], **DECOR[entry["decor"]]}
            photo = out / f"photo{n}-{entry['slug']}-{lname}.jpg"
            generate.render(ev, photo)
            reel(photo, wav, out / f"reel{n}-{entry['slug']}-{lname}.mp4")
            print(photo)
    wav.unlink()


if __name__ == "__main__":
    main()
