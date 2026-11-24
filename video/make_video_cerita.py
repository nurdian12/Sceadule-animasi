#!/usr/bin/env python3
"""Seri cerita dua angle (gaya video 'move on bukan melupakan' yang menang), 720x1280, 24 fps, 20 detik.

Pola tetap: panel atas = DIA yang menyakiti (tokoh putih makin terpuruk: retak hati, hujan, air mata),
panel bawah = DIA yang sehat (cahaya hangat, hati). Tiap cerita punya BENDA/metafora sendiri.
Judul diketik, judul baris-2 di detik 10, panel meredup di detik 12, punchline emas + putih, catatan kecil.

Pakai: python3 make_video_cerita.py <kunci> [out.mp4]    (PREVIEW=3,7,11 untuk frame PNG)
"""
import math, os, subprocess, sys, tempfile, wave
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_argv = sys.argv; sys.argv = [sys.argv[0]]
import numpy as np
from PIL import Image, ImageDraw
import cerita_base as base
from cerita_base import (AMBER, BLUE, CORAL, FLOOR, FPS, F_PUNCH, F_SUB, F_TITLE, GREY, H, PH, PW, PX,
                         PYA, PYB, RED, S, W, WHITE, BG, blank, broken_heart, clamp, ease, fig_layer,
                         finish_panel, heart, lerp, lerp_col, overlay, paste_glow, pulse, put, ring_pulse,
                         scale_col, shock, sparks, spaced, spaced_multi, tears, vignette, font)
sys.argv = _argv
DUR = 20.0
DIA = (112, 118, 142)
LIT = (230, 230, 238)
GOLD = (255, 200, 90)

# ------------------------------------------------------------------ alat gambar
def C4(c, a=255): return tuple(c[:3]) + (int(a),)
def layer(p, fn, alpha=1.0):
    lay = blank(); fn(ImageDraw.Draw(lay)); put(p, lay, alpha)
def LN(d, pts, col, w=2, a=255): d.line([(x * S, y * S) for x, y in pts], fill=C4(col, a), width=max(1, int(w * S)), joint="curve")
def EL(d, x, y, r, fill=None, out=None, w=1.5, a=255, ry=None):
    ry = r if ry is None else ry
    d.ellipse([(x - r) * S, (y - ry) * S, (x + r) * S, (y + ry) * S], fill=C4(fill, a) if fill else None, outline=C4(out, a) if out else None, width=int(w * S))
def RC(d, x0, y0, x1, y1, fill=None, out=None, w=1.5, rad=0, a=255):
    box = [x0 * S, y0 * S, x1 * S, y1 * S]
    if rad: d.rounded_rectangle(box, rad * S, fill=C4(fill, a) if fill else None, outline=C4(out, a) if out else None, width=int(w * S))
    else: d.rectangle(box, fill=C4(fill, a) if fill else None, outline=C4(out, a) if out else None, width=int(w * S))
def PG(d, pts, fill, a=255): d.polygon([(x * S, y * S) for x, y in pts], fill=C4(fill, a))
def TX(d, x, y, s, size, col, a=255): d.text((x * S, y * S), s, font=font(int(size * S)), fill=C4(col, a), anchor="mm")
def arc_pt(a, b, u, h): return (lerp(a[0], b[0], u), lerp(a[1], b[1], u) - h * math.sin(math.pi * u))
def track(keys, t):
    x, moving, f = float(keys[0][1]), False, keys[0][2] if len(keys[0]) > 2 else -1
    for k0, k1 in zip(keys, keys[1:]):
        t0, x0 = k0[0], k0[1]; t1, x1 = k1[0], k1[1]
        if t >= t0:
            if x1 != x0: f = 1 if x1 > x0 else -1
            if t < t1:
                u = ease((t - t0) / (t1 - t0)); x = lerp(x0, x1, u); moving = x1 != x0 and 0 < u < 1
            else: x = float(x1)
    return x, moving, f
def rain_mask(p, t, k, hole=None):
    n = int(40 * clamp(k))
    if n <= 0: return
    def fn(d):
        for j in range(n):
            x = (j * 53 + 11) % PW; y = (t * 250 + j * 97) % (PH + 20) - 10
            if hole and hole[0] < x < hole[1] and y > hole[2]: continue
            d.line([(x * S, y * S), ((x - 4) * S, (y + 14) * S)], fill=(140, 160, 230, 130), width=S)
    layer(p, fn)

# ------------------------------------------------------------------ konteks per panel
class Ctx:
    def __init__(self, p, t, side, hero):
        self.p, self.t, self.A, self.h = p, t, side == "A", hero
        self.hero_drawn = False
    def put_hero(self):
        if not self.hero_drawn: put(self.p, self.h["lay"]); self.hero_drawn = True
    def dia(self, x, f=-1, walk=None, lit=0.0, face=None, arm_f=15, arm_b=-8, sit=0.0, alpha=1.0, lean=0.0, head=0.0):
        col = lerp_col(DIA, LIT, lit)
        lay, _, hd = fig_layer(x, FLOOR, col, f=f, walk=walk, lean=lean, head=head, arm_f=arm_f, arm_b=arm_b, sit=sit, face=face)
        hand = base.LAST_HAND
        put(self.p, lay, alpha)
        return hand, hd

# ------------------------------------------------------------------ CERITA
# Tiap cerita: teks + fungsi A(c) / B(c). c.t = waktu, c.h = tokoh putih (x, hand, hd).
STORIES = {}
def story(key, **kw):
    def deco(fn_pair):
        kw.update(fn_pair()); STORIES[key] = kw; return fn_pair
    return deco

IMP = [5.2, 6.8, 8.4]      # momen 'kena' di panel A
ACT, BURST = 4.6, 9.4      # aksi sehat & puncak di panel B

# 1 ------------------------------------------------------------ surat (didengar)
def envelope(d, x, y, k_open=0.0, crumple=0.0):
    if crumple > 0.5:
        EL(d, x, y, 7, fill=(236, 232, 220)); LN(d, [(x - 4, y - 2), (x + 3, y + 1), (x - 1, y + 4)], (160, 150, 130), 1); return
    if k_open < 0.5:
        RC(d, x - 11, y - 7, x + 11, y + 7, fill=(240, 236, 224)); LN(d, [(x - 11, y - 7), (x, y + 1), (x + 11, y - 7)], (170, 160, 140), 1.2)
    else:
        RC(d, x - 13, y - 18, x + 13, y + 14, fill=(250, 246, 234))
        for i in range(4): LN(d, [(x - 9, y - 11 + i * 6), (x + 9, y - 11 + i * 6)], (170, 160, 140), 1)
@story("surat", title1="PERASAAN BUKAN DRAMA.", title2="JANGAN REMAS SURATNYA,",
       la="DIA YANG MEREMAS", lb="DIA YANG MEMBACA",
       at=[(0, ""), (2.1, "INI YANG AKU RASAKAN."), (4.6, "DIREMAS."), (6.8, "DIBUANG."), (8.4, "DITINGGAL."), (10.0, "TIDAK DIDENGAR.")],
       bt=[(0, ""), (2.1, "INI YANG AKU RASAKAN."), (4.6, "DIBUKA."), (6.4, "DIBACA PELAN."), (8.3, "DIDENGAR."), (9.4, "LEGA, DEKAT.")],
       p1=[("BACA", AMBER)], p2=[("PERASAANNYA.", WHITE)], s1="TIDAK SELALU BENAR.", s2="TAPI SELALU LAYAK DIBACA.")
def _():
    def A(c):
        t = c.t; x, mv, f = track([(0, 560), (2.0, 560), (3.4, 330), (7.4, 330), (8.6, 720)], t)
        if t > 7.4: f = 1
        hand, hd = c.dia(x, f=f, walk=t * 8 if mv else None, face="calm", arm_f=60 if 3.4 < t < 6.8 else 15)
        hh = c.h["hand"]
        if t < 3.0: pos, cr = (hh[0] + 6, hh[1] + 4), 0
        elif t < 3.8: pos, cr = arc_pt((hh[0] + 6, hh[1] + 4), (hand[0] - 4, hand[1] + 2), ease((t - 3.0) / 0.8), 30), 0
        elif t < 6.0: pos, cr = (hand[0] - 4, hand[1] + 2), ease((t - 4.4) / 0.6)
        else: pos, cr = arc_pt((340, hand[1]), (470, FLOOR - 6), ease((t - 6.0) / 0.8), 50), 1
        layer(c.p, lambda d: envelope(d, pos[0], pos[1], crumple=cr))
    def B(c):
        t = c.t; x, mv, f = track([(0, 560), (2.0, 560), (3.4, 330), (6.4, 330), (7.6, 230)], t)
        lit = ease((t - 9.0) / 0.6)
        hand, hd = c.dia(x, f=-1, walk=t * 8 if mv else None, face="happy" if t > BURST else "calm", arm_f=lerp(60, 120, ease((t - 4.4) / 0.4)) if t < 6.4 else 60, lit=lit)
        hh = c.h["hand"]
        if t < 3.0: pos, k = (hh[0] + 6, hh[1] + 4), 0
        elif t < 3.8: pos, k = arc_pt((hh[0] + 6, hh[1] + 4), (hand[0] - 4, hand[1] + 2), ease((t - 3.0) / 0.8), 30), 0
        else: pos, k = (hand[0] - 6, hand[1] - 2), ease((t - 4.4) / 0.4)
        if k > 0.5: paste_glow(c.p, pos[0], pos[1], 0.35)
        layer(c.p, lambda d: envelope(d, pos[0], pos[1], k_open=k))
    return dict(A=A, B=B)

