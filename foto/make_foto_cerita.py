#!/usr/bin/env python3
"""Foto & karosel 1080x1350 dengan gaya video cerita yang menang (dua panel panggung, DIA YANG ...,
hati retak/hujan vs cahaya hangat, kalimat penutup emas + putih). Memakai mesin make_video_cerita.py.
Pakai: python3 make_foto_cerita.py <folder-keluaran>"""
import importlib.util, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
VID = os.path.join(HERE, "..", "video")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "cerita")
sys.argv = [sys.argv[0]]; sys.path.insert(0, VID); sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("mc", os.path.join(VID, "make_video_cerita.py")); mc = importlib.util.module_from_spec(spec); spec.loader.exec_module(mc)
from PIL import Image, ImageDraw
from cerita_base import font, finish_panel, AMBER, BLUE, WHITE, GREY, FLOOR, PH, PW, scale_col
W, H = 1080, 1350
T_STILL = 10.6

# ------------------------------------------------------------------ pabrik cerita foto
def dialog(la, lb, line, qa, qb):
    def A(c):
        c.dia(450, f=1, face="calm", arm_f=15)
        mc.bub(c, 450, 172, qa, "r", size=16)
    def B(c):
        c.dia(245, f=-1, face="happy", arm_f=60, lit=1.0)
        mc.bub(c, 330, 172, qb, "w", size=16)
    return dict(A=A, B=B, la=la, lb=lb, at=[(0, ""), (0.1, line)], bt=[(0, ""), (0.1, line)])

def kirain(kir, ter):
    def A(c):
        hh = c.h["hand"]
        mc.layer(c.p, lambda d: mc.RC(d, hh[0] + 2, hh[1] - 9, hh[0] + 10, hh[1] + 5, fill=(170, 200, 255)))
        mc.layer(c.p, lambda d: (mc.EL(d, 190, 195, 4, fill=(230, 230, 236)), mc.EL(d, 205, 180, 6, fill=(230, 230, 236))))
        mc.bub(c, 330, 150, kir, "n", size=15)
    def B(c):
        c.dia(330, f=-1, face="calm", arm_f=30, lit=1.0)
        mc.bub(c, 330, 172, ter, "w", size=15)
    return dict(A=A, B=B, la="KIRAIN...", lb="TERNYATA...", at=[(0, ""), (0.1, "YANG ADA DI KEPALAMU.")], bt=[(0, ""), (0.1, "YANG SEBENARNYA TERJADI.")])

def angka(la, lb, line, qa, big, qb):
    def A(c):
        c.dia(330, f=-1, face="hit", arm_f=150, arm_b=120, lean=0.15)
        mc.bub(c, 360, 172, qa, "r", size=16)
    def B(c):
        mc.paste_glow(c.p, 330, 112, 0.6)
        mc.layer(c.p, lambda d: mc.TX(d, 330, 108, big, 38, mc.GOLD))
        c.dia(330, f=-1, face="happy", arm_f=30, lit=1.0)
        mc.bub(c, 360, 200, qb, "w", size=15)
    return dict(A=A, B=B, la=la, lb=lb, at=[(0, ""), (0.1, line)], bt=[(0, ""), (0.1, line)])

# benda (perumpamaan) -------------------------------------------------
def heart_shape(d, x, y, s, col):
    pts = []
    for i in range(48):
        a = i / 48 * 2 * math.pi
        pts.append((x + 16 * math.sin(a) ** 3 * s, y - (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) * s))
    mc.PG(d, pts, col)
def b_perban():
    def A(c):
        c.dia(470, f=1, face="calm", arm_f=15)
        def fn(d):
            heart_shape(d, 310, 200, 2.6, (200, 90, 100)); mc.LN(d, [(310, 160), (300, 190), (318, 210), (304, 240)], (20, 14, 20), 3)
            mc.RC(d, 280, 186, 340, 202, fill=(240, 220, 190), rad=4)
        mc.layer(c.p, fn)
    def B(c):
        mc.paste_glow(c.p, 310, 200, 0.6)
        c.dia(380, f=-1, face="happy", arm_f=80, lit=1.0, sit=0.6)
        mc.layer(c.p, lambda d: heart_shape(d, 310, 200, 2.6, (255, 120, 140)))
    return dict(A=A, B=B, la="DIA YANG SEKADAR MINTA MAAF", lb="DIA YANG MERAWAT LUKANYA", at=[(0, ""), (0.1, "MAAF = PERBAN.")], bt=[(0, ""), (0.1, "MAAF = PERBAN.")])
