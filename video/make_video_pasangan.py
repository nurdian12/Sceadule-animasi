"""Seri 'A vs B' v2, 12 dtk 1080x1920: dua pasangan, dua pilihan, satu kalimat penutup.
Tata letak dua kolom berdampingan (bukan kamar bertumpuk); tiap cerita punya BENDA/visual sendiri
yang menunjukkan akibatnya (jembatan, ponsel, hati, payung, cangkir, tanaman, puzzle, baterai, sangkar, buku, kue, mangkuk).
Pakai: SCN=<kunci> python3 make_video_pasangan.py out.mp4   (ONLY=3.5,8 untuk pratinjau frame)."""
import importlib.util, math, os, subprocess, sys, wave
import numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv, _argv = [sys.argv[0]], sys.argv
spec = importlib.util.spec_from_file_location("mv", HERE + "/make_video.py")
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)
sys.argv = _argv
W, H, FPS, DUR, S = 1080, 1920, 30, 12, 2
CW, CH = 500, 1150
F, WHITE, GREY, GOLD = mv.F, mv.WHITE, mv.GREY, mv.GOLD
seg, clamp, fade, text_c = mv.seg, mv.clamp, mv.fade, mv.text_c
RED, GREEN = (255, 120, 110), (110, 220, 150)
BLUE = (36, 110, 190)
WHITE_C, GREY_C = (240, 240, 244), (170, 172, 182)
BG = {"A": ((40, 24, 32), (26, 16, 24)), "B": ((20, 38, 36), (14, 26, 26))}

# kunci: (hook baris-1, kalimat pembuka, balasan A, balasan B, label A, label B, hasil A, hasil B, penutup, benda)
SCN = {
 "cuek":     ("DIA MULAI CUEK.", "Kamu akhir-akhir ini cuek.", "Perasaanmu aja.", "Ceritain. Aku dengerin.", "MENYANGKAL", "MENDENGAR", "Perasaan dianggap sepele", "Perasaan didengar", "BEDA CARA MENDENGARNYA.", "jembatan"),
 "chat":     ("CHAT BELUM DIBALAS.", "Chat aku belum kamu balas.", "Aku kan sibuk.", "Maaf, aku bales sekarang.", "MENGELAK", "MENGAKUI", "Dibaca. Lalu hening.", "Dibalas dalam 2 menit", "BEDA CARA MENANGGAPINYA.", "ponsel"),
 "cemburu":  ("SAAT CEMBURU DATANG.", "Aku cemburu sama dia.", "Kamu berlebihan.", "Makasih udah jujur.", "MEREMEHKAN", "MENJELASKAN", "Hati jadi retak", "Hati jadi tenang", "BEDA CARA MENJELASKANNYA.", "hati"),
 "telat":    ("PASANGAN TELAT JEMPUT.", "Kamu telat jemput lagi.", "Gitu aja marah.", "Maaf, harusnya kukabari.", "MENYEPELEKAN", "MENGAKUI", "Dibiarkan kehujanan", "Dipayungi", "BEDA CARA MINTA MAAFNYA.", "payung"),
 "malam":    ("BERTENGKAR LARUT MALAM.", "Aku masih marah soal tadi.", "Terserah. Aku pergi.", "Lanjut besok ya.", "PERGI", "BERTAHAN", "Pintu dibanting", "Teh hangat untuk berdua", "BEDA CARA BERTAHANNYA.", "cangkir"),
 "kritik":   ("SAAT DIKRITIK.", "Caramu bicara bikin sakit.", "Kamu terlalu sensitif.", "Aku mau perbaiki ya.", "MENGEJEK", "MENERIMA", "Hubungan layu", "Hubungan tumbuh", "BEDA CARA MENERIMANYA.", "tanaman"),
 "debat":    ("SAAT BEDA PENDAPAT.", "Pendapatku beda sama kamu.", "Aku yang benar.", "Aku dengerin versimu.", "MAU MENANG", "MAU MEMAHAMI", "Saling menolak", "Saling melengkapi", "BEDA CARA MENGHADAPINYA.", "puzzle"),
 "capek":    ("SAAT PASANGAN CAPEK.", "Aku capek, butuh ngobrol.", "Aku juga capek!", "Sini, aku temani.", "MELAMPIASKAN", "MENEMANI", "Energi habis", "Energi terisi", "BEDA CARA MENEMANINYA.", "baterai"),
 "ruang":    ("SAAT MINTA RUANG.", "Besok aku main sama teman.", "Terserah.", "Seru-seruan, kabarin ya.", "TERSERAH", "MEMBERI RUANG", "Terkurung", "Bebas lalu pulang", "BEDA CARA MEMBERI RUANG.", "sangkar"),
 "masalalu": ("SAAT BERCERITA MASA LALU.", "Aku mau cerita masa laluku.", "Gak penting.", "Aku dengerin pelan-pelan.", "MENGABAIKAN", "MENDENGAR", "Cerita ditutup", "Cerita dibuka", "BEDA CARA MENDENGARNYA.", "buku"),
 "ultah":    ("ULANG TAHUN TERLUPA.", "Kamu lupa ulang tahunku.", "Kan aku sibuk.", "Maaf. Aku tebus ya.", "MENGELAK", "MENEBUS", "Hari berlalu begitu saja", "Dirayakan walau telat", "BEDA CARA MENEBUSNYA.", "kue"),
 "sakit":    ("SAAT PASANGAN SAKIT.", "Aku lagi gak enak badan.", "Minum obat aja.", "Kubawain bubur ya.", "MENYEPELEKAN", "MENEMANI", "Sendirian dengan obat", "Ditemani bubur hangat", "BEDA CARA MEMEDULIKANNYA.", "mangkuk"),
}
KEY = os.environ.get("SCN", "chat")
_S = SCN[KEY]

