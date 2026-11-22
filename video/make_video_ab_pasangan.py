"""Video 12 dtk 1080x1920 bentuk cerita 'A vs B': dua pasangan, dua pilihan, satu kalimat penutup.
Referensi gaya: video 'Kamu yang mana' (dua panel kamar, jam digital merah, stick figure, bubble pendek).
Cerita: sama-sama dibilang 'kamu cuek' -> Pasangan A menyangkal, Pasangan B mendengarkan -> jam 01.42.
Penutup: 'SAMA MASALAHNYA. BEDA CARA MENDENGARNYA.' (+ ajakan 'kamu yang mana?')."""
import importlib.util, math, os, subprocess, sys, wave
import numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv, _argv = [sys.argv[0]], sys.argv
spec = importlib.util.spec_from_file_location("mv", HERE + "/make_video.py")
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)
sys.argv = _argv
OUT = sys.argv[1] if len(sys.argv) > 1 else "ab-pasangan.mp4"
W, H, FPS, DUR, S = 1080, 1920, 30, 12, 2
PW, PH = 1080, 600
F, WHITE, GREY, GOLD = mv.F, mv.WHITE, mv.GREY, mv.GOLD
seg, clamp, fade, text_c = mv.seg, mv.clamp, mv.fade, mv.text_c
RED, GREEN = (255, 120, 110), (110, 220, 150)
FLOOR = 520
BG_T, BG_B = (20, 24, 38), (40, 44, 58)
WHITE_C, GREY_C = (240, 240, 244), (170, 172, 182)

def lerp(a, b, p): return a + (b - a) * clamp(p)

# ---------- stick figure ----------
def fig(d, x, base, col, kind="stand", lean=0.0, arms=((38, 48), (-28, 70)), walk=0.0, face=1, y_lie=0):
    lw = int(10 * S)
    def L(*pts): d.line([(px * S, py * S) for px, py in pts], fill=col, width=lw, joint="curve")
    def head(c, r=30): d.ellipse([(c[0] - r) * S, (c[1] - r) * S, (c[0] + r) * S, (c[1] + r) * S], fill=col)
    if kind == "stand":
        hip = (x, base - 122); sh = (x + face * lean * 14, base - 215); hd = (sh[0] + face * lean * 8, sh[1] - 36)
        sw = math.sin(walk) * 26
        L(hip, (x - 18 + sw, base)); L(hip, (x + 18 - sw, base)); L(hip, sh)
        for dx, dy in arms: L(sh, (sh[0] + face * dx, sh[1] + dy))
        head(hd); return {"sh": sh, "hd": hd}
    if kind == "sit":
        hip = (x, base - 62); knee = (x + face * 52, base - 62); foot = (x + face * 52, base)
        sh = (x + face * lean * 18, hip[1] - 92); hd = (sh[0] + face * lean * 12, sh[1] - 32 + lean * 8)
        L(hip, knee, foot); L(hip, sh)
        L(sh, (knee[0] - face * 10, knee[1] - 20)); head(hd); return {"sh": sh, "hd": hd}
    if kind == "lie":
        y = y_lie
        L((x - 50, y), (x + 70, y)); L((x + 70, y), (x + 150, y + 4))
        L((x - 40, y), (x - 10, y + 22))
        head((x - 82, y - 6)); return {"sh": (x - 50, y), "hd": (x - 82, y - 6)}

