"""Foto 1080x1350 niche cinta, gaya editorial gelap: latar siluet monokrom bergrain, teks tebal + aksen limau,
lencana teks melingkar, grid titik, kartu callout. (Gaya diambil dari referensi; semua elemen digambar sendiri.)
Pakai: python3 make_foto_v2.py <folder-keluaran>"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
W, H, S = 1080, 1350, 2
FD = "/usr/share/fonts/opentype/inter/"
def F(sz, w="InterDisplay-Black"): return ImageFont.truetype(FD + w + ".otf", int(sz * S))
LIME, WHITE, GREY, RED = (206, 246, 62), (246, 246, 248), (176, 180, 190), (255, 104, 96)
BRAND = "Animasiredflag"

# ---------- latar: siluet monokrom + grain ----------
def photo_bg(kind, seed, light_at=(900, 140), dx=0):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    light = 52 + 82 * np.clip(1 - np.hypot(xx - light_at[0], yy - light_at[1]) / 900, 0, 1) ** 1.2          # cahaya dari kanan atas
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    def person(cx, head_y, scale, tilt=0, bun=True):
        r = 86 * scale
        d.ellipse([cx - r + tilt, head_y - r, cx + r + tilt, head_y + r], fill=255)                 # kepala
        if bun: d.ellipse([cx - r * 0.55 + tilt, head_y - r * 1.45, cx + r * 0.55 + tilt, head_y - r * 0.5], fill=255)
        d.rectangle([cx - r * 0.4 + tilt * 0.5, head_y + r * 0.6, cx + r * 0.4 + tilt * 0.5, head_y + r * 1.5], fill=255)  # leher
        d.ellipse([cx - r * 2.2, head_y + r * 1.1, cx + r * 2.2, head_y + r * 3.4], fill=255)         # bahu
        d.rectangle([cx - r * 2.05, head_y + r * 2.2, cx + r * 2.05, H], fill=255)                  # badan
    if kind == 1:   # dua orang berdekatan, saling condong
        person(700 + dx, 470, 1.0, tilt=14); person(900 + dx, 520, 0.95, tilt=-16, bun=False)
    else:           # dua orang saling membelakangi, celah terang di tengah
        person(660 + dx, 470, 1.0, tilt=-10); person(960 + dx, 470, 0.95, tilt=10, bun=False)
    mk = np.asarray(m.filter(ImageFilter.GaussianBlur(4)), dtype=np.float32) / 255
    rim = np.clip(np.asarray(m.filter(ImageFilter.GaussianBlur(9)), dtype=np.float32) / 255 - mk, 0, 1)
    img = light * (1 - mk) + 18 * mk
    if kind == 2: img += 90 * np.exp(-((xx - (810 + dx)) / 36) ** 2) * (1 - mk)                         # celah cahaya
    img += 55 * np.asarray(Image.fromarray((rim * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)), dtype=np.float32) / 255
    for _ in range(5):                                                                          # bokeh
        cx, cy, r = rng.integers(500, 1080), rng.integers(40, 420), rng.integers(30, 80)
        img += 26 * np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)))
    img += rng.normal(0, 8, (H, W))                                                             # grain
    grad = np.clip((xx - 80) / 800, 0, 1) * 0.65 + 0.35                                           # gelap di kiri untuk teks
    low = np.clip((yy - 700) / 500, 0, 1)                                                        # gelap di bawah
    img = img * grad * (1 - 0.8 * low)
    vig = 1 - 0.55 * np.clip((np.hypot(xx - W / 2, yy - H / 2) - 450) / 500, 0, 1)
    img = np.clip(img * vig, 0, 255).astype(np.uint8)
    return Image.fromarray(img, "L").convert("RGBA")

# ---------- elemen ----------
def overlay(): return Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
def T(d, x, y, s, f, col, anchor="ls"): d.text((x * S, y * S), s, font=f, fill=col, anchor=anchor)
def rr(d, x0, y0, x1, y1, r, fill=None, out=None, w=2): d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], r * S, fill=fill, outline=out, width=int(w * S))
def circle_text(ov, cx, cy, R, text, f, col):
    n = len(text)
    for i, ch in enumerate(text):
        th = 2 * math.pi * i / n - math.pi / 2
        tmp = Image.new("RGBA", (160, 160), (0, 0, 0, 0)); ImageDraw.Draw(tmp).text((80, 80), ch, font=f, fill=col, anchor="mm")
        tmp = tmp.rotate(-math.degrees(th) - 90, resample=Image.BICUBIC)
        ov.paste(tmp, (int((cx + R * math.cos(th)) * S - 80), int((cy + R * math.sin(th)) * S - 80)), tmp)
def dots(d, x, y, n=8, gap=15, r=2.6, col=LIME):
    for i in range(n):
        for j in range(n): d.ellipse([(x + i * gap - r) * S, (y + j * gap - r) * S, (x + i * gap + r) * S, (y + j * gap + r) * S], fill=col)
def flag(d, x, y, col, s=1.0):
    d.line([x * S, y * S, x * S, (y + 58 * s) * S], fill=WHITE, width=int(4.5 * S))
    d.polygon([(x * S, y * S), ((x + 46 * s) * S, (y + 14 * s) * S), (x * S, (y + 28 * s) * S)], fill=col)
def wrap(d, s, f, maxw):
    words, lines, cur = s.split(" "), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f) > maxw * S and cur: lines.append(cur); cur = w_
        else: cur = t
    return lines + [cur]
def chrome(ov, d, label):
    circle_text(ov, 150, 150, 80, label, F(17, "InterDisplay-Bold"), LIME)
    T(d, W - 70, 1300, BRAND, F(28, "InterDisplay-Bold"), LIME, "rs")
def finish(bg, ov, path):
    ov = ov.resize((W, H), Image.LANCZOS)
    Image.alpha_composite(bg, ov).convert("RGB").save(path, quality=93, subsampling=0)

# ---------- foto 1: 5 ciri ----------
def foto1(path):
    bg = photo_bg(1, 11); ov = overlay(); d = ImageDraw.Draw(ov)
    chrome(ov, d, "CERITA CINTA · GREEN FLAG · CERITA CINTA · GREEN FLAG · ")
    T(d, 70, 560, "5 CIRI", F(104), LIME); T(d, 70, 664, "PASANGAN", F(104), WHITE); T(d, 70, 768, "YANG SEHAT.", F(104), WHITE)
    d.rectangle([70 * S, 790 * S, 330 * S, 797 * S], fill=LIME)
    items = ["Memberi kabar saat sibuk", "Minta maaf tanpa disuruh", "Mau mendengar, bukan menyela", "Tidak membuatmu menebak-nebak", "Konsisten, bukan cuma manis di awal"]
    y = 870
    for i, s in enumerate(items, 1):
        T(d, 70, y, f"{i:02d}", F(34, "InterDisplay-Black"), LIME); T(d, 150, y, s, F(36, "Inter-SemiBold"), WHITE); y += 58
    rr(d, 70, 1170, 760, 1256, 22, fill=LIME)
    T(d, 100, 1222, "Mana yang sudah kamu temukan? Tulis angkanya.", F(25, "Inter-Bold"), (22, 30, 12))
    dots(d, 880, 1130)
    finish(bg, ov, path)

# ---------- foto 2: red vs green saat bertengkar ----------
def foto2(path):
    bg = photo_bg(2, 23); ov = overlay(); d = ImageDraw.Draw(ov)
    chrome(ov, d, "SAAT BERTENGKAR · RED FLAG · GREEN FLAG · SAAT BERTENGKAR · ")
    T(d, 70, 560, "RED FLAG", F(96), WHITE); d.rectangle([70 * S, 578 * S, 520 * S, 586 * S], fill=RED)
    T(d, 70, 676, "vs", F(60, "InterDisplay-Bold"), GREY)
    gw = d.textlength("GREEN FLAG", font=F(88)) / S
    rr(d, 70, 696, 70 + gw + 40, 792, 8, fill=LIME); T(d, 90, 770, "GREEN FLAG", F(88), (18, 26, 10))
    cols = [(RED, "Pergi membanting pintu", "Diam berhari-hari", "Menyalahkan terus", "Mengungkit masa lalu"),
            (LIME, "Minta waktu, lalu kembali", "Bilang apa yang dirasakan", "Fokus ke masalah", "Mengaku saat salah")]
    for ci, (col, *its) in enumerate(cols):
        x0 = 70 + ci * 490
        rr(d, x0, 835, x0 + 460, 1150, 22, fill=(8, 10, 14, 175), out=col, w=2)
        flag(d, x0 + 28, 858, col, 0.6); T(d, x0 + 88, 888, "RED FLAG" if ci == 0 else "GREEN FLAG", F(26, "InterDisplay-Black"), col)
        y = 940
        for s in its:
            T(d, x0 + 30, y, "—", F(30, "InterDisplay-Black"), col); T(d, x0 + 72, y, s, F(27, "Inter-SemiBold"), WHITE); y += 52
    rr(d, 70, 1180, 760, 1262, 22, fill=LIME)
    T(d, 100, 1230, "Kamu lebih sering di sisi yang mana? Komen A atau B.", F(24, "Inter-Bold"), (22, 30, 12))
    dots(d, 905, 1182, n=5)
    finish(bg, ov, path)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    foto1(os.path.join(OUT, "foto-5-ciri-green-flag.jpg")); foto2(os.path.join(OUT, "foto-red-vs-green-bertengkar.jpg"))
    print("ok")