def b_pagar():
    def A(c):
        mc.layer(c.p, lambda d: [mc.RC(d, 230 + (i % 2) * 18, FLOOR - 26 - 22 * j, 266 + (i % 2) * 18, FLOOR - 6 - 22 * j, fill=(130, 80, 70), out=(90, 54, 46), w=1) for j in range(8) for i in range(1)] and None)
        mc.layer(c.p, lambda d: [mc.RC(d, 236, FLOOR - 22 * (j + 1), 280, FLOOR - 22 * j - 2, fill=(140, 86, 72), out=(90, 54, 46), w=1) for j in range(9)] and None)
        c.dia(420, f=-1, face="calm", arm_f=15)
    def B(c):
        def fn(d):
            for i in range(6): mc.RC(d, 220 + i * 14, FLOOR - 50, 226 + i * 14, FLOOR, fill=(200, 170, 120))
            mc.LN(d, [(216, FLOOR - 36), (306, FLOOR - 36)], (200, 170, 120), 4)
        mc.layer(c.p, fn)
        c.dia(360, f=-1, face="happy", arm_f=60, lit=1.0)
    return dict(A=A, B=B, la="DIA YANG MEMBANGUN TEMBOK", lb="DIA YANG MEMASANG PAGAR", at=[(0, ""), (0.1, "BATAS = PAGAR, BUKAN TEMBOK.")], bt=[(0, ""), (0.1, "BATAS = PAGAR, BUKAN TEMBOK.")])
def b_gelas():
    def glass(d, x, y, lvl, leak):
        mc.PG(d, [(x - 22, y - 60), (x + 22, y - 60), (x + 16, y), (x - 16, y)], (150, 190, 230), a=110)
        if lvl > 0: mc.PG(d, [(x - 22 + 6 * (1 - lvl), y - 60 * lvl), (x + 22 - 6 * (1 - lvl), y - 60 * lvl), (x + 16, y), (x - 16, y)], (90, 150, 230))
        if leak:
            for i in range(4): mc.EL(d, x + 2, y + 10 + i * 14, 2.4, fill=(90, 150, 230))
    def A(c):
        c.dia(440, f=1, face="calm", arm_f=15)
        hh = c.h["hand"]; mc.layer(c.p, lambda d: glass(d, hh[0] + 22, hh[1] + 10, 0.1, True))
    def B(c):
        hh = c.h["hand"]; mc.paste_glow(c.p, hh[0] + 22, hh[1] - 20, 0.5)
        mc.layer(c.p, lambda d: glass(d, hh[0] + 22, hh[1] + 10, 0.9, False))
        c.dia(330, f=-1, face="happy", arm_f=30, lit=1.0)
    return dict(A=A, B=B, la="DIA YANG MENGURAS", lb="DIA YANG IKUT MENGISI", at=[(0, ""), (0.1, "HATI = GELAS.")], bt=[(0, ""), (0.1, "HATI = GELAS.")])
def b_jampasir():
    def hour(d, x, y, top):
        mc.PG(d, [(x - 24, y - 70), (x + 24, y - 70), (x + 3, y - 36), (x - 3, y - 36)], (200, 200, 215), a=90)
        mc.PG(d, [(x - 3, y - 34), (x + 3, y - 34), (x + 24, y), (x - 24, y)], (200, 200, 215), a=90)
        mc.PG(d, [(x - 20 * top, y - 38 - 30 * top), (x + 20 * top, y - 38 - 30 * top), (x, y - 38)], (240, 200, 120))
        mc.PG(d, [(x - 20 * (1 - top), y), (x + 20 * (1 - top), y), (x, y - 30 * (1 - top))], (240, 200, 120))
        mc.RC(d, x - 28, y - 76, x + 28, y - 70, fill=(140, 110, 80)); mc.RC(d, x - 28, y, x + 28, y + 6, fill=(140, 110, 80))
    def A(c):
        mc.layer(c.p, lambda d: hour(d, 300, FLOOR - 8, 0.08))
        hand, _ = c.dia(460, f=1, face="calm", arm_f=60, head=0.25)
        mc.layer(c.p, lambda d: mc.RC(d, hand[0] + 2, hand[1] - 9, hand[0] + 10, hand[1] + 5, fill=(170, 200, 255)))
    def B(c):
        mc.paste_glow(c.p, 300, FLOOR - 50, 0.4)
        mc.layer(c.p, lambda d: hour(d, 300, FLOOR - 8, 0.85))
        c.dia(380, f=-1, face="happy", arm_f=30, lit=1.0, sit=1.0)
    return dict(A=A, B=B, la="DIA YANG MENUNDA", lb="DIA YANG MENYEMPATKAN", at=[(0, ""), (0.1, "WAKTU = JAM PASIR.")], bt=[(0, ""), (0.1, "WAKTU = JAM PASIR.")])
