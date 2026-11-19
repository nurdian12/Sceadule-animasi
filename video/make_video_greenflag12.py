"""Video percobaan 12 dtk 1080x1920: 'Green flag itu sederhana' (hook relatable, format pendek, ajakan share).
Hasil riset TikTok/FB: durasi 10-15 dtk, kalimat pembuka kena di detik 1-2, ajakan share/simpan. Pakai helper make_video.py."""
import importlib.util, math, os, subprocess, sys, wave
import numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv, _argv = [sys.argv[0]], sys.argv
spec = importlib.util.spec_from_file_location("mv", HERE + "/make_video.py")
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)
sys.argv = _argv
SCN = {
 "minta-maaf": ("ITU MAU MINTA MAAF.", "kemarin kamu kok gitu?", "ah lebay banget kamu", "maaf ya, aku salah", "DIA YANG MENYANGKAL", "DIA YANG MENGAKUI",
                "BUKAN YANG TAK PERNAH SALAH.", "TAPI YANG MAU MENGAKUI.", ["Ditanya baik-baik, dibilang lebay.", "Yang ini langsung minta maaf."]),
 "mendengar": ("ITU MAU MENDENGAR.", "aku lagi capek banget", "ya semua orang capek", "sini cerita, aku dengerin", "DIA YANG MENYEPELEKAN", "DIA YANG MENDENGAR",
               "BUKAN YANG PUNYA SOLUSI.", "TAPI YANG MAU MENDENGAR.", ["Curhat dibalas, semua orang capek.", "Yang ini bilang: sini cerita."]),
 "kejelasan": ("ITU KEJELASAN.", "kita ini apa sih?", "jalanin aja dulu", "aku serius, pelan-pelan ya", "DIA YANG MENGGANTUNG", "DIA YANG JELAS",
               "BUKAN YANG JANJI MANIS.", "TAPI YANG JELAS ARAHNYA.", ["Ditanya status, jawabnya mengambang.", "Yang ini jujur soal arahnya."]),
 "ruang": ("ITU MEMBERI RUANG.", "aku butuh waktu sendiri dulu", "kamu jahat banget", "oke, kabarin kalau siap", "DIA YANG MENAHAN", "DIA YANG MEMBERI RUANG",
           "BUKAN YANG MENAHAN.", "TAPI YANG MEMBERI RUANG.", ["Minta waktu sendiri, dibilang jahat.", "Yang ini: kabarin kalau siap."]),
}
KEY = os.environ.get("SCN")  # kosong = versi asli 'sederhana' (hilang vs ngasih kabar)
OUT = sys.argv[1] if len(sys.argv) > 1 else "greenflag-12detik.mp4"
W, H, FPS, DUR, S, PW, PH = mv.W, 1920, 30, 12, mv.S, mv.PW, mv.PH
F, WHITE, GREY, GOLD, BLUE = mv.F, mv.WHITE, mv.GREY, mv.GOLD, mv.BLUE
seg, clamp, fade, text_c = mv.seg, mv.clamp, mv.fade, mv.text_c
RED, GREEN, BG = (255, 120, 110), (110, 220, 150), (12, 16, 28)

def flag(d, x, y, col, s=1.0):
    d.line([x, y, x, y + 60 * s * S], fill=WHITE, width=int(4 * S))
    d.polygon([(x, y), (x + 46 * s * S, y + 14 * s * S), (x, y + 28 * s * S)], fill=col)