# ---------- latar kamar ----------
def room(img, t, door_open, lamp_on):
    d = ImageDraw.Draw(img)
    for y in range(0, FLOOR * S, 8):  # gradasi dinding
        p = y / (FLOOR * S); c = tuple(int(BG_T[i] + (BG_B[i] - BG_T[i]) * p) for i in range(3))
        d.rectangle([0, y, PW * S, y + 8], fill=c)
    d.rectangle([0, FLOOR * S, PW * S, PH * S], fill=(58, 60, 70)); d.line([0, FLOOR * S, PW * S, FLOOR * S], fill=(96, 98, 110), width=2 * S)
    # jendela + bulan + gorden
    d.rectangle([230 * S, 80 * S, 430 * S, 300 * S], fill=(16, 22, 46), outline=(110, 116, 140), width=3 * S)
    d.ellipse([360 * S, 110 * S, 396 * S, 146 * S], fill=(236, 236, 214))
    for k, (bx, bh) in enumerate([(250, 50), (290, 90), (330, 60), (372, 100), (404, 40)]):
        d.rectangle([bx * S, (300 - bh) * S, (bx + 30) * S, 300 * S], fill=(26, 32, 58))
    d.line([330 * S, 80 * S, 330 * S, 300 * S], fill=(110, 116, 140), width=2 * S)
    d.polygon([(222 * S, 74 * S), (258 * S, 74 * S), (250 * S, 304 * S), (222 * S, 304 * S)], fill=(52, 62, 104))
    d.polygon([(402 * S, 74 * S), (438 * S, 74 * S), (438 * S, 304 * S), (410 * S, 304 * S)], fill=(52, 62, 104))
    # lemari kecil kiri
    d.rectangle([-10 * S, 380 * S, 40 * S, FLOOR * S], fill=(38, 40, 52))
    # tempat tidur
    d.rectangle([40 * S, 462 * S, 440 * S, FLOOR * S], fill=(46, 58, 98))
    d.rectangle([40 * S, 462 * S, 440 * S, 478 * S], fill=(210, 214, 228))
    d.rectangle([30 * S, 400 * S, 50 * S, FLOOR * S], fill=(60, 50, 44))
    # meja kecil + lampu
    d.rectangle([450 * S, 470 * S, 500 * S, FLOOR * S], fill=(40, 40, 52))
    d.polygon([(458 * S, 440 * S), (492 * S, 440 * S), (484 * S, 410 * S), (466 * S, 410 * S)], fill=(250, 214, 140) if lamp_on else (80, 76, 70))
    d.line([475 * S, 440 * S, 475 * S, 470 * S], fill=(120, 120, 130), width=3 * S)
    # pintu
    dx0, dx1 = 860, 990
    if door_open > 0.02:
        d.rectangle([dx0 * S, 150 * S, dx1 * S, FLOOR * S], fill=(236, 214, 160))
        wdt = (dx1 - dx0) * (1 - door_open) * 0.9
        d.rectangle([(dx1 - wdt) * S, 150 * S, dx1 * S, FLOOR * S], fill=(36, 38, 50))
        spill = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(spill).polygon([(dx0 * S, FLOOR * S), (dx1 * S, FLOOR * S), ((dx1 - 330) * S, PH * S), ((dx0 - 330) * S, PH * S)], fill=(255, 224, 160, int(60 * door_open)))
        img.paste(spill, (0, 0), spill)
    else:
        d.rectangle([dx0 * S, 150 * S, dx1 * S, FLOOR * S], fill=(34, 36, 48), outline=(66, 70, 88), width=2 * S)
        d.rectangle([dx0 * S + 18 * S, 180 * S, dx1 * S - 18 * S, 300 * S], outline=(56, 60, 78), width=2 * S)
    d.ellipse([(dx0 + 12) * S, 330 * S, (dx0 + 22) * S, 340 * S], fill=(150, 150, 160))
    return ImageDraw.Draw(img)

CLOCK = [(0, "21:30"), (3.4, "21:31"), (4.6, "22:48"), (5.6, "23:59"), (6.8, "01:40"), (8.0, "01:42")]
def clock(t):
    s = CLOCK[0][1]
    for a, c in CLOCK:
        if t >= a: s = c
    return s