def b_benang():
    def A(c):
        def fn(d):
            for i in range(14):
                a = i * 0.9; mc.EL(d, 310 + 18 * math.cos(a), 250 + 14 * math.sin(a * 1.3), 26 - i, out=(230, 120, 150), w=1.6)
            mc.LN(d, [c.h["hand"], (286, 250)], (230, 120, 150), 1.6)
        mc.layer(c.p, fn)
        hand, _ = c.dia(450, f=-1, face="hit", arm_f=80, lean=-0.2)
        mc.layer(c.p, lambda d: mc.LN(d, [(334, 250), hand], (230, 120, 150), 1.6))
    def B(c):
        hand, _ = c.dia(400, f=-1, face="happy", arm_f=80, lit=1.0)
        mc.layer(c.p, lambda d: mc.LN(d, [c.h["hand"], ((c.h["hand"][0] + hand[0]) / 2, c.h["hand"][1] + 14), hand], (230, 120, 150), 2))
    return dict(A=A, B=B, la="DIA YANG MENARIK PAKSA", lb="DIA YANG MENGURAI PELAN", at=[(0, ""), (0.1, "MASALAH = BENANG KUSUT.")], bt=[(0, ""), (0.1, "MASALAH = BENANG KUSUT.")])
def b_pelampung():
    def water(d): mc.RC(d, 0, FLOOR - 40, PW, PH, fill=(24, 40, 80), a=230)
    def A(c):
        mc.layer(c.p, water)
        c.dia(470, f=-1, face="calm", arm_f=80)
        mc.layer(c.p, lambda d: (mc.EL(d, 300, FLOOR - 20, 14, fill=(90, 90, 100)), mc.LN(d, [(300, FLOOR - 34), (300, FLOOR - 60)], (90, 90, 100), 4)))
    def B(c):
        mc.layer(c.p, water)
        c.dia(470, f=-1, face="happy", arm_f=80, lit=1.0)
        mc.layer(c.p, lambda d: (mc.EL(d, 210, FLOOR - 40, 22, out=(240, 120, 100), w=7), mc.LN(d, [(232, FLOOR - 40), (440, FLOOR - 140)], (220, 220, 230), 1.5)))
    return dict(A=A, B=B, la="DIA YANG MELEMPAR JANGKAR", lb="DIA YANG MELEMPAR PELAMPUNG", at=[(0, ""), (0.1, "DUKUNGAN = PELAMPUNG.")], bt=[(0, ""), (0.1, "DUKUNGAN = PELAMPUNG.")], hero_sit=1.0, hero_face="sad")