def panel(t, which):
    img = Image.new("RGB", (PW * S, PH * S), BG); d = ImageDraw.Draw(img)
    cx = (600 if which == "A" else 680) * S
    cone = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(cone).polygon([(cx - 40 * S, 0), (cx + 40 * S, 0), (cx + 230 * S, 520 * S), (cx - 230 * S, 520 * S)], fill=(150, 170, 220, 22))
    img.paste(cone, (0, 0), cone); d = ImageDraw.Draw(img)
    floor = (PH - 90) * S; base = PH - 90
    d.rectangle([0, floor, PW * S, PH * S], fill=(62, 64, 72)); d.line([0, floor, PW * S, floor], fill=(110, 112, 122), width=2 * S)
    big = F(28 * S)
    if KEY:
        _, q, ra, ga, la, lb, *_ = SCN[KEY]
        if which == "A":
            flag(d, 40 * S, 22 * S, RED, 0.8); d.text((110 * S, 40 * S), la, font=F(24 * S), fill=WHITE, anchor="lm")
            hand = mv.figure(d, 200, base, WHITE, math.sin(t * 3) * 0.2 * (t > 2)); mv.phone(d, hand, 1, face=(60, 120, 200))
            a = seg(t, 2.2, 2.5)
            if a > 0: mv.bubble(d, 330 * S, (230 - 14 * (1 - a)) * S, q, big, (36, 110, 190), WHITE, alpha=a)
            a = seg(t, 3.6, 3.9)
            if a > 0:
                w = d.textlength(ra, font=big) + 44 * S
                d.rounded_rectangle([330 * S, (330 - 14 * (1 - a)) * S, 330 * S + w, (330 - 14 * (1 - a)) * S + 62 * S], 22 * S, fill=fade((70, 40, 40), a, BG), outline=fade(RED, a, BG), width=2 * S)
                d.text((352 * S, (361 - 14 * (1 - a)) * S), ra, font=big, fill=fade(WHITE, a, BG), anchor="lm")
            if t > 4.4: d.text((330 * S, 430 * S), "kamu jadi ragu sama diri sendiri.", font=F(22 * S, False), fill=RED, anchor="lm")
        else:
            flag(d, 40 * S, 22 * S, GREEN, 0.8); d.text((110 * S, 40 * S), lb, font=F(24 * S), fill=WHITE, anchor="lm")
            if t > 6.3:
                hand = mv.figure(d, 200, base, WHITE, math.sin(t * 3) * 0.2); mv.phone(d, hand, 1, face=(60, 120, 200))
            a = seg(t, 6.5, 6.8)
            if a > 0: mv.bubble(d, 330 * S, (230 - 14 * (1 - a)) * S, q, big, (36, 110, 190), WHITE, alpha=a)
            a = seg(t, 7.7, 8.0)
            if a > 0: mv.bubble(d, 330 * S, (330 - 14 * (1 - a)) * S, ga, big, (60, 62, 74), WHITE, alpha=a)
            if t > 8.4: d.text((330 * S, 430 * S), "tenang. gak perlu nebak-nebak.", font=F(22 * S, False), fill=GREEN, anchor="lm")
    elif which == "A":
        flag(d, 40 * S, 22 * S, RED, 0.8)
        d.text((110 * S, 40 * S), "DIA YANG HILANG", font=F(26 * S), fill=WHITE, anchor="lm")
        look = clamp((t - 2.2) / 4)
        hand = mv.figure(d, 200, base, WHITE, math.sin(t * (2 + 8 * look)) * (0.2 + look) * (t > 2), lean=look * 0.9)
        mv.phone(d, hand, 1, face=(60, 120, 200))
        a = seg(t, 2.2, 2.5)
        if a > 0: mv.bubble(d, 330 * S, (330 - 14 * (1 - a)) * S, "kamu lagi apa?", big, (36, 110, 190), WHITE, alpha=a)
        if t > 2.9: d.text((330 * S, 414 * S), "Dibaca", font=F(18 * S, False), fill=BLUE, anchor="lm")
        if t > 3.0:
            el = "+10 MENIT" if t < 4.2 else "+1 JAM" if t < 5.3 else "+6 JAM"
            d.text(((PW - 30) * S, 44 * S), el, font=F(40 * S), fill=RED, anchor="rm")
        a = seg(t, 5.8, 6.2)
        if a > 0: d.text((330 * S, 230 * S), "...", font=F(60 * S), fill=fade(GREY, a, BG), anchor="lm")
    else:
        flag(d, 40 * S, 22 * S, GREEN, 0.8)
        d.text((110 * S, 40 * S), "DIA YANG SIBUK TAPI NGASIH KABAR", font=F(24 * S), fill=WHITE, anchor="lm")
        if t > 6.3:
            hand = mv.figure(d, 200, base, WHITE, math.sin(t * 3) * 0.2)
            mv.phone(d, hand, 1, face=(60, 120, 200))
        a = seg(t, 6.5, 6.8)
        if a > 0: mv.bubble(d, 330 * S, (250 - 14 * (1 - a)) * S, "kamu lagi apa?", big, (36, 110, 190), WHITE, alpha=a)
        a = seg(t, 7.5, 7.8)
        if a > 0: mv.bubble(d, 330 * S, (340 - 14 * (1 - a)) * S, "lagi sibuk, nanti kukabarin ya", big, (60, 62, 74), WHITE, alpha=a)
        if t > 8.0:
            d.text(((PW - 30) * S, 44 * S), "2 MENIT", font=F(40 * S), fill=GREEN, anchor="rm")
            c = (80 * S, 0)
            d.text((330 * S, 450 * S), "tenang. gak perlu nebak-nebak.", font=F(22 * S, False), fill=GREEN, anchor="lm")
    img = img.resize((PW, PH), Image.LANCZOS)
    ImageDraw.Draw(img).rectangle([0, 0, PW - 1, PH - 1], outline=(40, 48, 66), width=2)
    return img

CAPS = [(2.0, 4.6, "Chat dibaca. Lalu hilang."), (4.6, 6.4, "6 jam. Nggak ada kabar."),
        (6.5, 9.9, "Sibuk, tapi bilang dulu.")]
if KEY: CAPS = [(2.0, 6.4, SCN[KEY][8][0]), (6.5, 9.9, SCN[KEY][8][1])]