# 2 ------------------------------------------------------------ pesawat kertas (chat)
def plane(d, x, y, ang=0.0, col=(240, 236, 224)):
    ca, sa = math.cos(ang), math.sin(ang)
    pts = [(14, 0), (-10, -7), (-5, 0), (-10, 7)]
    PG(d, [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts], col)
@story("pesan", title1="CHAT BUKAN SOAL CEPAT.", title2="BUKAN SOAL SEMPURNA,",
       la="DIA YANG MENGABAIKAN", lb="DIA YANG MEMBALAS",
       at=[(0, ""), (2.1, "PESAN PERTAMA."), (5.2, "TIDAK DIBALAS."), (6.8, "DIKIRIM LAGI."), (8.4, "MASIH DIAM."), (10.0, "LELAH MENUNGGU.")],
       bt=[(0, ""), (2.1, "PESAN PERTAMA."), (4.6, "DIBALAS."), (6.4, "WALAU SINGKAT."), (8.3, "ADA KABARNYA."), (9.4, "TENANG.")],
       p1=[("BALAS", AMBER)], p2=[("WALAU SINGKAT.", WHITE)], s1="SIBUK ITU WAJAR.", s2="MENGHILANG ITU PILIHAN.")
def _():
    START, END = (175, 248), (440, FLOOR - 4)
    def A(c):
        t = c.t
        hand, hd = c.dia(460, f=1, face="calm", arm_f=60, head=0.25)          # membelakangi, menatap ponsel
        layer(c.p, lambda d: RC(d, hand[0] + 2, hand[1] - 9, hand[0] + 10, hand[1] + 5, fill=(170, 200, 255)))
        paste_glow(c.p, hand[0] + 6, hand[1] - 2, 0.25)
        throws = [2.2, 4.6, 6.2, 7.8]
        def fn(d):
            for i, t0 in enumerate(throws):
                u = (t - t0) / 0.7
                if u < 0: continue
                land = (420 + i * 14, FLOOR - 4 - (i % 2) * 3)
                if u < 1: x, y = arc_pt(START, land, ease(u), 70); plane(d, x, y, -0.4 + 0.8 * u)
                else: plane(d, land[0], land[1], 0.15 * (i - 1))
        layer(c.p, fn)
    def B(c):
        t = c.t; x, mv, f = track([(0, 460), (6.4, 460), (7.6, 260)], t)
        lit = ease((t - 9.0) / 0.6)
        catch = 2.2 + 0.7
        hand, hd = c.dia(x, f=-1, walk=t * 8 if mv else None, face="happy" if t > BURST else "calm", arm_f=lerp(15, 150, pulse(t - catch, 0.8) * 1.4) if t < 4.6 else lerp(150, 40, ease((t - 4.6) / 0.5)), lit=lit)
        def fn(d):
            u = (t - 2.2) / 0.7
            if 0 <= u < 1: px, py = arc_pt(START, (440, 230), ease(u), 60); plane(d, px, py, -0.3 + 0.6 * u)
            v = (t - ACT) / 0.8
            if 0 <= v < 1: px, py = arc_pt((430, 230), (180, 250), ease(v), 70); plane(d, px, py, math.pi + 0.3 - 0.6 * v, (255, 214, 140))
        layer(c.p, fn)
    return dict(A=A, B=B)

# 3 ------------------------------------------------------------ bayangan (cemburu)
@story("bayangan", title1="CEMBURU BUKAN KEJAHATAN.", title2="JANGAN DIREMEHKAN,",
       la="DIA YANG MEMBIARKAN", lb="DIA YANG MENERANGI",
       at=[(0, ""), (2.1, "ADA RASA TAKUT."), (5.2, "KAMU BERLEBIHAN."), (6.8, "TAKUTNYA MEMBESAR."), (8.4, "MAKIN GELAP."), (10.0, "SENDIRIAN.")],
       bt=[(0, ""), (2.1, "ADA RASA TAKUT."), (4.6, "LAMPU DINYALAKAN."), (6.4, "DIAJAK BICARA."), (8.3, "TAKUTNYA MENGECIL."), (9.4, "TERANG.")],
       p1=[("TERANGI", AMBER)], p2=[("TAKUTNYA.", WHITE)], s1="BAYANGAN MENGECIL", s2="SAAT LAMPUNYA DINYALAKAN.")
def _():
    LAMP = 330
    def shadow(c, sc, a):
        lay, _, _ = fig_layer(c.h["x"] - 46 * sc / 1.15, FLOOR, (6, 8, 18), f=1, sc=sc, arm_f=20, arm_b=-10)
        put(c.p, lay, a)
    def lamp(d, on):
        LN(d, [(LAMP, FLOOR), (LAMP, FLOOR - 120)], (90, 92, 110), 3); EL(d, LAMP, FLOOR - 126, 9, fill=(255, 220, 140) if on else (80, 80, 96))
    def A(c):
        t = c.t; g = sum(ease((t - m) / 0.6) for m in IMP)
        shadow(c, 1.15 + 0.55 * g, 0.55 + 0.12 * g)
        layer(c.p, lambda d: lamp(d, False))
        swing = sum(pulse(t - m, 0.6) for m in IMP)
        c.dia(470, f=1 if t > 6.0 else -1, face="calm", arm_f=15 + 110 * swing)
    def B(c):
        t = c.t; on = t > ACT
        if on: paste_glow(c.p, LAMP, FLOOR - 126, 0.9 + 0.4 * ease((t - ACT) / 1.0))
        shadow(c, lerp(1.15, 0.55, ease((t - ACT) / 2.0)), lerp(0.55, 0.0, ease((t - ACT) / 3.0)))
        layer(c.p, lambda d: lamp(d, on))
        x, mv, f = track([(0, 470), (2.6, 470), (4.0, 350), (6.4, 350), (7.6, 230)], t)
        c.dia(x, f=-1, walk=t * 8 if mv else None, face="happy" if t > BURST else "calm", arm_f=150 if 4.0 < t < 4.8 else 30, lit=ease((t - 9.0) / 0.6))
    return dict(A=A, B=B)

# 4 ------------------------------------------------------------ payung (telat jemput)
def umbrella(d, x, y, r=46, col=(90, 150, 230)):
    pts = [(x - r + 2 * r * i / 20, y - math.sin(math.pi * i / 20) * r * 0.6) for i in range(21)]
    PG(d, pts + [(x + r, y)], col)
    for i in range(1, 4): LN(d, [(x - r + 2 * r * i / 4, y), (x, y - r * 0.6)], (60, 110, 190), 1)
    LN(d, [(x, y - r * 0.6), (x, y + 62)], (210, 210, 220), 2)
@story("payung", title1="TELAT ITU MANUSIAWI.", title2="TAPI JANGAN DATANG KOSONG,",
       la="DIA YANG DATANG KOSONG", lb="DIA YANG BAWA PAYUNG",
       at=[(0, ""), (2.1, "MENUNGGU DI HALTE."), (5.2, "SATU JAM BERLALU."), (6.8, "AKHIRNYA DATANG."), (8.4, "GITU AJA MARAH?"), (10.0, "TETAP KEHUJANAN.")],
       bt=[(0, ""), (2.1, "MENUNGGU DI HALTE."), (4.6, "DIA BERLARI."), (6.4, "MAAF, AKU TELAT."), (8.3, "DIPAYUNGI."), (9.4, "HANGAT.")],
       p1=[("BAWA", AMBER)], p2=[("PAYUNGNYA.", WHITE)], s1="TELAT BISA DIMAAFKAN.", s2="YANG PENTING DATANG MEMPERBAIKI.")
def _():
    def stop(d):
        LN(d, [(92, FLOOR), (92, FLOOR - 140)], (120, 124, 140), 3); RC(d, 76, FLOOR - 160, 108, FLOOR - 134, fill=(70, 110, 180), rad=4); TX(d, 92, FLOOR - 147, "BUS", 8, WHITE)
    def A(c):
        t = c.t; layer(c.p, stop); rain_mask(c.p, t, 1.0)
        x, mv, f = track([(0, 760), (5.6, 760), (6.8, 330)], t)
        shrug = pulse(t - IMP[2], 1.2)
        c.dia(x, f=-1, walk=t * 8 if mv else None, face="calm", arm_f=15 + 140 * shrug, arm_b=-8 - 120 * shrug)
    def B(c):
        t = c.t; layer(c.p, stop)
        x, mv, f = track([(0, 760), (ACT, 760), (6.4, 225)], t)
        under = (c.h["x"] - 60, x + 50, FLOOR - 170) if t > 6.4 else None
        rain_mask(c.p, t, 1.0, hole=under)
        hand, hd = c.dia(x, f=-1, walk=t * 12 if mv else None, face="happy" if t > BURST else "calm", arm_f=160, lit=ease((t - 9.0) / 0.6))
        layer(c.p, lambda d: umbrella(d, hand[0] - 12, hand[1] - 52, 64 if t > 6.4 else 46))
    return dict(A=A, B=B)