# ---------- primitif gambar (koordinat kolom, belum diskalakan) ----------
def P(*pts): return [(x * S, y * S) for x, y in pts]
def line(d, pts, col, w=6): d.line(P(*pts), fill=col, width=int(w * S), joint="curve")
def rect(d, x0, y0, x1, y1, fill=None, out=None, w=2, r=0):
    box = [x0 * S, y0 * S, x1 * S, y1 * S]
    (d.rounded_rectangle(box, r * S, fill=fill, outline=out, width=int(w * S)) if r else d.rectangle(box, fill=fill, outline=out, width=int(w * S)))
def circ(d, x, y, r, fill=None, out=None, w=2): d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=fill, outline=out, width=int(w * S))
def poly(d, pts, fill, out=None): d.polygon(P(*pts), fill=fill, outline=out)
def txt(d, x, y, s, size, col, anchor="mm", bold=True): d.text((x * S, y * S), s, font=F(int(size * S), bold), fill=col, anchor=anchor)
def mini_heart(d, x, y, r, col):
    circ(d, x - r * 0.55, y - r * 0.3, r * 0.6, fill=col); circ(d, x + r * 0.55, y - r * 0.3, r * 0.6, fill=col)
    poly(d, [(x - r * 1.1, y - r * 0.1), (x + r * 1.1, y - r * 0.1), (x, y + r * 1.1)], col)
def ex(d, x, y, r, col): line(d, [(x - r, y - r), (x + r, y + r)], col, 6); line(d, [(x + r, y - r), (x - r, y + r)], col, 6)
def check(d, x, y, r, col): line(d, [(x - r, y), (x - r * 0.3, y + r * 0.8), (x + r, y - r * 0.8)], col, 6)
def lerp(a, b, p): return a + (b - a) * clamp(p)

def wrap(d, s, font, maxw):
    words, lines, cur = s.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) > maxw and cur: lines.append(cur); cur = w
        else: cur = t
    return lines + [cur]

