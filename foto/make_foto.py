"""Dua postingan foto 1080x1350 (4:5), niche cinta: (1) 5 ciri green flag, (2) red flag vs green flag saat bertengkar.
Pakai: python3 make_foto.py <folder-keluaran>"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
W, H, S = 1080, 1350, 2
FD = "/usr/share/fonts/opentype/inter/"
def F(sz, w="Bold"): return ImageFont.truetype(FD + ("InterDisplay-" if w == "Bold" else "Inter-") + w + ".otf", int(sz * S))
WHITE, GREY, RED, GREEN, GOLD = (244, 244, 248), (150, 156, 172), (255, 112, 104), (104, 222, 148), (255, 196, 70)
CARD = (30, 34, 46)

def canvas():
    img = Image.new("RGB", (W * S, H * S)); d = ImageDraw.Draw(img)
    for y in range(0, H * S, 6):
        p = y / (H * S); c = tuple(int((14, 16, 24)[i] + ((22, 30, 38)[i] - (14, 16, 24)[i]) * p) for i in range(3)); d.rectangle([0, y, W * S, y + 6], fill=c)
    return img, d

def rr(d, x0, y0, x1, y1, r, fill=None, out=None, w=2): d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], r * S, fill=fill, outline=out, width=int(w * S))
def T(d, x, y, s, f, col, anchor="lm"): d.text((x * S, y * S), s, font=f, fill=col, anchor=anchor)
def wrap(d, s, f, maxw):
    words, lines, cur = s.split(" "), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f) > maxw * S and cur: lines.append(cur); cur = w_
        else: cur = t
    return lines + [cur]
def flag(d, x, y, col, s=1.0):
    d.line([x * S, y * S, x * S, (y + 64 * s) * S], fill=WHITE, width=int(5 * S))
    d.polygon([(x * S, y * S), ((x + 50 * s) * S, (y + 16 * s) * S), (x * S, (y + 32 * s) * S)], fill=col)
def footer(d, s):
    T(d, W / 2, 1262, s, F(30, "Medium"), GREY, "mm")
    T(d, W / 2, 1312, "Animasiredflag", F(26, "Medium"), (90, 96, 112), "mm")

def card1():
    img, d = canvas()
    rr(d, 70, 78, 70 + 250, 78 + 56, 28, fill=(24, 58, 44), out=GREEN, w=2); flag(d, 100, 90, GREEN, 0.5)
    T(d, 140, 106, "GREEN FLAG", F(26), GREEN)
    T(d, 70, 215, "5 ciri pasangan", F(78), WHITE); T(d, 70, 305, "yang sehat.", F(78), GREEN)
    items = ["Memberi kabar saat sibuk", "Minta maaf tanpa disuruh", "Mau mendengar, bukan menyela", "Tidak membuatmu menebak-nebak", "Konsisten, bukan cuma manis di awal"]
    y = 380
    for i, s in enumerate(items, 1):
        rr(d, 70, y, 1010, y + 146, 30, fill=CARD)
        d.ellipse([100 * S, (y + 33) * S, 180 * S, (y + 113) * S], fill=GREEN); T(d, 140, y + 73, str(i), F(44), (14, 30, 22), "mm")
        lines = wrap(d, s, F(40, "SemiBold"), 760)
        for k, l in enumerate(lines): T(d, 215, y + 73 + (k - (len(lines) - 1) / 2) * 50, l, F(40, "SemiBold"), WHITE)
        y += 146 + 22
    footer(d, "Mana yang sudah kamu temukan? Tulis angkanya di komentar.")
    return img.resize((W, H), Image.LANCZOS)

def card2():
    img, d = canvas()
    T(d, 70, 120, "SAAT BERTENGKAR", F(28), GOLD)
    T(d, 70, 215, "Red flag vs", F(78), WHITE); T(d, 70, 305, "green flag.", F(78), GREEN)
    cols = [("RED FLAG", RED, (64, 32, 36), ["Pergi sambil membanting pintu", "Diam berhari-hari", "Menyalahkan terus, bukan membahas masalah", "Mengungkit masa lalu"]),
            ("GREEN FLAG", GREEN, (26, 58, 44), ["Minta waktu, lalu kembali bicara", "Bilang apa yang dirasakan", "Fokus ke masalah, bukan orangnya", "Mengaku saat salah"])]
    for ci, (title, col, tint, items) in enumerate(cols):
        x0 = 70 + ci * 480; x1 = x0 + 460
        rr(d, x0, 360, x1, 440, 24, fill=tint, out=col, w=2); flag(d, x0 + 28, 372, col, 0.55); T(d, x0 + 88, 400, title, F(30), col)
        y = 462
        for s in items:
            rr(d, x0, y, x1, y + 170, 26, fill=CARD, out=tint, w=2)
            lines = wrap(d, s, F(34, "SemiBold"), 400)
            for k, l in enumerate(lines): T(d, x0 + 28, y + 85 + (k - (len(lines) - 1) / 2) * 44, l, F(34, "SemiBold"), WHITE)
            y += 170 + 18
    footer(d, "Kamu lebih sering di sisi yang mana? Komen A atau B.")
    return img.resize((W, H), Image.LANCZOS)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    card1().save(os.path.join(OUT, "foto-5-ciri-green-flag.jpg"), quality=93, subsampling=0)
    card2().save(os.path.join(OUT, "foto-red-vs-green-bertengkar.jpg"), quality=93, subsampling=0)
    print("ok")