# 5 ------------------------------------------------------------ tali (bertengkar)
@story("tali", title1="BERTENGKAR ITU WAJAR.", title2="TAPI JANGAN SALING TARIK,",
       la="DIA YANG MENARIK", lb="DIA YANG MENGENDURKAN",
       at=[(0, ""), (2.1, "SAMA-SAMA MARAH."), (5.2, "DITARIK."), (6.8, "DITARIK LAGI."), (8.4, "PUTUS."), (10.0, "MASING-MASING.")],
       bt=[(0, ""), (2.1, "SAMA-SAMA MARAH."), (4.6, "DIKENDURKAN."), (6.4, "MENDEKAT."), (8.3, "DIIKAT LAGI."), (9.4, "UTUH.")],
       p1=[("KENDURKAN", AMBER)], p2=[("TALINYA.", WHITE)], s1="MARAH BOLEH.", s2="JANGAN SAMPAI PUTUS.")
def _():
    def rope(c, a, b, sag, col=(224, 120, 110), cut=None):
        def fn(d):
            pts = [(lerp(a[0], b[0], i / 24), lerp(a[1], b[1], i / 24) + sag * 4 * (i / 24) * (1 - i / 24) + (2 * math.sin(c.t * 40 + i) if sag < 2 else 0)) for i in range(25)]
            if cut is None: LN(d, pts, col, 2.2)
            else:
                LN(d, pts[:12], col, 2.2); LN(d, [(x, y + cut * 60) for x, y in pts[13:]], col, 2.2)
        layer(c.p, fn)
    def A(c):
        t = c.t; snap = ease((t - IMP[2]) / 0.5)
        x, mv, f = track([(0, 430), (IMP[2] + 0.4, 430), (IMP[2] + 2.0, 700)], t)
        tug = sum(pulse(t - m, 0.6) for m in IMP)
        hand, hd = c.dia(x, f=-1 if t < IMP[2] + 0.4 else 1, walk=t * 8 if mv else None, face="hit" if tug > 0.1 else "calm", lean=-0.25 - 0.2 * tug if t < IMP[2] else 0, arm_f=80)
        if t < IMP[2]: rope(c, c.h["hand"], hand, 0.5)
        elif t < IMP[2] + 0.8: rope(c, c.h["hand"], (lerp(hand[0], 330, 0), hand[1]), 0, cut=snap)
    def B(c):
        t = c.t; x, mv, f = track([(0, 430), (ACT, 430), (6.4, 225)], t)
        hand, hd = c.dia(x, f=-1, walk=t * 8 if mv else None, face="happy" if t > BURST else "calm", lean=-0.25 * (1 - ease((t - ACT) / 0.5)), arm_f=80 if t < 6.4 else 60, lit=ease((t - 9.0) / 0.6))
        rope(c, c.h["hand"], hand, lerp(0.5, 30, ease((t - ACT) / 0.8)) if t < 6.4 else 8)
        if t > 8.3: layer(c.p, lambda d: EL(d, (c.h["hand"][0] + hand[0]) / 2, (c.h["hand"][1] + hand[1]) / 2 + 6, 6, out=GOLD, w=2.5))
    return dict(A=A, B=B)

# 6 ------------------------------------------------------------ tanaman (kritik)
def plant(d, x, grow, wilt):
    RC(d, x - 18, FLOOR - 26, x + 18, FLOOR, fill=(170, 104, 70), rad=3)
    h = 30 + 60 * grow
    col = lerp_col((90, 200, 110), (150, 120, 60), wilt)
    top = (x + 30 * wilt, FLOOR - 26 - h + 40 * wilt)
    LN(d, [(x, FLOOR - 26), (x + 4 * wilt, FLOOR - 26 - h / 2), top], col, 3)
    for k in range(1, 3 + int(2 * grow)):
        yy = FLOOR - 26 - h * k / (3 + 2 * grow)
        dy = 10 * wilt
        PG(d, [(x, yy), (x - 18, yy - 8 + dy * 2), (x - 6, yy + 4)], col); PG(d, [(x, yy - 6), (x + 18, yy - 14 + dy * 2), (x + 6, yy - 2)], col)
    if grow > 0.8: EL(d, top[0], top[1] - 4, 7, fill=(255, 170, 190))
def can(d, x, y, tilt):
    ca, sa = math.cos(tilt), math.sin(tilt)
    def R(px, py): return (x + px * ca - py * sa, y + px * sa + py * ca)
    PG(d, [R(-10, -8), R(10, -8), R(10, 10), R(-10, 10)], (110, 160, 200)); LN(d, [R(10, -2), R(26, -14)], (110, 160, 200), 3)
@story("tanaman", title1="KRITIK BUKAN SERANGAN.", title2="KALAU DITERIMA,",
       la="DIA YANG MENOLAK", lb="DIA YANG MENERIMA",
       at=[(0, ""), (2.1, "ADA YANG INGIN DIPERBAIKI."), (5.2, "DITEPIS."), (6.8, "KAMU TERLALU SENSITIF."), (8.4, "LAYU."), (10.0, "BERHENTI BICARA.")],
       bt=[(0, ""), (2.1, "ADA YANG INGIN DIPERBAIKI."), (4.6, "DITERIMA."), (6.4, "PELAN-PELAN."), (8.3, "TUMBUH."), (9.4, "BERBUNGA.")],
       p1=[("IA", AMBER), (" TUMBUH.", WHITE)], p2=[("BUKAN LAYU.", WHITE)], s1="YANG MAU MENDENGAR,", s2="TUMBUH LEBIH KUAT.")
def _():
    POT = 330
    def drops(c, t0, t1):
        t = c.t
        if t0 < t < t1:
            def fn(d):
                for i in range(6):
                    y = FLOOR - 120 + ((t * 160 + i * 23) % 80)
                    EL(d, POT - 8 + (i % 3) * 8, y, 2.2, fill=(130, 180, 240))
            layer(c.p, fn)
    def A(c):
        t = c.t; wilt = clamp(sum(ease((t - m) / 0.8) for m in IMP[1:]) / 2)
        layer(c.p, lambda d: plant(d, POT, 0.2, wilt))
        hh = c.h["hand"]; tilt = 0.6 * ease((t - 3.4) / 0.6) * (1 - ease((t - IMP[0]) / 0.3))
        layer(c.p, lambda d: can(d, hh[0] + 8, hh[1] + 4, tilt))
        drops(c, 3.8, IMP[0])
        push = pulse(t - IMP[0], 0.8)
        c.dia(420, f=-1, face="calm", arm_f=15 + 100 * push, lean=0.1 * push)
    def B(c):
        t = c.t; g = ease((t - ACT) / 4.5)
        layer(c.p, lambda d: plant(d, POT, 0.2 + 0.8 * g, 0))
        hh = c.h["hand"]; tilt = 0.6 * ease((t - 3.4) / 0.6) * (1 - ease((t - 7.0) / 0.5))
        layer(c.p, lambda d: can(d, hh[0] + 8, hh[1] + 4, tilt))
        drops(c, 3.8, 7.0)
        c.dia(420, f=-1, face="happy" if t > BURST else "calm", arm_f=15, lit=ease((t - 9.0) / 0.6))
    return dict(A=A, B=B)

# 7 ------------------------------------------------------------ puzzle (beda pendapat)
def piece(d, x, y, col, rot, tab=1):
    ca, sa = math.cos(rot), math.sin(rot)
    def R(px, py): return (x + px * ca - py * sa, y + px * sa + py * ca)
    PG(d, [R(-18, -18), R(18, -18), R(18, 18), R(-18, 18)], col)
    tx, ty = R(18 * tab + 6 * tab, 0); EL(d, tx, ty, 8, fill=col)
@story("puzzle", title1="BEDA PENDAPAT ITU BIASA.", title2="JANGAN SALING MEMAKSA,",
       la="DIA YANG MEMAKSA", lb="DIA YANG MEMUTAR",
       at=[(0, ""), (2.1, "DUA PENDAPAT."), (5.2, "DIPAKSA."), (6.8, "TIDAK MASUK."), (8.4, "SALING MENJAUH."), (10.0, "SAMA-SAMA LELAH.")],
       bt=[(0, ""), (2.1, "DUA PENDAPAT."), (4.6, "DIPUTAR."), (6.4, "DICOBA LAGI."), (8.3, "PAS."), (9.4, "SALING MELENGKAPI.")],
       p1=[("PUTAR", AMBER)], p2=[("SUDUT PANDANGNYA.", WHITE)], s1="BEDA PENDAPAT", s2="BUKAN BERARTI BEDA ARAH.")
def _():
    def A(c):
        t = c.t; bump = sum(pulse(t - m, 0.5) for m in IMP)
        away = ease((t - IMP[2]) / 1.2)
        hand, hd = c.dia(400 + 120 * away, f=-1 if t < IMP[2] + 0.3 else 1, walk=t * 8 if 0 < away < 1 else None, face="hit" if bump > 0.1 else "calm", arm_f=80)
        gap = 22 + 24 * bump
        layer(c.p, lambda d: (piece(d, 300 - gap / 2, 270, (230, 120, 110), 0, 1), piece(d, 330 + gap / 2 + 60 * away, 270, (110, 170, 240), 0, 1)))
        for m in IMP: sparks(c.p, 318, 262, t - m - 0.02) if t - m < 0.5 else None
    def B(c):
        t = c.t; rot = math.pi * ease((t - ACT) / 1.2); join = ease((t - 6.4) / 1.2)
        c.dia(400, f=-1, face="happy" if t > BURST else "calm", arm_f=80, lit=ease((t - 9.0) / 0.6))
        if join > 0.95: paste_glow(c.p, 310, 270, 0.5)
        layer(c.p, lambda d: (piece(d, 296 + 4 * join, 270, (230, 120, 110), 0, 1), piece(d, lerp(352, 330, join), 270, (110, 170, 240), rot, 1)))
    return dict(A=A, B=B)