def caption(img, t):
    d = ImageDraw.Draw(img)
    for a, b, s in CAPS:
        if a <= t < b:
            al = min(seg(t, a, a + 0.2), 1 - seg(t, b - 0.15, b))
            f = F(52)
            text_c(d, (W / 2, 1745), s, f, fade(WHITE, al), sp=0)
            return

def frame(i):
    t = i / FPS
    img = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(img)
    # hook besar sejak detik 0
    a = seg(t, 0.0, 0.3)
    text_c(d, (W / 2, 190), "GREEN FLAG", F(100), fade(GREEN, a), sp=6)
    sub = SCN[KEY][0] if KEY else "ITU SEDERHANA."
    text_c(d, (W / 2, 300), sub, F(min(80, int((900 / len(sub) - 6) / 0.6))), fade(WHITE, a), sp=6)
    dim = 1 - seg(t, 9.9, 10.5)
    pa, pb = panel(t, "A"), panel(t, "B")
    blk = Image.new("RGB", pa.size, (0, 0, 0))
    if dim < 1: pa, pb = Image.blend(blk, pa, dim), Image.blend(blk, pb, dim)
    s = seg(t, 0.5, 1.2)
    for p, y in ((pa, 420), (pb, 1040)):
        q = p if s >= 1 else Image.blend(blk, p, s)
        img.paste(q, (60, int(y + 30 * (1 - s))))
    d = ImageDraw.Draw(img)
    if t >= 10.2:
        d.rectangle([0, 700, W, 1300], fill=(0, 0, 0))
        def line(txt, y, a0, col=WHITE, font=None, sp=5):
            a = seg(t, a0, a0 + 0.4)
            if a > 0: text_c(d, (W / 2, y + 20 * (1 - a)), txt, font or F(80), fade(col, a), sp=sp)
        p1, p2 = (SCN[KEY][6], SCN[KEY][7]) if KEY else ("BUKAN CEPAT BALASNYA.", "TAPI ADA KABARNYA.")
        line(p1, 850, 10.2, font=F(min(58, int((1000 / len(p1) - 5) / 0.6))))
        line(p2, 960, 10.5, col=GREEN, font=F(min(64, int((1000 / len(p2) - 5) / 0.6))))
        line("share ke temanmu yang butuh dengar ini", 1100, 11.0, col=GREY, font=F(30, False), sp=2)
    caption(img, t)
    return img

def build_audio(path, sr=44100):
    n = sr * DUR; t = np.arange(n) / sr; a = np.zeros(n); rng = np.random.default_rng(11)
    for s, e, fs in [(0, 6.4, [110, 130.8, 164.8]), (6.4, 10, [130.8, 164.8, 196]), (10, 12, [130.8, 196, 261.6, 329.6])]:
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
    tone(0.05, 55, 0.8, 0.35, 4)                                             # hit hook
    noise(2.2, 0.3, 0.2, 7, 30); tone(2.25, 500, 0.3, 0.12, 8, 1400)         # kirim
    tone(2.9, 1500, 0.12, 0.2, 30); tone(2.98, 2000, 0.2, 0.18, 20)          # dibaca
    for k, tt_ in enumerate(np.arange(3.0, 6.4, 0.4)): tone(tt_, 1800 if k % 2 == 0 else 1300, 0.06, 0.12, 70)
    tone(5.8, 500, 0.5, 0.15, 3, 150)                                        # womp
    noise(6.5, 0.3, 0.2, 7, 30); tone(6.55, 500, 0.3, 0.12, 8, 1400)         # kirim 2
    tone(7.7 if KEY else 7.5, 660, 0.4, 0.22); tone(7.88 if KEY else 7.68, 880, 0.5, 0.2)
    if KEY: tone(3.6, 330, 0.5, 0.15, 5, 200)                     # balasan cepat
    for f in (523.3, 659.3, 784): tone(10.2, f, 1.6, 0.12, 2)                # resolusi
    a = np.tanh(a * 1.3); a[-sr // 2:] *= np.linspace(1, 0, sr // 2)
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a * 32000).astype(np.int16).tobytes())

def work(a): i, tmp = a; frame(i).save(f"{tmp}/{i:04d}.png")

if __name__ == "__main__":
    tmp = os.path.dirname(os.path.abspath(OUT)) + "/_frames_gf12_" + (KEY or "base"); os.makedirs(tmp, exist_ok=True)
    only = os.environ.get("ONLY")
    if only: frame(int(float(only) * FPS)).save(tmp + "/_preview.png"); print("preview"); sys.exit()
    with Pool(4) as p: p.map(work, [(i, tmp) for i in range(FPS * DUR)], chunksize=10)
    build_audio(tmp + "/a.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", tmp + "/%04d.png", "-i", tmp + "/a.wav",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "160k", "-shortest",
                    "-movflags", "+faststart", OUT], check=True)
    print("ok")