# ------------------------------------------------------------------ data
AB = [  # file, judul1, judul2, cerita, punch1, punch2, sub1, sub2
 ("ab-01", "DIA MULAI CUEK.", "DUA PASANGAN. DUA CARA.", dialog("DIA YANG MENYANGKAL", "DIA YANG MENDENGAR", "KAMU AKHIR-AKHIR INI CUEK.", "perasaanmu aja", "ceritain, aku dengerin"), "DENGARKAN,", "JANGAN DIBANTAH.", "PERASAAN PERLU DIDENGAR,", "BUKAN DIBANTAH."),
 ("ab-02", "BERTENGKAR LARUT MALAM.", "DUA PASANGAN. DUA CARA.", dialog("DIA YANG PERGI", "DIA YANG BERTAHAN", "AKU MASIH MARAH SOAL TADI.", "terserah, aku pergi", "lanjut besok, aku di sini"), "MARAH BOLEH,", "PERGI JANGAN.", "JEDA BOLEH.", "MENGHILANG JANGAN."),
 ("ab-03", "SAAT BEDA PENDAPAT.", "DUA PASANGAN. DUA CARA.", dialog("DIA YANG MAU MENANG", "DIA YANG MAU MEMAHAMI", "PENDAPATKU BEDA.", "aku yang benar", "aku dengerin versimu"), "MENANG DEBAT,", "KALAH DEKAT.", "YANG DICARI BUKAN MENANG,", "TAPI SALING MENGERTI."),
 ("ab-04", "CERITA MASA LALU.", "DUA PASANGAN. DUA CARA.", dialog("DIA YANG MENGABAIKAN", "DIA YANG MENDENGAR", "AKU MAU CERITA MASA LALUKU.", "gak penting", "aku dengerin pelan-pelan"), "JUJUR TIDAK", "HARUS SEKALIGUS.", "YANG PENTING", "ADA YANG MAU MENDENGAR."),
 ("ab-05", "ULANG TAHUN TERLUPA.", "DUA PASANGAN. DUA CARA.", dialog("DIA YANG MENGELAK", "DIA YANG MENEBUS", "KAMU LUPA ULANG TAHUNKU.", "kan aku sibuk", "maaf, aku tebus ya"), "LUPA ITU WAJAR,", "MENEBUS ITU PILIHAN.", "MAAF YANG TULUS", "DATANG DENGAN TINDAKAN."),
 ("ab-06", "SAAT PASANGAN SAKIT.", "DUA PASANGAN. DUA CARA.", dialog("DIA YANG MENYEPELEKAN", "DIA YANG MENEMANI", "AKU LAGI GAK ENAK BADAN.", "minum obat aja", "kubawain bubur ya"), "PEDULI", "ITU HADIR.", "OBAT UNTUK BADAN.", "KEHADIRAN UNTUK HATI."),
 ("ab-07", "SAAT DIPERCAYAI CERITA.", "DUA PASANGAN. DUA CARA.", dialog("DIA YANG MEMBOCORKAN", "DIA YANG MENJAGA", "INI RAHASIA YA.", "eh, tau gak dia cerita...", "rahasiamu aman"), "RAHASIA", "ITU AMANAH.", "YANG DIPERCAYA", "MENJAGA."),
 ("ab-08", "SAAT NGAMBEK.", "DUA PASANGAN. DUA CARA.", dialog("DIA YANG MINTA DITEBAK", "DIA YANG BILANG JUJUR", "KAMU KENAPA?", "tebak sendiri", "aku kesal karena tadi"), "PERASAAN", "ITU DIUCAPKAN.", "PASANGAN BUKAN", "PEMBACA PIKIRAN."),
 ("ab-09", "SOAL JANJI.", "DUA PASANGAN. DUA CARA.", dialog("DIA YANG BERJANJI MANIS", "DIA YANG MENEPATI", "KAMU JADI TELEPON?", "nanti pasti kutepati", "jam 8 aku telepon"), "JANJI KECIL", "YANG DITEPATI.", "KEPERCAYAAN DIBANGUN", "DARI HAL KECIL."),
 ("foto-red-vs-green-bertengkar", "SAAT BERTENGKAR.", "RED FLAG VS GREEN FLAG.", dialog("RED FLAG", "GREEN FLAG", "KITA LAGI SAMA-SAMA MARAH.", "terserah! *banting pintu*", "aku butuh waktu, nanti kita bahas"), "MINTA WAKTU,", "LALU KEMBALI.", "FOKUS KE MASALAHNYA,", "BUKAN ORANGNYA."),
]
BAL = [
 ("bal-01", "dia cuma balas 'ok'", "dia lagi di rumah sakit", "JANGAN MENEBAK", "CERITA ORANG."),
 ("bal-02", "dia mulai dingin", "dia kewalahan di kerjaan", "DINGIN TIDAK SELALU", "BERARTI PERGI."),
 ("bal-03", "dia sempurna sekali", "itu cuma pencitraan", "KONSISTEN LEBIH", "PENTING DARI MANIS."),
 ("bal-04", "aku yang salah terus", "aku yang dikendalikan", "MINTA MAAF TERUS", "BUKAN TANDA SALAH."),
 ("bal-05", "ditolak = akhir segalanya", "aku diselamatkan", "DITOLAK BISA", "JADI DILINDUNGI."),
 ("bal-06", "'kita perlu bicara'", "dia mau bilang makasih", "JANGAN LANGSUNG", "MENEBAK YANG TERBURUK."),
]
BAL2 = [
 ("dia yang paling lucu", "dia yang paling butuh didengar", "YANG TERTAWA BELUM TENTU", "BAIK-BAIK SAJA."),
 ("'aku sibuk'", "dia memang menghindar", "SIBUK BISA ALASAN,", "BISA PILIHAN."),
 ("posesif karena sayang", "takut kehilangan kendali", "SAYANG", "TIDAK MENGURUNG."),
 ("'dia berubah'", "kamu baru lihat aslinya", "AWAL BISA MENIPU,", "POLA TIDAK."),
 ("mantan yang dibenci", "guru yang paling jujur", "YANG PERGI MENGAJARKAN", "BATASMU."),
]
HIT = [
 ("hit-01", angka("DIA YANG BILANG LUPA", "DIA YANG MENEPATI", "JANJINYA LUPA LAGI.", "lupa lagi, maaf", "3 KALI", "kali ini kutepati"), "SATU KALI MANUSIA,", "TIGA KALI POLA."),
 ("hit-02", angka("DIA YANG LANGSUNG MEMBALAS", "DIA YANG JEDA 5 DETIK", "SAAT SEDANG MARAH.", "kamu selalu begitu!", "5 DETIK", "tarik napas dulu ya"), "LIMA DETIK MENYELAMATKAN", "SATU MALAM."),
 ("hit-03", angka("DIA YANG MENGHILANG", "DIA YANG MEMBERI KABAR", "SEHARIAN TANPA KABAR.", "lupa ngabarin", "2 MENIT", "lagi meeting, nanti kutelpon"), "DUA MENIT MENGHEMAT", "DUA HARI CURIGA."),
 ("hit-04", angka("DIA YANG PUTUS SAAT MARAH", "DIA YANG MENUNGGU 24 JAM", "SEDANG SANGAT MARAH.", "kita putus aja!", "24 JAM", "kita bahas besok pagi"), "BESOK PAGI", "LEBIH JERNIH."),
]
HIT2 = [
 (angka("DIA YANG DIAM BERJAM-JAM", "DIA YANG MULAI BICARA", "SETELAH BERTENGKAR.", "...", "10 MENIT", "aku minta maaf duluan ya"), "SEPULUH MENIT PERTAMA", "MENENTUKAN MALAM."),
 (angka("DIA YANG LANGSUNG BERDEBAT", "DIA YANG MEMELUK DULU", "SAAT TEGANG.", "dengerin aku dulu!", "20 DETIK", "sini, peluk dulu"), "PELUK DULU,", "BICARA KEMUDIAN."),
 (angka("DIA YANG TERUS MENGECEK", "DIA YANG MENCORET KALENDER", "SETELAH PUTUS.", "aku cek story dia lagi", "30 HARI", "hari ke-30, aku lebih ringan"), "BERI WAKTU", "UNTUK PULIH."),
 (angka("DIA YANG LUPA KATA AJAIB", "DIA YANG MENGUCAPKANNYA", "SEHARI-HARI.", "ambilin itu", "3 KALIMAT", "tolong, maaf, makasih"), "TIGA KATA,", "SETENGAH HUBUNGAN."),
 (angka("DIA YANG BANYAK BICARA", "DIA YANG BERTINDAK", "SOAL PERHATIAN.", "aku sayang kamu banget", "1 TINDAKAN", "aku jemput ya"), "LIHAT", "TINDAKANNYA."),
]
BEN = [
 ("ben-01", "MAAF = PERBAN.", b_perban(), "MAAF TANPA DIOBATI", "TIDAK SEMBUH."),
 ("ben-02", "BATAS = PAGAR.", b_pagar(), "PAGAR MENJAGA,", "TEMBOK MEMISAHKAN."),
 ("ben-03", "HATI = GELAS.", b_gelas(), "GELAS YANG BOCOR", "TIDAK PERNAH PENUH."),
 ("ben-04", "WAKTU = JAM PASIR.", b_jampasir(), "WAKTU MENUNJUKKAN", "PRIORITAS."),
 ("ben-05", "MASALAH = BENANG KUSUT.", b_benang(), "DIURAI PELAN,", "BUKAN DITARIK PAKSA."),
 ("ben-06", "DUKUNGAN = PELAMPUNG.", b_pelampung(), "SAAT DIA TENGGELAM,", "LEMPAR PELAMPUNG."),
]
CAROUSEL1 = [  # situasi A vs B (karosel 'sama masalah, beda cara')
 ("CHAT BELUM DIBALAS.", dialog("DIA YANG MENGELAK", "DIA YANG MENGAKUI", "CHAT AKU BELUM KAMU BALAS.", "aku kan sibuk", "maaf, aku bales sekarang"), "KABAR KECIL,", "RASA AMAN BESAR."),
 ("SAAT CEMBURU DATANG.", dialog("DIA YANG MEREMEHKAN", "DIA YANG MENJELASKAN", "AKU CEMBURU SAMA DIA.", "kamu berlebihan", "makasih udah jujur"), "CEMBURU DIBICARAKAN,", "BUKAN DISELIDIKI."),
 ("TELAT JEMPUT.", dialog("DIA YANG MENYEPELEKAN", "DIA YANG MENGAKUI", "KAMU TELAT LAGI.", "gitu aja marah", "maaf, harusnya kukabari"), "MAAF YANG TULUS", "MENYEBUT KESALAHANNYA."),
 ("SAAT DIKRITIK.", dialog("DIA YANG MENGEJEK", "DIA YANG MENERIMA", "CARAMU BICARA BIKIN SAKIT.", "kamu terlalu sensitif", "aku mau perbaiki ya"), "KRITIK DIDENGAR,", "BUKAN DIBALAS SERANGAN."),
 ("MINTA RUANG.", dialog("DIA YANG BILANG TERSERAH", "DIA YANG MEMBERI RUANG", "BESOK AKU MAIN SAMA TEMAN.", "terserah", "seru-seruan, kabarin ya"), "MEMBERI RUANG", "BUKAN MEMBIARKAN."),
 ("PASANGAN CAPEK.", dialog("DIA YANG MELAMPIASKAN", "DIA YANG MENEMANI", "AKU CAPEK, BUTUH NGOBROL.", "aku juga capek!", "sini, aku temani"), "CAPEK TIDAK JADI", "ALASAN MENYAKITI."),
]