# 8 ------------------------------------------------------------ tas & baterai (capek)
def bag(d, x, y, col=(150, 120, 90)):
    EL(d, x, y, 13, fill=col, ry=11); LN(d, [(x - 4, y - 11), (x, y - 17), (x + 4, y - 11)], (110, 86, 64), 2)
def battery(d, x, y, lv):
    RC(d, x - 20, y - 9, x + 18, y + 9, out=WHITE, w=1.6, rad=3); RC(d, x + 18, y - 4, x + 22, y + 4, fill=WHITE)
    col = RED if lv < 0.25 else ((255, 200, 90) if lv < 0.6 else (110, 220, 150))
    RC(d, x - 17, y - 6, x - 17 + 32 * clamp(lv), y + 6, fill=col)
@story("baterai", title1="CAPEK ITU MANUSIAWI.", title2="JANGAN DIBALAS CAPEK,",
       la="DIA YANG MENAMBAH", lb="DIA YANG MEMBANTU",
       at=[(0, ""), (2.1, "PULANG DENGAN CAPEK."), (5.2, "AKU JUGA CAPEK!"), (6.8, "DITAMBAH LAGI."), (8.4, "HABIS."), (10.0, "TIDAK KUAT.")],
       bt=[(0, ""), (2.1, "PULANG DENGAN CAPEK."), (4.6, "SINI, AKU BANTU."), (6.4, "DIBAWA BERDUA."), (8.3, "TERISI LAGI."), (9.4, "RINGAN.")],
       p1=[("TEMANI", AMBER)], p2=[("CAPEKNYA.", WHITE)], s1="BEBAN TERASA RINGAN", s2="SAAT DIBAWA BERDUA.")
def _():
    def A(c):
        t = c.t; hh = c.h["hand"]; hd = c.h["hd"]
        n = 1 + sum(1 for m in IMP if t > m)
        lv = 0.4 - 0.12 * sum(ease((t - m) / 0.6) for m in IMP)
        hand, _ = c.dia(400, f=-1, face="calm", arm_f=15 + 120 * sum(pulse(t - (m - 0.5), 0.6) for m in IMP))
        def fn(d):
            for i in range(n): bag(d, hh[0] + 4, hh[1] + 12 - i * 16)
            for m in IMP:
                u = (t - (m - 0.5)) / 0.5
                if 0 <= u < 1: x, y = arc_pt((hand[0], hand[1]), (hh[0] + 4, hh[1] - 20), ease(u), 40); bag(d, x, y)
            battery(d, hd[0], hd[1] - 44, lv)
        layer(c.p, fn)
    def B(c):
        t = c.t; hh = c.h["hh"] if "hh" in c.h else c.h["hand"]; hd = c.h["hd"]
        x, mv, f = track([(0, 400), (3.6, 400), (ACT, 240)], t)
        hand, _ = c.dia(x, f=-1, walk=t * 8 if mv else None, face="happy" if t > BURST else "calm", arm_f=50, lit=ease((t - 9.0) / 0.6))
        lv = lerp(0.4, 0.95, ease((t - ACT) / 4.5))
        def fn(d):
            if t < ACT: bag(d, hh[0] + 4, hh[1] + 12)
            else: bag(d, hand[0] - 4, hand[1] + 12)
            battery(d, hd[0], hd[1] - 44, lv)
        layer(c.p, fn)
    return dict(A=A, B=B)

# 9 ------------------------------------------------------------ burung & sangkar (minta ruang)
def bird(d, x, y, flap=0.0, droop=0.0):
    EL(d, x, y, 9, fill=(250, 210, 90), ry=8); PG(d, [(x + 8, y - 2), (x + 16, y + 1 + 4 * droop), (x + 8, y + 3)], (240, 140, 60))
    LN(d, [(x - 2, y), (x - 12, y - 8 * math.cos(flap) + 6 * droop)], (240, 196, 70), 3)
    EL(d, x + 4, y - 3, 1.4, fill=(30, 30, 40))
def cage(d, x, y, door=0.0):
    for i in range(7): LN(d, [(x - 30 + i * 10, y - 60), (x - 30 + i * 10, y)], (180, 182, 200), 1.6)
    LN(d, [(x - 32, y), (x + 32, y)], (180, 182, 200), 3); d.arc([(x - 32) * S, (y - 80) * S, (x + 32) * S, (y - 40) * S], 180, 360, fill=C4((180, 182, 200)), width=int(2 * S))
@story("sangkar", title1="MINTA RUANG BUKAN PERGI.", title2="JANGAN DIKURUNG,",
       la="DIA YANG MENGURUNG", lb="DIA YANG MELEPAS",
       at=[(0, ""), (2.1, "INGIN PERGI SEBENTAR."), (5.2, "TERSERAH."), (6.8, "DIKURUNG."), (8.4, "SESAK."), (10.0, "MERASA TERJEBAK.")],
       bt=[(0, ""), (2.1, "INGIN PERGI SEBENTAR."), (4.6, "KABARIN YA."), (6.4, "TERBANG."), (8.3, "LALU PULANG."), (9.4, "BEBAS, DEKAT.")],
       p1=[("BUKA", AMBER)], p2=[("SANGKARNYA.", WHITE)], s1="YANG DIBERI RUANG", s2="TAHU JALAN PULANG.")
def _():
    def A(c):
        t = c.t; hh = c.h["hand"]
        cy = lerp(FLOOR - 150, hh[1] + 22, ease((t - 4.4) / 0.8))
        c.dia(420, f=-1, face="calm", arm_f=15 + 120 * pulse(t - 4.4, 1.0))
        droop = ease((t - IMP[2]) / 0.8)
        layer(c.p, lambda d: (bird(d, hh[0] + 10, hh[1] - 2 + 6 * droop, t * 3 * (1 - droop), droop), cage(d, hh[0] + 10, cy)))
    def B(c):
        t = c.t; hh = c.h["hand"]
        c.dia(420, f=-1, face="happy" if t > BURST else "calm", arm_f=40, lit=ease((t - 9.0) / 0.6))
        u = clamp((t - ACT) / (8.6 - ACT))
        if 0 < u < 1:
            bx = lerp(hh[0] + 10, 500, math.sin(math.pi * u)) + 40 * math.sin(u * 9)
            by = lerp(hh[1] - 2, 80, math.sin(math.pi * u)) + 20 * math.cos(u * 7)
        else: bx, by = hh[0] + 10, hh[1] - 2
        layer(c.p, lambda d: bird(d, bx, by, t * 18 if 0 < u < 1 else t * 3))
    return dict(A=A, B=B)

# 10 ----------------------------------------------------------- kotak cerita (masa lalu)
def box(d, x, lid):
    RC(d, x - 26, FLOOR - 34, x + 26, FLOOR, fill=(160, 124, 86), out=(110, 82, 58), w=1.5, rad=3)
    ang = -1.2 * lid
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = x - 26, FLOOR - 34
    PG(d, [(px, py), (px + 54 * ca, py + 54 * sa), (px + 54 * ca + 8 * sa, py + 54 * sa - 8 * ca), (px + 8 * sa, py - 8 * ca)], (176, 138, 96))
@story("kotak", title1="MASA LALU BUKAN AIB.", title2="JANGAN DITUTUP PAKSA,",
       la="DIA YANG MENUTUP", lb="DIA YANG MENDENGARKAN",
       at=[(0, ""), (2.1, "INGIN BERCERITA."), (5.2, "GAK PENTING."), (6.8, "DITUTUP."), (8.4, "DITINGGAL."), (10.0, "DIPENDAM LAGI.")],
       bt=[(0, ""), (2.1, "INGIN BERCERITA."), (4.6, "DUDUK DI SAMPING."), (6.4, "DIBUKA PELAN."), (8.3, "DIDENGARKAN."), (9.4, "RINGAN.")],
       p1=[("DENGARKAN", AMBER)], p2=[("CERITANYA.", WHITE)], s1="TIDAK UNTUK DIHAKIMI.", s2="CUKUP DIMENGERTI.")
def _():
    BX = 270
    def A(c):
        t = c.t; lid = ease((t - 3.2) / 0.6) * (1 - ease((t - IMP[0]) / 0.15))
        if lid > 0.3: paste_glow(c.p, BX, FLOOR - 50, 0.3 * lid)
        layer(c.p, lambda d: box(d, BX, lid))
        x, mv, f = track([(0, 420), (IMP[1], 420), (IMP[2] + 0.4, 700)], t)
        c.dia(x, f=-1 if t < IMP[1] else 1, walk=t * 8 if mv else None, face="calm", arm_f=15 + 120 * pulse(t - (IMP[0] - 0.3), 0.6))
    def B(c):
        t = c.t; lid = ease((t - 6.0) / 1.0)
        if lid > 0.2:
            paste_glow(c.p, BX, FLOOR - 60, 0.6 * lid)
            def motes(d):
                for i in range(6):
                    u = ((t - 6.0) * 0.4 + i / 6) % 1
                    EL(d, BX - 20 + i * 8 + 6 * math.sin(u * 8 + i), FLOOR - 40 - 90 * u, 2.2, fill=GOLD, a=255 * (1 - u))
                layer(c.p, motes)
        layer(c.p, lambda d: box(d, BX, lid))
        x, mv, f = track([(0, 420), (3.4, 420), (ACT, 330)], t)
        c.dia(x, f=-1, walk=t * 8 if mv else None, face="happy" if t > BURST else "calm", sit=ease((t - ACT) / 0.6), arm_f=30, lit=ease((t - 9.0) / 0.6))
    return dict(A=A, B=B)