def bubble(d, x, y, s, fill, out, a, align="l", bg=(20, 20, 28)):
    f = F(int(26 * S)); lines = wrap(d, s, f, 400 * S)
    wd = max(d.textlength(l, font=f) for l in lines) + 36 * S; ht = len(lines) * 34 * S + 26 * S
    x0 = x * S if align == "l" else x * S - wd
    y0 = (y - 12 * (1 - a)) * S
    d.rounded_rectangle([x0, y0, x0 + wd, y0 + ht], 22 * S, fill=fade(fill, a, bg), outline=fade(out, a, bg) if out else None, width=2 * S)
    for i, l in enumerate(lines): d.text((x0 + 18 * S, y0 + (13 + 17 + i * 34) * S), l, font=f, fill=fade(WHITE, a, bg), anchor="lm")
    return ht / S

# ---------- stick figure ----------
def fig(d, x, base, col, lean=0.0, face=1, walk=0.0, arms=((34, 44), (-24, 62))):
    lw = 9
    hip = (x, base - 110); sh = (x + face * lean * 14, base - 195); hd = (sh[0] + face * lean * 8, sh[1] - 32)
    sw = math.sin(walk) * 22
    line(d, [hip, (x - 16 + sw, base)], col, lw); line(d, [hip, (x + 16 - sw, base)], col, lw); line(d, [hip, sh], col, lw)
    for dx, dy in arms: line(d, [sh, (sh[0] + face * dx, sh[1] + dy)], col, lw)
    circ(d, hd[0], hd[1], 27, fill=col)
    return sh

