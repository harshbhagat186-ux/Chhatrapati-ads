"""Daily ad generator for Chhatrapati Bullion. Renders 1080x1920 (Full HD) posters."""
import math, random, sys, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONTS = Path(__file__).resolve().parent / "fonts"
W, H = 1080, 1920

SHOP = {
    "gu": {
        "blessing": "॥ શ્રી સિદ્ધનાથ પ્રસન્ન ॥",
        "name": "છત્રપતિ બુલિયન",
        "line1": "ચાંદી-સોનું લેનાર તથા વેચનાર",
        "line2": "બદલો કરી આપશું.",
        "addr": "ડાયમંડ ચેમ્બર્સ, ગ્રાઉન્ડ ફ્લોર, દરબાર ગઢ ચોક, સોની બજાર, રાજકોટ.",
        "owner": "હર્ષ અર્જુન ભગત",
    },
    "hi": {
        "blessing": "॥ श्री सिद्धनाथ प्रसन्न ॥",
        "name": "छत्रपति बुलियन",
        "line1": "चांदी-सोना लेनार और विक्रेता",
        "line2": "तबादला भी करते है.",
        "addr": "डायमंड चेम्बर्स, ग्राउन्ड फलोर, दरबार गढ चोक, सोनी बाजार, राजकोट.",
        "owner": "हर्ष अर्जुन भगत",
    },
}
PHONES = "📞 2291736 | 2290015"
MOBILES = ["88300 50875", "97679 88351", "90964 92957"]


def font(lang, size):
    name = {"gu": "HindVadodara-Bold.ttf", "hi": "Hind-Bold.ttf"}[lang]
    return ImageFont.truetype(str(FONTS / name), size, layout_engine=ImageFont.Layout.RAQM)


def latin(size, bold=True):
    f = ImageFont.truetype(str(FONTS / "PlayfairDisplay.ttf"), size)
    f.set_variation_by_name("Bold" if bold else "Regular")
    return f