# 11 ----------------------------------------------------------- lilin ulang tahun
def cake(d, x, flame, life):
    RC(d, x - 42, FLOOR - 52, x + 42, FLOOR - 46, fill=(104, 80, 60)); LN(d, [(x - 34, FLOOR - 46), (x - 34, FLOOR)], (78, 60, 46), 4); LN(d, [(x + 34, FLOOR - 46), (x + 34, FLOOR)], (78, 60, 46), 4)
    RC(d, x - 26, FLOOR - 80, x + 26, FLOOR - 52, fill=(250, 220, 230), rad=4); RC(d, x - 26, FLOOR - 80, x + 26, FLOOR - 72, fill=(255, 150, 170), rad=4)
    h = 26 * life; RC(d, x - 2.5, FLOOR - 80 - h, x + 2.5, FLOOR - 80, fill=(240, 240, 250))
    if flame > 0.02: PG(d, [(x, FLOOR - 80 - h - 14 * flame), (x - 4, FLOOR - 82 - h), (x + 4, FLOOR - 82 - h)], (255, 200, 80))
@story("lilin", title1="LUPA ITU MANUSIAWI.", title2="TAPI JANGAN DIBIARKAN PADAM,",
       la="DIA YANG LEWAT", lb="DIA YANG MENYALAKAN",
       at=[(0, ""), (2.1, "HARI YANG DITUNGGU."), (5.2, "DILEWATI."), (6.8, "LILINNYA PADAM."), (8.4, "TIDAK ADA KABAR."), (10.0, "SENDIRIAN.")],
       bt=[(0, ""), (2.1, "HARI YANG DITUNGGU."), (4.6, "MAAF, AKU LUPA."), (6.4, "DINYALAKAN LAGI."), (8.3, "DITEBUS."), (9.4, "HANGAT.")],
       p1=[("NYALAKAN", AMBER)], p2=[("LAGI.", WHITE)], s1="LUPA BISA DITEBUS.", s2="YANG MEMADAMKAN ITU DIAM.")
def _():
    CX = 320
    def A(c):
        t = c.t; out_ = ease((t - IMP[1]) / 0.4); fl = (1 - out_) * (0.9 + 0.1 * math.sin(t * 20))
        if fl > 0.05: paste_glow(c.p, CX, FLOOR - 110, 0.5 * fl)
        layer(c.p, lambda d: cake(d, CX, fl, 1 - 0.6 * clamp(t / 7)))
        x, mv, f = track([(0, 700), (3.6, 700), (6.8, 520), (8.4, 760)], t)
        hand, _ = c.dia(x, f=-1, walk=t * 8 if mv else None, face="calm", arm_f=60, head=0.25, alpha=0.9)
        layer(c.p, lambda d: RC(d, hand[0] - 9, hand[1] - 9, hand[0] - 1, hand[1] + 5, fill=(170, 200, 255)))
        if 6.8 < t < 8.4:
            def smoke(d):
                for i in range(3):
                    u = ((t - 6.8) * 0.8 + i / 3) % 1; EL(d, CX + 5 * math.sin(u * 7), FLOOR - 112 - 40 * u, 3 + 3 * u, fill=(140, 140, 150), a=150 * (1 - u))
            layer(c.p, smoke)
    def B(c):
        t = c.t; relight = ease((t - 6.2) / 0.3)
        fl = relight if t > 6.2 else (1 - ease((t - 3.6) / 0.4))
        if fl > 0.05: paste_glow(c.p, CX, FLOOR - 110, 0.6 * fl + 0.4 * relight)
        layer(c.p, lambda d: cake(d, CX, fl * (0.9 + 0.1 * math.sin(t * 20)), 0.7))
        x, mv, f = track([(0, 700), (4.4, 700), (5.8, 380)], t)
        hand, _ = c.dia(x, f=-1, walk=t * 10 if mv else None, face="happy" if t > BURST else "calm", arm_f=100 if 5.8 < t < 6.6 else 30, lit=ease((t - 9.0) / 0.6))
        if 5.0 < t < 6.6: layer(c.p, lambda d: PG(d, [(hand[0] - 2, hand[1] - 14), (hand[0] - 5, hand[1] - 4), (hand[0] + 1, hand[1] - 4)], (255, 200, 80)))
    return dict(A=A, B=B)

# 12 ----------------------------------------------------------- mangkuk (sakit)
def door(d, x, op):
    RC(d, x - 30, FLOOR - 150, x + 30, FLOOR, fill=(236, 214, 160) if op > 0.05 else (40, 42, 56), out=(80, 84, 100), w=2)
    if op > 0.05: RC(d, x + 30 - 60 * (1 - op), FLOOR - 150, x + 30, FLOOR, fill=(40, 42, 56))
def bowl(d, x, y, t):
    PG(d, [(x - 20, y), (x + 20, y), (x + 14, y + 16), (x - 14, y + 16)], (240, 236, 226))
    for k in range(3):
        u = (t * 0.9 + k / 3) % 1; LN(d, [(x - 8 + k * 8, y - 4), (x - 10 + k * 8 + 4 * math.sin(u * 6), y - 10 - 20 * u)], (230, 230, 240), 1.6, a=255 * (1 - u))
@story("bubur", title1="SAKIT BUKAN MANJA.", title2="OBAT SAJA TIDAK CUKUP,",
       la="DIA YANG PERGI", lb="DIA YANG MENEMANI",
       at=[(0, ""), (2.1, "BADAN SEDANG LEMAH."), (5.2, "MINUM OBAT AJA."), (6.8, "DITINGGAL."), (8.4, "PINTU TERTUTUP."), (10.0, "SEMBUH SENDIRIAN.")],
       bt=[(0, ""), (2.1, "BADAN SEDANG LEMAH."), (4.6, "KUBAWAIN BUBUR."), (6.4, "DUDUK MENEMANI."), (8.3, "HANGAT."), (9.4, "DITEMANI.")],
       p1=[("HADIR", AMBER)], p2=[("ITU OBATNYA.", WHITE)], s1="OBAT UNTUK BADAN.", s2="KEHADIRAN UNTUK HATI.")
def _():
    def A(c):
        t = c.t; op = 1 - ease((IMP[2] - t) / 0.01) if False else (1.0 if t < IMP[2] else 1 - ease((t - IMP[2]) / 0.4))
        layer(c.p, lambda d: door(d, 560, op))
        x, mv, f = track([(0, 420), (6.0, 420), (IMP[2], 560)], t)
        hand, _ = c.dia(x, f=-1 if t < 6.0 else 1, walk=t * 8 if mv else None, face="calm", arm_f=70 if 4.4 < t < 5.4 else 15, alpha=1.0 if t < IMP[2] else 1 - ease((t - IMP[2]) / 0.3))
        pp = (hand[0] - 4, hand[1] + 4) if t < 4.8 else arc_pt((hand[0], hand[1]), (250, FLOOR - 8), ease((t - 4.8) / 0.5), 20) if t < 5.3 else (250, FLOOR - 8)
        layer(c.p, lambda d: (RC(d, pp[0] - 6, pp[1] - 10, pp[0] + 6, pp[1] + 8, fill=(240, 150, 140), rad=2), RC(d, pp[0] - 6, pp[1] - 12, pp[0] + 6, pp[1] - 8, fill=WHITE)))
    def B(c):
        t = c.t; layer(c.p, lambda d: door(d, 560, 1.0 if t < 6.4 else 1 - ease((t - 6.4) / 0.6)))
        x, mv, f = track([(0, 560), (3.0, 560), (ACT, 290)], t)
        sit = ease((t - 6.0) / 0.6)
        hand, _ = c.dia(x, f=-1, walk=t * 8 if mv else None, face="happy" if t > BURST else "calm", arm_f=70, sit=sit, lit=ease((t - 9.0) / 0.6))
        paste_glow(c.p, hand[0] - 6, hand[1] - 4, 0.35)
        layer(c.p, lambda d: bowl(d, hand[0] - 8, hand[1] - 4, t))
    return dict(A=A, B=B, hero_sit=0.85, hero_face="sad")

# 13 ----------------------------------------------------------- arah (kejelasan / HTS)
def signpost(d, x, lit):
    LN(d, [(x, FLOOR), (x, FLOOR - 110)], (140, 120, 100), 4)
    col = GOLD if lit > 0.5 else (120, 110, 100)
    PG(d, [(x - 6, FLOOR - 104), (x + 46, FLOOR - 104), (x + 58, FLOOR - 94), (x + 46, FLOOR - 84), (x - 6, FLOOR - 84)], col)
    TX(d, x + 24, FLOOR - 94, "KITA", 8, (30, 30, 40))
    PG(d, [(x + 6, FLOOR - 76), (x - 46, FLOOR - 76), (x - 58, FLOOR - 66), (x - 46, FLOOR - 56), (x + 6, FLOOR - 56)], (110, 104, 96))
    TX(d, x - 24, FLOOR - 66, "???", 8, (30, 30, 40))