# ---------- benda cerita: p = 0..1 (kemajuan akibat), A=salah satu, B=yang sehat ----------
def prop(d, name, side, p, t):
    A = side == "A"; cx, cy = 250, 905
    if name == "jembatan":
        rect(d, 30, cy, 150, cy + 150, (70, 72, 90)); rect(d, 350, cy, 470, cy + 150, (70, 72, 90))
        for i in range(6):
            x0 = 150 + i * 33
            if A:
                fall = clamp((p - 0.25 - i * 0.04) * 3) if 1 <= i <= 4 else 0
                if fall < 1: rect(d, x0, cy + 6 + fall * 160, x0 + 29, cy + 26 + fall * 160, (176, 130, 80))
            else:
                if p > i / 7: rect(d, x0, cy + 6, x0 + 29, cy + 26, (176, 130, 80))
        line(d, [(150, cy), (350, cy)], (120, 120, 140), 3) if not A or p < 0.3 else None
        txt(d, 90, cy - 20, "AKU", 20, WHITE_C); txt(d, 410, cy - 20, "KAMU", 20, GREY_C)
    elif name == "ponsel":
        rect(d, 160, cy - 150, 340, cy + 130, (30, 34, 48), (150, 156, 176), 3, 26)
        rect(d, 172, cy - 126, 328, cy + 108, (16, 20, 30), None, 0, 14)
        rect(d, 182, cy - 112, 290, cy - 80, BLUE, None, 0, 12); txt(d, 236, cy - 96, "Chat aku...", 15, WHITE)
        if A:
            txt(d, 300, cy - 58, "Dibaca", 14, (110, 170, 255));
            for k in range(3): circ(d, 232 + k * 18, cy + 10, 4 + (1 if int(t * 3) % 3 == k else 0) * 0, fill=(80, 84, 100))
            txt(d, 250, cy + 70, "...", 34, GREY)
            # jam pasir
            poly(d, [(240, cy + 150), (260, cy + 150), (250, cy + 175)], (200, 180, 120)); poly(d, [(240, cy + 200), (260, cy + 200), (250, cy + 175)], (200, 180, 120))
        else:
            a = seg(p, 0.15, 0.4)
            if a > 0: rect(d, 192 + (1 - a) * 0, cy - 60, 318, cy - 28, (60, 62, 74), None, 0, 12); txt(d, 255, cy - 44, "Maaf, bales ya", 14, fade(WHITE, a))
            a = seg(p, 0.5, 0.8)
            if a > 0: mini_heart(d, 250, cy + 40, 22, fade(GREEN, a))
    elif name == "hati":
        k = 1 - 0.25 * p if A else 1 + 0.25 * p
        col = tuple(int(c) for c in ((180, 80, 90) if A else (255, 110, 150)))
        circ(d, cx - 40 * k, cy - 30 * k, 52 * k, fill=col); circ(d, cx + 40 * k, cy - 30 * k, 52 * k, fill=col)
        poly(d, [(cx - 88 * k, cy - 8 * k), (cx + 88 * k, cy - 8 * k), (cx, cy + 100 * k)], col)
        if A:
            if p > 0.2: line(d, [(cx, cy - 78), (cx - 14, cy - 40), (cx + 12, cy - 10), (cx - 10, cy + 30), (cx + 4, cy + 70)], (20, 12, 18), 6)
            if p > 0.6: line(d, [(cx + 10, cy - 20), (cx + 40, cy)], (20, 12, 18), 4)
        else:
            for i in range(8):
                ang = i * math.pi / 4 + t; r0 = 120 * k + 8 * math.sin(t * 4 + i)
                line(d, [(cx + math.cos(ang) * r0, cy + 10 + math.sin(ang) * r0), (cx + math.cos(ang) * (r0 + 16), cy + 10 + math.sin(ang) * (r0 + 16))], (255, 200, 210), 3)
    elif name == "payung":
        if A:
            line(d, [(120, cy + 150), (380, cy + 150)], (90, 92, 110), 4)
            line(d, [(150, cy + 140), (360, cy + 130)], (190, 90, 90), 8); circ(d, 150, cy + 140, 8, fill=(190, 90, 90))  # payung tertutup di tanah
        else:
            ang = 1
            poly(d, [(cx - 130, cy - 10), (cx - 90, cy - 80), (cx, cy - 110), (cx + 90, cy - 80), (cx + 130, cy - 10)], (90, 150, 230))
            line(d, [(cx, cy - 110), (cx, cy + 120)], (210, 210, 220), 5)
        for i in range(26):
            x = (i * 53 + 17) % 460 + 20; y = ((t * 380 + i * 71) % 330) + cy - 150
            if (not A) and abs(x - cx) < 135 and y < cy - 5: continue
            line(d, [(x, y), (x - 6, y + 20)], (130, 170, 230), 3)
        if A: txt(d, 250, cy - 120, "…", 40, GREY)
    elif name == "cangkir":
        if A:
            rect(d, 170, cy - 140, 330, cy + 150, (60, 46, 40), (120, 96, 80), 4, 6)
            sh = 6 * math.sin(t * 60) * (1 - seg(p, 0.3, 0.6)) if p < 0.6 else 0
            txt(d, 250 + sh, cy - 20, "BAM!", 52, RED)
            circ(d, 305, cy + 20, 7, fill=(200, 180, 120))
        else:
            rect(d, 90, cy + 90, 410, cy + 120, (110, 84, 60))
            for x0 in (140, 290):
                rect(d, x0, cy + 20, x0 + 70, cy + 90, (240, 236, 226), None, 0, 10)
                circ(d, x0 + 80, cy + 52, 18, None, (240, 236, 226), 6)
                for k in range(2):
                    ph = (t * 1.2 + k * 0.5) % 1
                    line(d, [(x0 + 25 + k * 22, cy + 10), (x0 + 15 + k * 22 + 10 * math.sin(ph * 6), cy - 10 - ph * 40)], (230, 230, 240), 3)
    elif name == "tanaman":
        rect(d, 195, cy + 90, 305, cy + 150, (160, 100, 70), None, 0, 8)
        if A:
            line(d, [(250, cy + 90), (250, cy + 20), (250 + 60 * p, cy - 20 + 40 * p)], (120, 110, 60), 7)
            for sx, sy in ((-40, 40), (50, 60)): poly(d, [(250, cy + 50), (250 + sx * 1.6, cy + 50 + sy * p), (250 + sx * 0.6, cy + 20 + sy * p * 0.5)], (140, 112, 60))
        else:
            h = 50 + 170 * p
            line(d, [(250, cy + 90), (250, cy + 90 - h)], (80, 190, 110), 7)
            for k in range(1, 4):
                yy = cy + 90 - h * k / 4
                if h > 50 * k: poly(d, [(250, yy), (250 - 58, yy - 20), (250 - 18, yy + 8)], (90, 210, 120)); poly(d, [(250, yy - 14), (250 + 58, yy - 34), (250 + 18, yy - 6)], (90, 210, 120))
    elif name == "puzzle":
        gap = 90 * (1 - p) if not A else 40 + 70 * p
        for sgn, col in ((-1, (230, 120, 110)), (1, (110, 190, 240))):
            x = cx + sgn * (gap / 2 + 62) if A else cx + sgn * (gap / 2 + 62 - 0)
            rect(d, x - 62, cy - 62, x + 62, cy + 62, col, None, 0, 12)
            circ(d, x - sgn * 62, cy, 20, fill=col if sgn == 1 else (16, 20, 30)) if False else None
        if A:
            for i in range(5):
                ang = i * 1.3 + t * 9; line(d, [(cx + math.cos(ang) * 26, cy - 90 + math.sin(ang) * 10), (cx + math.cos(ang) * 46, cy - 110 + math.sin(ang) * 14)], GOLD, 3)
            ex(d, cx, cy + 112, 18, RED)
        else:
            circ(d, cx, cy, 20, fill=(240, 220, 120)); check(d, cx, cy + 112, 20, GREEN)
    elif name == "baterai":
        rect(d, 110, cy - 90, 390, cy + 60, None, WHITE_C, 5, 18); rect(d, 390, cy - 50, 410, cy + 20, WHITE_C, None, 0, 6)
        lv = lerp(0.2, 0.05, p) if A else lerp(0.2, 0.92, p)
        col = RED if A else GREEN
        rect(d, 120, cy - 80, 120 + 260 * lv, cy + 50, col, None, 0, 10)
        txt(d, 250, cy + 125, f"{int(lv * 100)}%", 40, col)
        if not A: txt(d, 250, cy - 15, "+", 60, (20, 40, 30))
    elif name == "sangkar":
        for x0 in range(150, 360, 30): line(d, [(x0, cy - 110), (x0, cy + 100)], (170, 172, 190), 4)
        line(d, [(150, cy - 110), (350, cy - 110)], (170, 172, 190), 6); line(d, [(150, cy + 100), (350, cy + 100)], (170, 172, 190), 6)
        if A:
            circ(d, 250, cy + 60, 26, fill=(250, 210, 90)); poly(d, [(274, cy + 58), (296, cy + 64), (274, cy + 70)], (240, 140, 60))
            rect(d, 150, cy - 110, 350, cy + 100, None, (170, 172, 190), 3)
        else:
            bx = lerp(250, 390, seg(p, 0.1, 0.5)) - 150 * seg(p, 0.65, 1) * 0 + 40 * math.sin(t * 2) * seg(p, 0.5, 1)
            by = lerp(cy + 60, cy - 120, seg(p, 0.1, 0.5)) + 10 * math.sin(t * 5)
            circ(d, bx, by, 22, fill=(250, 210, 90)); poly(d, [(bx + 20, by - 2), (bx + 38, by + 4), (bx + 20, by + 10)], (240, 140, 60))
            line(d, [(bx - 22, by), (bx - 44, by - 16 + 8 * math.sin(t * 14))], (250, 210, 90), 5)
            mini_heart(d, 250, cy + 135, 18, fade(GREEN, seg(p, 0.7, 1)))
    elif name == "buku":
        if A:
            rect(d, 160, cy - 90, 340, cy + 100, (120, 80, 70), (80, 50, 44), 4, 8)
            line(d, [(190, cy - 50), (310, cy + 60)], RED, 8); line(d, [(310, cy - 50), (190, cy + 60)], RED, 8)
        else:
            poly(d, [(250, cy - 70), (110, cy - 90), (110, cy + 90), (250, cy + 110)], (240, 232, 214)); poly(d, [(250, cy - 70), (390, cy - 90), (390, cy + 90), (250, cy + 110)], (250, 242, 224))
            for i in range(5): line(d, [(130, cy - 50 + i * 28), (230, cy - 40 + i * 28)], (160, 150, 130), 3); line(d, [(270, cy - 40 + i * 28), (370, cy - 50 + i * 28)], (160, 150, 130), 3)
            for i in range(9):
                ang = -math.pi + i * math.pi / 8; r0 = 130 + 30 * p
                line(d, [(250 + math.cos(ang) * r0, cy - 90 + math.sin(ang) * r0), (250 + math.cos(ang) * (r0 + 22), cy - 90 + math.sin(ang) * (r0 + 22))], GOLD, 4)
    elif name == "kue":
        if A:
            rect(d, 150, cy - 110, 350, cy + 80, (240, 236, 226), (150, 150, 160), 3, 12)
            rect(d, 150, cy - 110, 350, cy - 60, (210, 80, 80), None, 0, 12)
            txt(d, 250, cy - 15, "17", 70, (60, 60, 70)); circ(d, 250, cy - 20, 62, None, RED, 5)
            txt(d, 250, cy + 130, "tidak ada kue", 22, GREY)
        else:
            rect(d, 130, cy + 30, 370, cy + 100, (240, 190, 140), None, 0, 10); rect(d, 160, cy - 30, 340, cy + 30, (250, 220, 230), None, 0, 10)
            line(d, [(250, cy - 30), (250, cy - 75)], (240, 240, 250), 8)
            fl = 1 + 0.2 * math.sin(t * 14)
            poly(d, [(250, cy - 80 - 40 * fl), (232, cy - 72), (268, cy - 72)], (255, 190, 60))
            for i in range(6): circ(d, 130 + i * 48, cy + 100, 6, fill=(255, 120, 150))
    elif name == "mangkuk":
        if A:
            for k, (x0, y0) in enumerate(((190, cy + 40), (260, cy - 10))):
                rect(d, x0, y0, x0 + 80, y0 + 34, (230, 120, 110), None, 0, 17); rect(d, x0 + 40, y0, x0 + 80, y0 + 34, (240, 240, 244), None, 0, 17)
            rect(d, 120, cy + 100, 380, cy + 118, (90, 92, 110)); txt(d, 250, cy + 150, "obat saja", 24, GREY)
        else:
            poly(d, [(140, cy + 10), (360, cy + 10), (330, cy + 100), (170, cy + 100)], (240, 236, 226)); rect(d, 140, cy, 360, cy + 14, (250, 200, 120), None, 0, 6)
            rect(d, 170, cy + 100, 330, cy + 112, (210, 206, 196)); line(d, [(360, cy + 40), (420, cy - 40)], (200, 200, 210), 5)
            for k in range(3):
                ph = (t * 0.9 + k * 0.33) % 1
                line(d, [(190 + k * 55, cy - 6), (180 + k * 55 + 10 * math.sin(ph * 6), cy - 20 - ph * 60)], (230, 230, 240), 4)