def sans(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", str(FONTS / "Hind-Bold.ttf")):
        if Path(p).exists():
            return ImageFont.truetype(p, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def radial_bg(c_in, c_out):
    img = Image.new("RGB", (W, H))
    px = img.load()
    cx, cy, maxd = W / 2, H * 0.38, math.hypot(W / 2, H * 0.62)
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            t = min(1, math.hypot(x - cx, y - cy) / maxd) ** 0.9
            c = lerp(c_in, c_out, t)
            px[x, y] = c
            if x + 1 < W: px[x + 1, y] = c
            if y + 1 < H:
                px[x, y + 1] = c
                if x + 1 < W: px[x + 1, y + 1] = c
    return img


def vgrad(w, h, top, bottom):
    g = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(g)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=lerp(top, bottom, y / max(1, h - 1)))
    return g


def mandala(layer, cx, cy, r, color, petals=16):
    d = ImageDraw.Draw(layer)
    for ring, (rr, n) in enumerate([(r, petals), (r * 0.72, petals), (r * 0.46, petals // 2)]):
        for i in range(n):
            a = 2 * math.pi * i / n + ring * math.pi / n
            px, py = cx + rr * math.cos(a), cy + rr * math.sin(a)
            s = rr * 0.16
            d.ellipse([px - s, py - s, px + s, py + s], outline=color, width=3)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=color, width=2)


def diya(layer, cx, cy, s, glow=True):
    d = ImageDraw.Draw(layer)
    if glow:
        g = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        for k in range(10, 0, -1):
            rr = s * 0.25 * k
            gd.ellipse([cx - rr, cy - s * 0.9 - rr, cx + rr, cy - s * 0.9 + rr], fill=(255, 190, 60, 10))
        layer.alpha_composite(g.filter(ImageFilter.GaussianBlur(s * 0.3)))
        d = ImageDraw.Draw(layer)
    # bowl
    d.chord([cx - s, cy - s * 0.55, cx + s, cy + s * 0.55], 0, 180, fill=(196, 84, 20), outline=(255, 214, 102), width=4)
    d.ellipse([cx - s, cy - s * 0.12, cx + s, cy + s * 0.12], fill=(140, 50, 10), outline=(255, 214, 102), width=3)
    for i in range(-3, 4):
        d.ellipse([cx + i * s * 0.26 - 5, cy + s * 0.28 - 5, cx + i * s * 0.26 + 5, cy + s * 0.28 + 5], fill=(255, 214, 102))
    # flame
    fx, fy = cx + s * 0.55, cy - s * 0.1
    d.polygon([(fx - s * 0.18, fy), (fx, fy - s * 0.85), (fx + s * 0.18, fy)], fill=(255, 150, 20))
    d.ellipse([fx - s * 0.18, fy - s * 0.25, fx + s * 0.18, fy + s * 0.05], fill=(255, 150, 20))
    d.polygon([(fx - s * 0.08, fy - s * 0.02), (fx, fy - s * 0.5), (fx + s * 0.08, fy - s * 0.02)], fill=(255, 245, 180))


def coin(layer, cx, cy, r, silver=False):
    d = ImageDraw.Draw(layer)
    base, rim, mark = ((200, 205, 215), (245, 245, 250), (150, 155, 165)) if silver else ((232, 170, 40), (255, 225, 120), (170, 110, 20))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=base, outline=rim, width=max(3, r // 10))
    d.ellipse([cx - r * 0.78, cy - r * 0.78, cx + r * 0.78, cy + r * 0.78], outline=mark, width=max(2, r // 18))
    f = ImageFont.truetype(str(FONTS / "Hind-Bold.ttf"), int(r * 0.9), layout_engine=ImageFont.Layout.RAQM)
    d.text((cx, cy + r * 0.05), "श्री", font=f, fill=mark, anchor="mm")


def sparkles(layer, n, seed, area):
    rnd = random.Random(seed)
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = area
    for _ in range(n):
        x, y, s = rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(3, 11)
        a = rnd.randint(120, 255)
        d.polygon([(x, y - s * 2), (x + s * 0.4, y), (x, y + s * 2), (x - s * 0.4, y)], fill=(255, 230, 150, a))
        d.polygon([(x - s * 2, y), (x, y + s * 0.4), (x + s * 2, y), (x, y - s * 0.4)], fill=(255, 230, 150, a))


def text_c(d, y, txt, f, fill, stroke=0, stroke_fill=None, shadow=True):
    if shadow:
        d.text((W / 2 + 4, y + 5), txt, font=f, fill=(0, 0, 0, 140), anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0, 140))
    d.text((W / 2, y), txt, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=stroke_fill)


def fit(lang, txt, max_w, start, fn=None):
    fn = fn or (lambda s: font(lang, s))
    s = start
    while s > 20:
        f = fn(s)
        if f.getbbox(txt)[2] - f.getbbox(txt)[0] <= max_w:
            return f
        s -= 2
    return fn(s)


def footer(img, lang):
    sh = SHOP[lang]
    top = 1395
    band = vgrad(W, H - top, (214, 40, 30), (250, 225, 30)).convert("RGBA")
    img.alpha_composite(band, (0, top))
    d = ImageDraw.Draw(img)
    d.line([(0, top), (W, top)], fill=(255, 215, 0), width=8)
    navy = (22, 30, 110)
    d.text((40, top + 34), PHONES.replace("📞 ", "Ph. "), font=sans(30), fill="white")
    d.text((W - 40, top + 34), sh["owner"], font=font(lang, 36), fill="white", anchor="ra")
    name_f = font(lang, 118)
    d.text((W / 2, top + 175), sh["name"], font=name_f, fill=navy, anchor="mm", stroke_width=5, stroke_fill="white")
    d.text((W / 2, top + 275), sh["line1"] + " • " + sh["line2"], font=fit(lang, sh["line1"] + " • " + sh["line2"], W - 80, 44), fill=(200, 20, 20), anchor="mm")
    d.text((W / 2, top + 340), sh["addr"], font=fit(lang, sh["addr"], W - 60, 34), fill=(20, 20, 20), anchor="mm")
    # mobile strip
    d.rounded_rectangle([30, top + 385, W - 30, top + 495], radius=28, fill=navy)
    d.text((W / 2, top + 440), "M. " + "  |  ".join(MOBILES), font=fit(lang, "M. " + "  |  ".join(MOBILES), W - 100, 46, fn=sans), fill="white", anchor="mm")


def render(ev, out):
    lang = ev["lang"]
    theme = ev.get("theme", {})
    bg = radial_bg(tuple(theme.get("inner", (120, 20, 30))), tuple(theme.get("outer", (30, 5, 10)))).convert("RGBA")
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mandala(deco, W / 2, 820, 400, (255, 215, 120, 70), 20)
    mandala(deco, W / 2, 820, 250, (255, 215, 120, 90), 12)
    bg.alpha_composite(deco)
    fx = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sparkles(fx, 70, ev["date"], (0, 0, W, 1350))
    for c in ev.get("coins", []):
        coin(fx, *c)
    for dx in ev.get("diyas", [(270, 1200, 85), (540, 1240, 105), (810, 1200, 85)]):
        diya(fx, *dx)
    bg.alpha_composite(fx)
    d = ImageDraw.Draw(bg)
    gold, cream = (255, 210, 90), (255, 244, 214)
    # top border
    d.rectangle([24, 24, W - 24, 1370], outline=(255, 210, 90, 180), width=3)
    d.rectangle([36, 36, W - 36, 1358], outline=(255, 210, 90, 110), width=1)
    text_c(d, 100, SHOP[lang]["blessing"], font(lang, 38), cream, shadow=False)
    text_c(d, 290, ev["title"], fit(lang, ev["title"], W - 120, 150), gold, 4, (110, 30, 0))
    if ev.get("en"):
        text_c(d, 420, ev["en"], latin(62), cream)
    y = 520
    for line in ev.get("lines", []):
        text_c(d, y, line, fit(lang, line, W - 140, 52), cream)
        y += 72
    if ev.get("offer"):
        f = fit(lang, ev["offer"], W - 200, 46)
        bw = f.getbbox(ev["offer"])[2] + 80
        d.rounded_rectangle([W / 2 - bw / 2, 1010, W / 2 + bw / 2, 1090], radius=40, fill=(255, 210, 90), outline=(120, 30, 0), width=3)
        d.text((W / 2, 1050), ev["offer"], font=f, fill=(110, 20, 10), anchor="mm")
    if ev.get("date_label"):
        text_c(d, 1325, ev["date_label"], sans(30), (255, 230, 170), shadow=False)
    footer(bg, lang)
    bg.convert("RGB").save(out, quality=95)
    return out


if __name__ == "__main__":
    events = json.loads(Path(sys.argv[1]).read_text())
    outdir = Path(sys.argv[2]); outdir.mkdir(parents=True, exist_ok=True)
    for ev in events:
        p = outdir / f"{ev['date']}_{ev['slug']}_{ev['lang']}.jpg"
        render(ev, p)
        print(p)