@story("arah", title1="HUBUNGAN BUTUH ARAH.", title2="JANGAN BERPUTAR TERUS,",
       la="DIA YANG BERPUTAR", lb="DIA YANG MEMILIH ARAH",
       at=[(0, ""), (2.1, "KITA INI APA?"), (5.2, "JALANIN AJA DULU."), (6.8, "BERPUTAR."), (8.4, "DI TEMPAT YANG SAMA."), (10.0, "PUSING.")],
       bt=[(0, ""), (2.1, "KITA INI APA?"), (4.6, "AKU SERIUS."), (6.4, "ARAHNYA JELAS."), (8.3, "BERJALAN BERSAMA."), (9.4, "TENANG.")],
       p1=[("PILIH", AMBER)], p2=[("ARAHNYA.", WHITE)], s1="TANPA ARAH,", s2="KITA HANYA BERPUTAR.")
def _():
    SX = 330
    def ring(c):
        def fn(d):
            for i in range(0, 360, 24): d.arc([(SX - 150) * S, (FLOOR - 14) * S, (SX + 150) * S, (FLOOR + 16) * S], i, i + 12, fill=C4(GREY, 120), width=2 * S)
        layer(c.p, fn)
    def A(c):
        t = c.t; ring(c); layer(c.p, lambda d: signpost(d, SX, 0))
        ang = max(0, t - 2.6) * 1.3
        x = SX + 150 * math.cos(ang + math.pi)
        c.dia(x, f=1 if math.sin(ang + math.pi) < 0 else -1, walk=t * 8 if t > 2.6 else None, face="calm", alpha=0.9 + 0.1 * math.sin(ang + math.pi))
        if t > 7.0:
            def q(d):
                for i in range(3): TX(d, c.h["hd"][0] - 10 + i * 12, c.h["hd"][1] - 40 - 6 * math.sin(t * 5 + i), "?", 12, GREY)
            layer(c.p, q)
    def B(c):
        t = c.t; ring(c); lit = ease((t - ACT) / 0.4)
        if lit > 0: paste_glow(c.p, SX + 30, FLOOR - 94, 0.5 * lit)
        layer(c.p, lambda d: signpost(d, SX, lit))
        if t < ACT:
            ang = max(0, t - 2.6) * 1.3; x = SX + 150 * math.cos(ang + math.pi); f = 1 if math.sin(ang + math.pi) < 0 else -1; walk = t * 8 if t > 2.6 else None
        else:
            x0 = SX + 150 * math.cos((ACT - 2.6) * 1.3 + math.pi)
            x, mv, f = track([(ACT, x0), (6.4, 230), (9.0, 230)], t); walk = t * 8 if mv else None
        c.dia(x, f=f, walk=walk, face="happy" if t > BURST else "calm", lit=ease((t - 9.0) / 0.6))
    return dict(A=A, B=B)

# 14 ----------------------------------------------------------- vas retak (minta maaf)
def vase(d, x, y, broken=0.0, gold=0.0):
    col = (120, 170, 220)
    if broken < 0.5:
        PG(d, [(x - 10, y - 46), (x + 10, y - 46), (x + 18, y - 20), (x + 12, y), (x - 12, y), (x - 18, y - 20)], col)
        if gold > 0: LN(d, [(x - 8, y - 40), (x + 2, y - 26), (x - 6, y - 12), (x + 6, y - 2)], GOLD, 2); LN(d, [(x + 2, y - 26), (x + 14, y - 20)], GOLD, 2)
    else:
        for i, (dx, dy) in enumerate([(-30, 0), (-12, 2), (6, -1), (22, 1), (38, 0)]):
            PG(d, [(x + dx - 7, y + dy), (x + dx + 5, y + dy - 6), (x + dx + 8, y + dy)], col)
@story("vas", title1="SALAH ITU MANUSIAWI.", title2="JANGAN SEMBUNYIKAN RETAKNYA,",
       la="DIA YANG MENYEMBUNYIKAN", lb="DIA YANG MEMPERBAIKI",
       at=[(0, ""), (2.1, "ADA YANG PECAH."), (5.2, "DISAPU KE BAWAH KARPET."), (6.8, "PURA-PURA BAIK."), (8.4, "MASIH MENGGANJAL."), (10.0, "TERSANDUNG.")],
       bt=[(0, ""), (2.1, "ADA YANG PECAH."), (4.6, "MAAF, AKU SALAH."), (6.4, "DIPUNGUT SATU-SATU."), (8.3, "DIRAPIKAN."), (9.4, "RETAKNYA JADI EMAS.")],
       p1=[("AKUI,", AMBER)], p2=[("LALU PERBAIKI.", WHITE)], s1="YANG DISEMBUNYIKAN", s2="AKAN MEMBUAT TERSANDUNG.")
def _():
    VX = 330
    def table(d): RC(d, VX - 30, FLOOR - 50, VX + 30, FLOOR - 44, fill=(104, 80, 60)); LN(d, [(VX - 24, FLOOR - 44), (VX - 24, FLOOR)], (78, 60, 46), 4); LN(d, [(VX + 24, FLOOR - 44), (VX + 24, FLOOR)], (78, 60, 46), 4)
    def fall(t):
        u = ease((t - 3.0) / 0.5); return (VX + 20 * u, lerp(FLOOR - 50, FLOOR, u)), u
    def A(c):
        t = c.t; (vx, vy), u = fall(t)
        sweep = ease((t - 4.4) / 0.8)
        def fn(d):
            table(d)
            RC(d, 300, FLOOR - 3 - 10 * sweep, 520, FLOOR, fill=(150, 60, 70), rad=4)
            if u < 1: vase(d, vx, vy)
            elif sweep < 1: vase(d, VX + 20 + 100 * sweep, FLOOR, broken=1)
        layer(c.p, fn)
        x, mv, f = track([(0, 420), (2.6, 420), (2.9, 370), (4.4, 370), (5.2, 460), (IMP[1], 460), (IMP[2], 700)], t)
        c.dia(x, f=-1 if t < 5.0 else 1, walk=t * 8 if mv else None, face="calm", arm_f=60 if 4.4 < t < 5.2 else 15, lean=0.4 * (4.4 < t < 5.2))
    def B(c):
        t = c.t; (vx, vy), u = fall(t); fix = ease((t - 6.4) / 1.4)
        def fn(d):
            table(d)
            if u < 1: vase(d, vx, vy)
            elif fix < 1: vase(d, VX + 20, FLOOR, broken=1)
            else: vase(d, VX, FLOOR - 50, gold=1)
        if fix >= 1: paste_glow(c.p, VX, FLOOR - 74, 0.45)
        layer(c.p, fn)
        x, mv, f = track([(0, 420), (2.6, 420), (2.9, 370), (ACT, 370)], t)
        c.dia(x, f=-1, walk=t * 8 if mv else None, face="happy" if t > BURST else "calm", sit=ease((t - 5.2) / 0.5) * (1 - ease((t - 7.6) / 0.5)), arm_f=60, lit=ease((t - 9.0) / 0.6))
    return dict(A=A, B=B)

# 15 ----------------------------------------------------------- rahasia (cahaya kecil)
@story("rahasia", title1="DIPERCAYA ITU BERAT.", title2="JANGAN SIMPAN DI KANTONG BOCOR,",
       la="DIA YANG MEMBOCORKAN", lb="DIA YANG MENJAGA",
       at=[(0, ""), (2.1, "SEBUAH RAHASIA DITITIPKAN."), (5.2, "KANTONGNYA BOCOR."), (6.8, "SATU ORANG TAHU."), (8.4, "SEMUA ORANG TAHU."), (10.0, "DIKHIANATI.")],
       bt=[(0, ""), (2.1, "SEBUAH RAHASIA DITITIPKAN."), (4.6, "DISIMPAN RAPAT."), (6.4, "DIKUNCI."), (8.3, "HANYA BERDUA."), (9.4, "AMAN.")],
       p1=[("JAGA", AMBER)], p2=[("RAHASIANYA.", WHITE)], s1="YANG DIPERCAYA", s2="MENJAGA.")