# ---------- kolom ----------
def column(t, side):
    A = side == "A"
    img = Image.new("RGB", (CW * S, CH * S), BG[side][0]); d = ImageDraw.Draw(img)
    for y in range(0, CH * S, 10):
        pr = y / (CH * S); c = tuple(int(BG[side][0][i] + (BG[side][1][i] - BG[side][0][i]) * pr) for i in range(3)); d.rectangle([0, y, CW * S, y + 10], fill=c)
    acc = RED if A else GREEN
    # label
    rect(d, 20, 20, 190, 64, acc, None, 0, 14); txt(d, 105, 42, "PASANGAN " + side, 22, (20, 20, 28))
    a = seg(t, 3.0, 3.4)
    if a > 0: txt(d, 20, 92, _S[4] if A else _S[5], 24, fade(acc, a, BG[side][0]), "lm")
    # panggung tokoh
    base = 700
    d.line(P((20, base), (480, base)), fill=(90, 90, 104), width=3 * S)
    ph = seg(t, 4.6, 6.2)
    wx = 150; gx0 = 350
    if A:
        gx = lerp(gx0, 600, ph); gwalk = t * 9 if 0 < ph < 1 else 0
        fig(d, wx, base, WHITE_C, lean=0.9 * seg(t, 5.0, 6.4), arms=((34, 44), (-24, 62)) if ph < 0.1 else ((14, 70), (-14, 70)))
        fig(d, gx, base, GREY_C, face=-1 if ph < 0.05 else 1, walk=gwalk)
    else:
        gx = lerp(gx0, 215, ph); gwalk = t * 9 if 0 < ph < 1 else 0
        shw = fig(d, wx, base, WHITE_C, lean=0.2 * ph)
        shg = fig(d, gx, base, GREY_C, face=-1, walk=gwalk)
        if ph >= 1:
            line(d, [shg, (wx + 14, shg[1] + 30)], GREY_C, 9); line(d, [shw, (gx - 14, shw[1] + 30)], WHITE_C, 9)
    # bubble
    a = seg(t, 1.0, 1.3)
    if a > 0: ht = bubble(d, 20, 130, _S[1], BLUE, None, a, bg=BG[side][0])
    a = seg(t, 2.8, 3.1) * (1 - 0.0)
    if a > 0: bubble(d, CW - 20, 270, _S[2] if A else _S[3], (84, 46, 46) if A else (36, 84, 60), acc, a, "r", BG[side][0])
    # benda cerita + hasil
    pp = seg(t, 5.0, 9.0)
    prop(d, _S[9], side, pp, t)
    a = seg(t, 7.4, 7.8)
    if a > 0:
        f = F(int(25 * S)); lines = wrap(d, _S[6] if A else _S[7], f, 400 * S)
        hh = len(lines) * 32 + 26; y0 = 1068
        d.rounded_rectangle([20 * S, y0 * S, (CW - 20) * S, (y0 + hh) * S], 16 * S, fill=fade(acc, 0.22 * a, BG[side][1]), outline=fade(acc, a, BG[side][1]), width=2 * S)
        for i, l in enumerate(lines): d.text((CW / 2 * S, (y0 + 13 + 16 + i * 32) * S), l, font=f, fill=fade(WHITE, a, BG[side][1]), anchor="mm")
    return img.resize((CW, CH), Image.LANCZOS)