# ------------------------------------------------------------------ komposisi
def spaced(d, text, cx, cy, fnt, fill, sp=4):
    ws = [d.textlength(ch, font=fnt) for ch in text]; x = cx - (sum(ws) + sp * (len(text) - 1)) / 2
    for ch, w in zip(text, ws): d.text((x, cy), ch, font=fnt, fill=fill, anchor="lm"); x += w + sp
def fit(d, text, size, maxw, sp=4):
    f = font(size)
    while sum(d.textlength(ch, font=f) for ch in text) + sp * (len(text) - 1) > maxw and size > 18: size -= 2; f = font(size)
    return f
def panel_img(st, side):
    st = dict(st); st.setdefault("A", lambda c: None)
    sc = mc.panel(st, T_STILL, side)
    lab = st["la"] if side == "A" else st["lb"]
    txt = st["at"] if side == "A" else st["bt"]
    p = finish_panel(sc, lab, txt, T_STILL, BLUE, AMBER if side == "B" else None, 0.0)
    return p.crop((0, 0, PW, 392)).resize((780, int(392 * 780 / PW)), Image.LANCZOS)
def poster(st, path, t1, t2, p1, p2, note=None, counter=None):
    fr = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(fr)
    spaced(d, t1, W / 2, 58, fit(d, t1, 38, 980), WHITE)
    spaced(d, t2, W / 2, 104, fit(d, t2, 30, 980), (200, 204, 214), sp=3)
    a, b = panel_img(st, "A"), panel_img(st, "B")
    fr.paste(a, (150, 132)); fr.paste(b, (150, 132 + a.size[1] + 14))
    y = 132 + 2 * a.size[1] + 14
    f = fit(d, max(p1, p2, key=len), 58, 980, 3)
    spaced(d, p1, W / 2, y + 48, f, AMBER, 3); spaced(d, p2, W / 2, y + 112, f, WHITE, 3)
    if note: spaced(d, note, W / 2, H - 26, font(18), GREY, 2)
    if counter: d.text((W - 40, 30), counter, font=font(22), fill=GREY, anchor="rm")
    fr.save(path, quality=93, subsampling=0)