def _():
    def orb(d, x, y, r=6): EL(d, x, y, r, fill=(255, 220, 140))
    def A(c):
        t = c.t; hh = c.h["hand"]
        x, mv, f = track([(0, 400), (4.2, 400), (8.8, 600)], t)
        hand, _ = c.dia(x, f=-1 if t < 4.2 else 1, walk=t * 6 if mv else None, face="calm", arm_f=40)
        def fn(d):
            if t < 3.0: orb(d, hh[0] + 6, hh[1])
            elif t < 3.8: px, py = arc_pt((hh[0] + 6, hh[1]), (hand[0], hand[1] + 10), ease((t - 3.0) / 0.8), 30); orb(d, px, py)
            EL(d, hand[0], hand[1] + 16, 11, fill=(150, 120, 90), ry=9)
            for i in range(10):
                t0 = 4.4 + 0.45 * i
                if t > t0: orb(d, lerp(400, 600, ease((t0 - 4.2) / 4.6)) - 10, FLOOR - 4, 3.2)
        layer(c.p, fn)
        for k, m in enumerate(IMP):
            if t > m:
                a = ease((t - m) / 0.6)
                lay, _, _ = fig_layer(470 + 50 * k, FLOOR, (46, 50, 66), f=-1, sc=1.0, arm_f=60, arm_b=-8)
                put(c.p, lay, a)
    def B(c):
        t = c.t; hh = c.h["hand"]
        hand, _ = c.dia(400, f=-1, face="happy" if t > BURST else "calm", arm_f=lerp(40, 80, ease((t - ACT) / 0.6)), lit=ease((t - 9.0) / 0.6))
        locked = t > 6.4
        def fn(d):
            if t < 3.0: orb(d, hh[0] + 6, hh[1])
            elif t < 3.8: px, py = arc_pt((hh[0] + 6, hh[1]), (hand[0], hand[1]), ease((t - 3.0) / 0.8), 30); orb(d, px, py)
            elif t < ACT: orb(d, hand[0], hand[1])
            RC(d, hand[0] - 12, hand[1] - 2, hand[0] + 12, hand[1] + 16, fill=(176, 138, 96), rad=3)
            if locked: RC(d, hand[0] - 4, hand[1] + 3, hand[0] + 4, hand[1] + 11, fill=GOLD, rad=1)
        if t > ACT: paste_glow(c.p, hand[0], hand[1] + 6, 0.3 + 0.2 * locked)
        layer(c.p, fn)
    return dict(A=A, B=B)

# 16 ----------------------------------------------------------- toples & koin (janji)
def jar(d, x, fill_):
    RC(d, x - 24, FLOOR - 70, x + 24, FLOOR - 4, out=(190, 210, 230), w=2, rad=8)
    if fill_ > 0.01: RC(d, x - 21, FLOOR - 7 - 58 * fill_, x + 21, FLOOR - 7, fill=GOLD, rad=6)
    RC(d, x - 18, FLOOR - 78, x + 18, FLOOR - 70, fill=(150, 150, 170))
    TX(d, x, FLOOR - 40, "PERCAYA", 7, (200, 210, 230))
@story("toples", title1="JANJI BUKAN SOAL BESAR.", title2="BUKAN JANJI YANG MEGAH,",
       la="DIA YANG BERJANJI BESAR", lb="DIA YANG MENABUNG",
       at=[(0, ""), (2.1, "JANJI DIUCAPKAN."), (5.2, "BESAR, TAPI MELESET."), (6.8, "LAGI-LAGI."), (8.4, "TOPLESNYA KOSONG."), (10.0, "TIDAK PERCAYA LAGI.")],
       bt=[(0, ""), (2.1, "JANJI DIUCAPKAN."), (4.6, "KECIL, TAPI DITEPATI."), (6.4, "SATU-SATU."), (8.3, "TERISI."), (9.4, "PERCAYA.")],
       p1=[("TEPATI", AMBER)], p2=[("YANG KECIL.", WHITE)], s1="KEPERCAYAAN DITABUNG,", s2="BUKAN DIPINJAM.")
def _():
    JX = 290
    def A(c):
        t = c.t; layer(c.p, lambda d: jar(d, JX, 0))
        hand, _ = c.dia(420, f=-1, face="calm", arm_f=15 + 140 * sum(pulse(t - (m - 0.6), 0.6) for m in IMP))
        def fn(d):
            for m in IMP:
                u = (t - (m - 0.6)) / 0.6
                if 0 <= u < 1: x, y = arc_pt((hand[0], hand[1]), (JX + 10, FLOOR - 90), ease(u), 80); EL(d, x, y, 16, fill=GOLD); TX(d, x, y, "$", 14, (150, 110, 40))
                v = (t - m) / 0.8
                if 0 <= v < 1: EL(d, JX + 30 + 60 * v, FLOOR - 90 + 60 * v * v, 16 * (1 - v), fill=(150, 150, 160), a=255 * (1 - v))
        layer(c.p, fn)
    def B(c):
        t = c.t; n = int(clamp((t - ACT) / 0.55, 0, 9))
        layer(c.p, lambda d: jar(d, JX, n / 9 * 0.9))
        if n >= 9: paste_glow(c.p, JX, FLOOR - 40, 0.4)
        hand, _ = c.dia(350, f=-1, face="happy" if t > BURST else "calm", arm_f=100, lit=ease((t - 9.0) / 0.6))
        u = ((t - ACT) / 0.55) % 1
        if ACT < t < ACT + 9 * 0.55: layer(c.p, lambda d: EL(d, lerp(hand[0], JX, u), lerp(hand[1], FLOOR - 76, u), 5, fill=GOLD))
    return dict(A=A, B=B)