CAPS = [(1.0, 2.8, "Situasi yang sama, dua tanggapan."), (3.0, 5.0, None), (5.2, 9.8, "Lihat akibatnya.")]

def frame(i):
    t = i / FPS
    img = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(img)
    a = seg(t, 0, 0.3)
    h1 = _S[0]; fs = min(66, int((1000 / len(h1) - 6) / 0.6))
    text_c(d, (W / 2, 150), h1, F(fs), fade(WHITE, a), sp=5)
    text_c(d, (W / 2, 235), "DUA PASANGAN. DUA CARA.", F(40), fade(GOLD, a), sp=5)
    dim = 1 - seg(t, 9.8, 10.4)
    s = seg(t, 0.4, 1.0)
    for side, x in (("A", 30), ("B", 550)):
        c = column(t, side)
        if min(s, dim) < 1: c = Image.blend(Image.new("RGB", c.size, (0, 0, 0)), c, min(s, dim))
        img.paste(c, (x, int(330 + 24 * (1 - s))))
    d = ImageDraw.Draw(img)
    if s > 0.4 and dim > 0.05:
        circ_x, circ_y = W // 2, 1000
        d.ellipse([circ_x - 34, circ_y - 34, circ_x + 34, circ_y + 34], fill=(20, 20, 28), outline=fade(GOLD, dim), width=3)
        text_c(d, (circ_x, circ_y), "VS", F(26), fade(GOLD, dim), sp=0)
    if t >= 10.2:
        def ln(txt_, y, a0, col=WHITE, font=None, sp=5):
            a = seg(t, a0, a0 + 0.4)
            if a > 0: text_c(d, (W / 2, y + 20 * (1 - a)), txt_, font or F(70), fade(col, a), sp=sp)
        ln("SAMA MASALAHNYA.", 820, 10.2, font=F(70))
        ln(_S[8], 940, 10.5, col=GOLD, font=F(min(48, int((1000 / len(_S[8]) - 5) / 0.6))))
        ln("kamu yang mana? A atau B?", 1090, 11.0, col=GREY, font=F(34, False), sp=2)
    else:
        for a0, b0, s_ in CAPS:
            if a0 <= t < b0:
                s_ = s_ or ('A: "' + _S[2] + '"  B: "' + _S[3] + '"')
                al = min(seg(t, a0, a0 + 0.2), 1 - seg(t, b0 - 0.15, b0)); f = F(40); tw = d.textlength(s_, font=f)
                if tw > 1000: f = F(int(40 * 1000 / tw))
                text_c(d, (W / 2, 1765), s_, f, fade(WHITE, al), sp=0); break
    return img