def title_card(path, l1, l2, sub, still=None, cta=None):
    fr = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(fr)
    if still is not None: fr.paste(panel_img(still, "B"), (150, 640))
    f = fit(d, max(l1, l2, key=len), 86, 980, 4)
    spaced(d, l1, W / 2, 300, f, WHITE); spaced(d, l2, W / 2, 400, f, AMBER)
    spaced(d, sub, W / 2, 500, fit(d, sub, 30, 960, 2), GREY, 2)
    if cta: spaced(d, cta, W / 2, 1230 if still is None else 1215, fit(d, cta, 30, 960, 2), AMBER, 2)
    fr.save(path, quality=93, subsampling=0)

if __name__ == "__main__":
    for sub in ("harian", "karosel", "karosel2", "karosel3"): os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    for f, t1, t2, st, p1, p2, s1, s2 in AB:
        dst = os.path.join(OUT, f + ".jpg") if f.startswith("foto-") else os.path.join(OUT, "harian", f + ".jpg")
        poster(st, dst, t1, t2, p1, p2, note=f"{s1} {s2}")
    for f, kir, ter, p1, p2 in BAL:
        poster(kirain(kir, ter), os.path.join(OUT, "harian", f + ".jpg"), "KIRAIN VS TERNYATA.", "JANGAN MENEBAK YANG TERBURUK.", p1, p2, note="CONTOH ILUSTRASI.")
    for f, st, p1, p2 in HIT:
        poster(st, os.path.join(OUT, "harian", f + ".jpg"), "ANGKA KECIL.", "HUBUNGAN DIJAGA HAL KECIL.", p1, p2)
    for f, t1, st, p1, p2 in BEN:
        poster(st, os.path.join(OUT, "harian", f + ".jpg"), t1, "PERUMPAMAAN CINTA.", p1, p2)
    # karosel 1 (8 slide)
    title_card(os.path.join(OUT, "karosel", "karosel-01.jpg"), "SAMA MASALAH.", "BEDA CARA.", "6 SITUASI PASANGAN A VS B. GESER.", CAROUSEL1[0][1], "GESER →")
    for i, (t1, st, p1, p2) in enumerate(CAROUSEL1):
        poster(st, os.path.join(OUT, "karosel", f"karosel-{i + 2:02d}.jpg"), t1, "DUA PASANGAN. DUA CARA.", p1, p2, counter=f"{i + 2:02d}/08")
    title_card(os.path.join(OUT, "karosel", "karosel-08.jpg"), "KAMU YANG", "MANA?", "TULIS A ATAU B DI KOMENTAR.", None, "SIMPAN, LALU KIRIM KE DIA YANG PERLU BACA.")
    # karosel 2 (7 slide)
    title_card(os.path.join(OUT, "karosel2", "karosel-01.jpg"), "KIRAIN", "VS TERNYATA.", "5 CERITA YANG SERING SALAH KITA KIRA.", kirain(*BAL2[0][:2]), "GESER →")
    for i, (kir, ter, p1, p2) in enumerate(BAL2):
        poster(kirain(kir, ter), os.path.join(OUT, "karosel2", f"karosel-{i + 2:02d}.jpg"), "KIRAIN VS TERNYATA.", f"CERITA {i + 1:02d}.", p1, p2, note="CONTOH ILUSTRASI.", counter=f"{i + 2:02d}/07")
    title_card(os.path.join(OUT, "karosel2", "karosel-07.jpg"), "PERNAH", "SALAH KIRA?", "CERITAIN DI KOMENTAR.", None, "SIMPAN, LALU KIRIM KE DIA YANG PERLU BACA.")
    # karosel 3 (7 slide)
    title_card(os.path.join(OUT, "karosel3", "karosel-01.jpg"), "5 ANGKA KECIL", "YANG MENYELAMATKAN.", "HUBUNGAN DIJAGA OLEH HAL KECIL.", HIT2[0][0], "GESER →")
    for i, (st, p1, p2) in enumerate(HIT2):
        poster(st, os.path.join(OUT, "karosel3", f"karosel-{i + 2:02d}.jpg"), "ANGKA KECIL.", f"ANGKA {i + 1:02d}.", p1, p2, counter=f"{i + 2:02d}/07")
    title_card(os.path.join(OUT, "karosel3", "karosel-07.jpg"), "ANGKA MANA", "YANG KAMU PAKAI?", "TULIS ANGKANYA DI KOMENTAR.", None, "SIMPAN, LALU KIRIM KE DIA YANG PERLU BACA.")
    print("ok")