# ---------- panel ----------
def panel(t, which):
    img = Image.new("RGB", (PW * S, PH * S), BG_T)
    A = which == "A"
    # status pintu / lampu
    if A: door = 1 - seg(t, 5.6, 6.0)
    else: door = 1 - seg(t, 8.6, 9.0)
    lamp = (not A) and t >= 5.6
    d = room(img, t, door, lamp)
    if lamp:
        gl = mv.glow_layer(img.size, (475 * S, 420 * S), 260 * S, (255, 214, 140), 0.6 * seg(t, 5.6, 6.0)); img.paste(gl, (0, 0), gl); d = ImageDraw.Draw(img)
    # posisi tokoh
    big = F(30 * S)
    wx, gx = 560, 830
    if A:
        # putih: berdiri -> jalan ke ranjang -> duduk -> berdiri ke jendela
        if t < 4.4: kind, x, walk, lean = "stand", wx, 0, 0
        elif t < 5.4: kind, x, walk, lean = "stand", lerp(wx, 395, seg(t, 4.4, 5.4)), t * 9, 0
        elif t < 8.4: kind, x, walk, lean = "sit", 395, 0, 0.6 + 0.4 * seg(t, 5.8, 7.0)
        elif t < 9.4: kind, x, walk, lean = "stand", lerp(395, 330, seg(t, 8.4, 9.4)), t * 9, 0
        else: kind, x, walk, lean = "stand", 330, 0, -0.4
        arms = ((38, 48), (-28, 70)) if kind == "stand" else None
        col = fade(WHITE_C, 1 - 0.25 * seg(t, 6, 9))
        if kind == "sit": fig(d, x, FLOOR, col, "sit", lean=lean)
        else: fig(d, x, FLOOR, col, "stand", lean=lean, walk=walk, arms=((38, 48), (-28, 70)) if t < 4.4 else ((18, 70), (-18, 70)))
        # abu-abu (pasangan) keluar lewat pintu
        if t < 4.4: gxx, gwalk = gx, 0
        else: gxx, gwalk = lerp(gx, 925, seg(t, 4.6, 5.5)), t * 9
        if gxx < 905: fig(d, gxx, FLOOR, GREY_C, "stand", walk=gwalk, face=-1 if t < 4.6 else 1, arms=((30, 50), (-20, 70)) if t < 4.4 else ((18, 70), (-18, 70)))
    else:
        if t < 4.4: wk, wxx, wl, wwalk = "stand", wx, 0, 0
        elif t < 5.2: wk, wxx, wl, wwalk = "stand", lerp(wx, 330, seg(t, 4.4, 5.2)), 0, t * 9
        elif t < 7.0: wk, wxx, wl, wwalk = "sit", 330, 0.2 + 0.5 * seg(t, 5.6, 6.4), 0
        else: wk, wxx, wl, wwalk = "lie", 220, 0, 0
        col = WHITE_C
        gcol = GREY_C
        if t < 4.4: gk, gxx, gwalk, gface = "stand", gx, 0, -1
        elif t < 5.4: gk, gxx, gwalk, gface = "stand", lerp(gx, 430, seg(t, 4.4, 5.4)), t * 9, -1
        elif t < 7.4: gk, gxx, gwalk, gface = "sit", 410, 0, -1
        elif t < 8.8: gk, gxx, gwalk, gface = "stand", lerp(410, 925, seg(t, 7.4, 8.6)), t * 9, 1
        else: gk, gxx, gwalk, gface = "stand", 925, 0, 1
        if wk == "lie":
            fig(d, wxx, FLOOR, col, "lie", y_lie=452)
            for k in range(3):
                zt = (t * 0.7 + k * 0.33) % 1.0
                d.text(((250 + zt * 40 + k * 14) * S, (400 - zt * 80) * S), "z", font=F(int((18 + 9 * k) * S)), fill=fade(GREY, 1 - zt, BG_T), anchor="mm")
        else:
            fig(d, wxx, FLOOR, col, wk, lean=wl, walk=wwalk, arms=((38, 48), (-28, 70)) if t < 4.4 else ((18, 70), (-18, 70)))
        if gxx < 905:
            gi = fig(d, gxx, FLOOR, gcol, gk, lean=0.5 if gk == "sit" else 0, walk=gwalk, face=gface, arms=((30, 50), (-20, 70)) if t < 4.4 else ((18, 70), (-18, 70)))
            if gk == "sit" and wk == "sit":  # pelukan
                lw = int(10 * S)
                wsh = (330 + 0.2 * 18 + 6, FLOOR - 62 - 92)
                d.line([(gi["sh"][0] * S, gi["sh"][1] * S), ((wsh[0] - 12) * S, (wsh[1] + 26) * S)], fill=gcol, width=lw)
                d.line([(wsh[0] * S, wsh[1] * S), ((gi["sh"][0] + 14) * S, (gi["sh"][1] + 26) * S)], fill=col, width=lw)
    # bubble
    def bub(x, y, txt, a, fill, line=None):
        w = d.textlength(txt, font=big) + 44 * S
        yy = (y - 14 * (1 - a)) * S
        d.rounded_rectangle([x * S, yy, x * S + w, yy + 62 * S], 22 * S, fill=fade(fill, a, BG_B), outline=fade(line, a, BG_B) if line else None, width=2 * S if line else 0)
        d.text((x * S + 22 * S, yy + 31 * S), txt, font=big, fill=fade(WHITE, a, BG_B), anchor="lm")
    a = seg(t, 1.0, 1.3) * (1 - seg(t, 4.4, 4.8))
    if a > 0: bub(430, 60, "Kamu akhir-akhir ini cuek.", a, (36, 110, 190))
    a = seg(t, 2.8, 3.1) * (1 - seg(t, 4.6, 5.0))
    if a > 0:
        if A: bub(600, 135, "Perasaanmu aja.", a, (84, 46, 46), RED)
        else: bub(520, 135, "Ceritain. Aku dengerin.", a, (36, 84, 60), GREEN)
    if not A:
        a = seg(t, 6.0, 6.3) * (1 - seg(t, 7.2, 7.5))
        if a > 0: bub(300, 100, "Makasih udah bilang.", a, (36, 110, 190))
    else:
        a = seg(t, 9.6, 9.9)
        if a > 0: d.text((410 * S, 150 * S), "...", font=F(60 * S), fill=fade(GREY, a, BG_B), anchor="lm")
    # label panel
    d.text((30 * S, 40 * S), "PASANGAN " + which, font=F(30 * S), fill=WHITE, anchor="lm")
    a = seg(t, 3.0, 3.4)
    if a > 0:
        d.text((30 * S, 80 * S), "MENYANGKAL" if A else "MENDENGAR", font=F(22 * S), fill=fade(RED if A else GREEN, a, BG_T), anchor="lm")
    img = img.resize((PW, PH), Image.LANCZOS)
    # vignette tipis
    return img