def build_audio(path, sr=44100):
    n = sr * DUR; t = np.arange(n) / sr; a = np.zeros(n); rng = np.random.default_rng(9)
    for s, e, fs in [(0, 4.6, [110, 130.8, 164.8]), (4.6, 10, [98, 130.8, 164.8, 196]), (10, 12, [130.8, 196, 261.6, 329.6])]:
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
    tone(0.05, 55, 0.8, 0.35, 4)
    tone(1.0, 700, 0.15, 0.15, 25); tone(1.1, 900, 0.2, 0.12, 20)
    tone(2.8, 700, 0.15, 0.15, 25); tone(2.9, 500, 0.4, 0.14, 8, 380)
    noise(4.6, 0.4, 0.15, 6, 40)
    tone(5.0, 330, 3.5, 0.06, 1, 520); tone(5.0, 440, 3.5, 0.04, 1, 300)         # dua arah nada: naik/turun
    for k in range(5): tone(5.2 + k * 0.8, 1500 + 120 * k, 0.1, 0.1, 40)
    tone(7.4, 880, 0.2, 0.18, 12); tone(7.55, 1175, 0.3, 0.16, 10)
    tone(10.2, 55, 1.2, 0.4, 3); noise(10.2, 0.4, 0.15, 12, 40)
    for f in (523.3, 659.3, 784): tone(10.5, f, 1.5, 0.12, 2)
    a = np.tanh(a * 1.3); a[-sr // 2:] *= np.linspace(1, 0, sr // 2)
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a * 32000).astype(np.int16).tobytes())

def work(a): i, tmp = a; frame(i).save(f"{tmp}/{i:04d}.png")

if __name__ == "__main__":
    OUT = sys.argv[1] if len(sys.argv) > 1 else f"pasangan-{KEY}.mp4"
    tmp = os.path.dirname(os.path.abspath(OUT)) + f"/_frames_ps_{KEY}"; os.makedirs(tmp, exist_ok=True)
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