# 17 ----------------------------------------------------------- dinding es (gengsi)
def icewall(d, x, h, melt=0.0):
    hh = h * (1 - melt)
    if hh > 2: RC(d, x - 16, FLOOR - hh, x + 16, FLOOR, fill=(170, 210, 240), a=200)
    for i in range(int(hh // 30)): LN(d, [(x - 10, FLOOR - 20 - i * 30), (x + 4, FLOOR - 30 - i * 30), (x - 2, FLOOR - 40 - i * 30)], (230, 245, 255), 1.2)
    if melt > 0: RC(d, x - 40 * melt - 16, FLOOR - 3, x + 40 * melt + 16, FLOOR, fill=(120, 170, 230), a=160)
@story("es", title1="GENGSI ITU DINGIN.", title2="JANGAN TUNGGU DIA DULUAN,",
       la="DIA YANG BERTAHAN GENGSI", lb="DIA YANG MENCAIRKAN",
       at=[(0, ""), (2.1, "SAMA-SAMA MERASA BENAR."), (5.2, "DIAM."), (6.8, "MAKIN DINGIN."), (8.4, "DINDINGNYA MENEBAL."), (10.0, "JAUH.")],
       bt=[(0, ""), (2.1, "SAMA-SAMA MERASA BENAR."), (4.6, "MAAF YA."), (6.4, "MENCAIR."), (8.3, "MENDEKAT."), (9.4, "HANGAT LAGI.")],
       p1=[("CAIRKAN", AMBER)], p2=[("GENGSINYA.", WHITE)], s1="SATU KATA MAAF", s2="MENCAIRKAN DINDING.")
def _():
    WX = 290
    def A(c):
        t = c.t; h = 80 + 40 * sum(ease((t - m) / 0.6) for m in IMP)
        layer(c.p, lambda d: icewall(d, WX, h))
        c.dia(420, f=1, face="calm", arm_f=60, arm_b=60)
    def B(c):
        t = c.t; melt = ease((t - 5.2) / 2.5)
        if t > ACT: paste_glow(c.p, 400, 280, 0.5 * ease((t - ACT) / 0.8))
        layer(c.p, lambda d: icewall(d, WX, 120, melt))
        x, mv, f = track([(0, 420), (7.4, 420), (8.6, 230)], t)
        hand, hd = c.dia(x, f=-1 if t > 4.0 else 1, walk=t * 8 if mv else None, face="happy" if t > BURST else "calm", arm_f=60 if t < 4.0 else 30, arm_b=60 if t < 4.0 else -8, lit=ease((t - 9.0) / 0.6))
        if 4.6 < t < 6.6: layer(c.p, lambda d: (RC(d, hd[0] - 34, hd[1] - 52, hd[0] + 34, hd[1] - 30, fill=(250, 240, 220), rad=8), TX(d, hd[0], hd[1] - 41, "maaf ya", 10, (40, 40, 50))))
    return dict(A=A, B=B)

# ------------------------------------------------------------------ mesin panel
def hero_state(t, A, st):
    x = 150
    if A:
        hit = sum(pulse(t - m) for m in IMP)
        r = sum(ease((t - (m + 0.15)) / 1.0) for m in IMP)
        face = "hit" if hit > 0.05 else ("sad" if r > 0.5 else (st.get("hero_face") or "hope"))
        sit = max(st.get("hero_sit", 0.0), ease((t - 9.6) / 0.8))
        return dict(x=x + 14 * hit, f=1, face=face, lean=0.04 * r - 0.25 * hit, head=0.12 * r, arm=25 + 25 * hit, sit=sit, hit=hit, r=r)
    face = "happy" if t >= BURST else ("calm" if t >= ACT else (st.get("hero_face") or "hope"))
    sit = st.get("hero_sit", 0.0) * (1 - 0.5 * ease((t - 6.4) / 0.8))
    return dict(x=x, f=1, face=face, lean=0.0, head=0.0, arm=25, sit=sit, hit=0.0, r=0.0)

def panel(st, t, side):
    A = side == "A"
    p = BG.copy()
    h = hero_state(t, A, st)
    lay, _, hd = fig_layer(h["x"], FLOOR, WHITE, f=h["f"], lean=h["lean"], head=h["head"], arm_f=h["arm"], sit=h["sit"], face=h["face"])
    h.update(lay=lay, hd=hd, hand=base.LAST_HAND)
    if not A:
        glow = ease((t - 6.4) / 2.5) * 1.2 + 0.6 * pulse(t - BURST, 0.6)
        paste_glow(p, 600, 290, glow)
        ring_pulse(p, 300, t - ACT)
    c = Ctx(p, t, side, h)
    (st["A"] if A else st["B"])(c)
    c.put_hero()
    if A:
        for m in IMP: shock(p, h["x"] + 8, hd[1] + 40, t - m, RED)
        fall = ease((t - (IMP[2] + 0.6)) / 0.9)
        if h["r"] > 0.15 and fall < 1: broken_heart(p, h["x"] - 4, hd[1] - 44, 1.0, h["r"], fall)
        if t > base.TEARS[0]: tears(p, hd, 1, t)
        base.rain(p, (h["r"] - 0.3) / 2.0, t)
        vignette(p, 0.75 * clamp(h["r"] / 3) + 0.35 * h["hit"])
        overlay(p, (200, 40, 55), 0.30 * sum(pulse(t - m, 0.35) for m in IMP))
        return p, 9 * h["hit"] * math.sin(t * 90), 5 * h["hit"] * math.cos(t * 77)
    shock(p, h["x"] + 10, hd[1] + 40, t - BURST, (255, 214, 140), rmax=150, dur=0.8)
    sparks(p, h["x"] + 10, hd[1] + 30, t - BURST)
    hu = ease((t - 9.7) / 0.5)
    if hu > 0: heart(p, h["x"] + 60, hd[1] - 50 + 3 * math.sin(t * 5), 0.7 * (1 + 0.12 * abs(math.sin(t * 6))), hu)
    for i in range(5):
        u = (t - (10.3 + 0.6 * i)) / 1.8
        if 0 <= u < 1: heart(p, 300 + 22 * i + 8 * math.sin(u * 6 + i), 200 - 80 * u, 0.36, math.sin(math.pi * u))
    overlay(p, (255, 205, 120), 0.28 * pulse(t - BURST, 0.5) + 0.06 * pulse(t - ACT, 0.5))
    return p, 0.0, 0.0

base.TEARS[:] = [9.9 + 0.55 * i + 0.13 * (i % 3) for i in range(6)]

def fit_font(d, segs, maxw=660):
    f = F_PUNCH; full = "".join(s for s, _ in segs)
    while sum(d.textlength(ch, font=f) for ch in full) + 3 * (len(full) - 1) > maxw and f.size > 30: f = font(f.size - 2)
    return f

def render(st, t):
    fr = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(fr)
    dim = 1 - 0.65 * ease((t - 12.0) / 0.8)
    l1 = st["title1"]; spaced(d, l1, W / 2, 84, F_TITLE, scale_col(WHITE, dim), nchars=int(len(l1) * clamp((t - 0.2) / 1.4) + 0.999))
    if t >= 10.0:
        l2 = st["title2"]; tf = F_TITLE if len(l2) <= 26 else font(24)
        spaced(d, l2, W / 2, 126, tf, scale_col(WHITE, dim), nchars=int(len(l2) * clamp((t - 10.0) / 1.3) + 0.999))
    fade_end = clamp((DUR - t) / 0.5)
    k = ease(t / 0.8) * lerp(1.0, 0.10, ease((t - 12.0) / 0.8)) * fade_end
    black = Image.new("RGB", (PW, PH), (0, 0, 0))
    pa = finish_panel(panel(st, t, "A"), st["la"], st["at"], t, BLUE)
    pb = finish_panel(panel(st, t, "B"), st["lb"], st["bt"], t, (170, 180, 200), AMBER, BURST)
    fr.paste(Image.blend(black, pa, k), (PX, PYA)); fr.paste(Image.blend(black, pb, k), (PX, PYB))
    pu = ease((t - 12.6) / 0.6) * fade_end
    if pu > 0:
        f1, f2 = fit_font(d, st["p1"]), fit_font(d, st["p2"]); fp = f1 if f1.size < f2.size else f2
        spaced_multi(d, st["p1"], W / 2, 600, fp, alpha=pu); spaced_multi(d, st["p2"], W / 2, 672, fp, alpha=pu)
    su = ease((t - 14.6) / 0.8) * fade_end
    if su > 0:
        spaced(d, st["s1"], W / 2, 1000, F_SUB, scale_col(GREY, su), sp=2); spaced(d, st["s2"], W / 2, 1038, F_SUB, scale_col(GREY, su), sp=2)
    fade = clamp(1 - t / 0.4)
    if fade > 0: fr = Image.blend(fr, Image.new("RGB", (W, H), (0, 0, 0)), fade)
    return fr

def make_audio(path, seed=7):
    sr = 44100; n = int(sr * DUR); t = np.arange(n) / sr; rs = np.random.RandomState(seed)
    out = 0.03 * np.sin(2 * np.pi * 55 * t) + 0.008 * np.convolve(rs.randn(n), np.ones(40) / 40, mode="same")
    def add(t0, sig):
        i = int(t0 * sr); j = min(n, i + len(sig))
        if i < n: out[i:j] += sig[:j - i]
    def burst(dur, amp): m = int(sr * dur); return amp * np.diff(rs.randn(m), prepend=0) * np.exp(-np.linspace(0, 6, m))
    def tone(f, dur, amp, decay=3.0, attack=0.0):
        m = int(sr * dur); x = np.arange(m) / sr; env = np.exp(-x * decay)
        if attack: env *= np.minimum(1, x / attack)
        return amp * np.sin(2 * np.pi * f * x) * env
    def sweep(f0, f1, dur, amp): m = int(sr * dur); f = np.linspace(f0, f1, m); return amp * np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-np.linspace(0, 4, m))
    def lp(dur, amp, k=60): return amp * np.convolve(rs.randn(int(sr * dur)), np.ones(k) / k, mode="same")
    def heartbeat(t0, amp=0.35, f=62): add(t0, tone(f, 0.18, amp, 22)); add(t0 + 0.17, tone(f * 0.85, 0.2, amp * 0.7, 20))
    m = int(sr * (12.0 - IMP[0])); add(IMP[0], lp(12.0 - IMP[0], 0.05, 6) * np.linspace(0, 1, m) ** 1.5)
    for tt in np.arange(2.0, 3.8, 0.4): add(tt, tone(95, 0.09, 0.05, 40))
    add(3.0, tone(660, 0.6, 0.04, 4)); add(3.2, tone(880, 0.5, 0.03, 5))
    for k, hh in enumerate(IMP):
        add(hh, tone(52, 0.7, 0.7, 6)); add(hh, burst(0.16, 0.22)); add(hh, tone(2637, 0.25, 0.03, 18)); add(hh, sweep(380, 150, 0.5, 0.1))
        heartbeat(hh + 0.45, 0.28 - 0.05 * k, 55); heartbeat(hh + 0.95, 0.2 - 0.04 * k, 52)
    for tt in base.TEARS: add(tt + 0.7, tone(1500, 0.12, 0.05, 30) * np.linspace(1, 0.4, int(sr * 0.12)))
    add(10.4, lp(0.9, 0.12, 30) * np.linspace(1, 0, int(sr * 0.9)))
    for i, fq in enumerate((440.0, 392.0, 329.6)): add(10.5 + i * 0.45, tone(fq, 1.6, 0.045, 2.6))
    add(ACT, tone(310, 0.12, 0.2, 30)); add(ACT + 0.1, lp(0.9, 0.1, 30) * np.linspace(1, 0, int(sr * 0.9))); add(ACT + 0.1, tone(880, 0.8, 0.04, 4)); add(ACT + 0.2, tone(1318, 0.7, 0.03, 5))
    m = int(sr * 3.0); x_ = np.arange(m) / sr
    add(6.4, 0.04 * np.sin(2 * np.pi * np.cumsum(220 + 120 * x_ / 3.0) / sr) * np.sin(np.linspace(0, np.pi, m)))
    heartbeat(BURST - 0.5, 0.35, 66); heartbeat(BURST - 0.1, 0.38, 70); add(BURST, tone(110, 0.8, 0.35, 5))
    for i, fq in enumerate((1046.5, 1318.5, 1568.0, 2093.0, 2637.0)): add(BURST + 0.05 + i * 0.07, tone(fq, 1.0, 0.035, 4))
    for fq in (523.3, 659.3, 784.0): add(BURST + 0.2, tone(fq, 1.8, 0.05, 2.0))
    for i in range(4): add(10.5 + 0.6 * i, tone(1760, 0.35, 0.015, 8))
    m = int(sr * 1.5); x_ = np.arange(m) / sr
    add(10.5, 0.07 * np.sin(2 * np.pi * np.cumsum(180 + 600 * (x_ / 1.5) ** 1.6) / sr) * np.linspace(0, 1, m) ** 1.5)
    add(12.0, tone(50, 1.4, 0.55, 3.2)); add(12.0, burst(0.28, 0.22))
    for fq in (261.6, 329.6, 392.0, 523.3): add(12.1, tone(fq, 7.0, 0.05, 0.45, attack=0.5))
    add(13.0, tone(1568, 1.5, 0.02, 2.5))
    out *= np.clip((DUR - t) / 0.5, 0, 1); out = out / max(1e-6, np.abs(out).max()) * 0.8
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes((out * 32767).astype(np.int16).tobytes())

def main():
    key = sys.argv[1]; st = STORIES[key]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), f"cerita-{key}.mp4")
    pv = os.environ.get("PREVIEW")
    if pv:
        for tt in pv.split(","): render(st, float(tt)).save(f"{out}_{tt}.png")
        return
    tmp = tempfile.mkdtemp(); wav = os.path.join(tmp, "a.wav"); make_audio(wav, seed=sum(map(ord, key)) % 1000)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)): p.stdin.write(render(st, i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("selesai:", out)

if __name__ == "__main__":
    main()