CAPS = [(1.0, 2.8, "Sama-sama dibilang: kamu cuek."), (3.0, 4.6, "A: \"Perasaanmu aja.\""), (4.6, 7.0, "A pergi. B duduk dan memeluk."),
        (7.0, 9.8, "Jam 01.42. Satu tidur, satu terjaga.")]

def caption(img, t):
    d = ImageDraw.Draw(img)
    for a, b, s in CAPS:
        if a <= t < b:
            al = min(seg(t, a, a + 0.2), 1 - seg(t, b - 0.15, b))
            f = F(46); tw = d.textlength(s, font=f)
            if tw > 1000: f = F(int(46 * 1000 / tw))
            text_c(d, (W / 2, 1765), s, f, fade(WHITE, al), sp=0)
            return

def frame(i):
    t = i / FPS
    img = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(img)
    a = seg(t, 0, 0.3)
    text_c(d, (W / 2, 150), "DUA PASANGAN.", F(72), fade(WHITE, a), sp=6)
    text_c(d, (W / 2, 240), "SATU MASALAH.", F(72), fade(GOLD, a), sp=6)
    dim = 1 - seg(t, 9.8, 10.4)
    pa, pb = panel(t, "A"), panel(t, "B")
    blk = Image.new("RGB", pa.size, (0, 0, 0))
    s = seg(t, 0.4, 1.0)
    for p, y in ((pa, 330), (pb, 990)):
        q = Image.blend(blk, p, min(s, dim)) if min(s, dim) < 1 else p
        img.paste(q, (0, int(y + 24 * (1 - s))))
    d = ImageDraw.Draw(img)
    if s > 0.5 and dim > 0.05:
        c = clock(t)
        for y in (950, 1610):
            text_c(d, (W / 2, y), c, F(40), fade(RED, dim), sp=8)
    if t >= 10.2:
        def line(txt, y, a0, col=WHITE, font=None, sp=5):
            a = seg(t, a0, a0 + 0.4)
            if a > 0: text_c(d, (W / 2, y + 20 * (1 - a)), txt, font or F(80), fade(col, a), sp=sp)
        line("SAMA MASALAHNYA.", 820, 10.2, font=F(70))
        line("BEDA CARA MENDENGARNYA.", 940, 10.5, col=GOLD, font=F(48))
        line("kamu yang mana? A atau B?", 1090, 11.0, col=GREY, font=F(34, False), sp=2)
    else:
        caption(img, t)
    return img

def build_audio(path, sr=44100):
    n = sr * DUR; t = np.arange(n) / sr; a = np.zeros(n); rng = np.random.default_rng(5)
    for s, e, fs in [(0, 5.6, [110, 130.8, 164.8]), (5.6, 10, [98, 130.8, 164.8, 196]), (10, 12, [130.8, 196, 261.6, 329.6])]:
        m = (t >= s) & (t < e); env = np.clip((t - s) / 1.0, 0, 1) * np.clip((e - t) / 1.0, 0, 1)
        for f in fs: a += np.where(m, np.sin(2 * np.pi * f * t) * env * 0.05, 0)
    def add(at, w):
        i0 = int(at * sr)
        if i0 < n: a[i0:i0 + len(w)] += w[: n - i0]
    def tone(at, f, dur, vol, decay=8, f2=None):
        tt = np.arange(int(dur * sr)) / sr; ff = f if f2 is None else f + (f2 - f) * tt / dur
        add(at, np.sin(2 * np.pi * np.cumsum(ff) / sr) * np.exp(-decay * tt) * vol)
    def noise(at, dur, vol, decay=10, lp=1):
        tt = np.arange(int(dur * sr)) / sr; w = rng.standard_normal(len(tt))
        if lp > 1: w = np.convolve(w, np.ones(lp) / lp, "same")
        add(at, w * np.exp(-decay * tt) * vol)
    tone(0.05, 55, 0.8, 0.35, 4)                                              # hit judul
    tone(1.0, 700, 0.15, 0.15, 25); tone(1.1, 900, 0.2, 0.12, 20)             # bubble pertama
    tone(2.8, 700, 0.15, 0.15, 25); tone(2.9, 500, 0.4, 0.14, 8, 380)         # balasan A/B
    for k, tt_ in enumerate(np.arange(3.4, 8.0, 0.35 if True else 0.5)):      # tik jam
        tone(tt_, 1800 if k % 2 == 0 else 1300, 0.05, 0.1, 80)
    noise(5.5, 0.5, 0.12, 6, 60); tone(5.6, 90, 0.3, 0.3, 20)                  # pintu A tertutup
    tone(5.6, 1200, 0.1, 0.1, 40)                                              # lampu B klik
    tone(6.0, 440, 1.4, 0.1, 2); tone(6.0, 554.4, 1.4, 0.08, 2)                # hangat saat B memeluk
    for k in range(4): tone(7.4 + k * 0.9, 85 + k % 2 * 10, 0.8, 0.04, 2)      # tidur
    noise(8.6, 0.4, 0.1, 6, 60); tone(8.8, 90, 0.3, 0.25, 20)                  # pintu B tertutup pelan
    tone(10.2, 55, 1.2, 0.4, 3); noise(10.2, 0.4, 0.15, 12, 40)               # hit penutup
    for f in (523.3, 659.3, 784): tone(10.5, f, 1.5, 0.12, 2)
    a = np.tanh(a * 1.3); a[-sr // 2:] *= np.linspace(1, 0, sr // 2)
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a * 32000).astype(np.int16).tobytes())

def work(a): i, tmp = a; frame(i).save(f"{tmp}/{i:04d}.png")

if __name__ == "__main__":
    tmp = os.path.dirname(os.path.abspath(OUT)) + "/_frames_ab"; os.makedirs(tmp, exist_ok=True)
    only = os.environ.get("ONLY")
    if only:
        for tt in only.split(","): frame(int(float(tt) * FPS)).save(f"{tmp}/_p{tt}.png")
        print("preview"); sys.exit()
    with Pool(4) as p: p.map(work, [(i, tmp) for i in range(FPS * DUR)], chunksize=10)
    build_audio(tmp + "/a.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", tmp + "/%04d.png", "-i", tmp + "/a.wav",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "160k", "-shortest",
                    "-movflags", "+faststart", OUT], check=True)
    print("ok")
