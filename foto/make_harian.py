"""Konten foto harian niche cinta (gaya make_foto_v2): A vs B, kirain-vs-ternyata, hitungan, perumpamaan benda + 2 karosel.
Pakai: python3 make_harian.py <folder-keluaran>   -> harian/, karosel2/, karosel3/"""
import importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
sys.argv = [sys.argv[0]]
spec = importlib.util.spec_from_file_location("fv", HERE + "/make_foto_v2.py"); fv = importlib.util.module_from_spec(spec); spec.loader.exec_module(fv)
F, T, rr, S, LIME, WHITE, GREY, RED = fv.F, fv.T, fv.rr, fv.S, fv.LIME, fv.WHITE, fv.GREY, fv.RED
DARK = (22, 30, 12)
LIGHTS = [(900, 140), (820, 200), (960, 120), (760, 160), (930, 220), (850, 100)]

AB = [  # (judul, A, B, penutup)
 ("DIA MULAI CUEK.", "Perasaanmu aja.", "Ceritain. Aku dengerin.", "Perasaan perlu didengar, bukan dibantah."),
 ("BERTENGKAR LARUT MALAM.", "Terserah. Aku pergi.", "Lanjut besok ya. Aku di sini.", "Marah boleh, pergi jangan."),
 ("SAAT BEDA PENDAPAT.", "Aku yang benar.", "Aku dengerin versimu dulu.", "Menang debat, kalah dekat."),
 ("CERITA MASA LALU.", "Gak penting.", "Aku dengerin, pelan-pelan.", "Jujur tidak harus sekaligus."),
 ("ULANG TAHUN TERLUPA.", "Kan aku sibuk.", "Maaf. Aku tebus ya.", "Lupa itu wajar, menebusnya pilihan."),
 ("SAAT PASANGAN SAKIT.", "Minum obat aja.", "Kubawain bubur ya.", "Peduli itu hadir."),
 ("SAAT DIPERCAYAI CERITA.", "Eh, tau gak dia cerita...", "Itu rahasiamu. Aman.", "Rahasia itu amanah."),
 ("SAAT NGAMBEK.", "Tebak sendiri.", "Aku kesal karena tadi.", "Perasaan itu diucapkan."),
 ("SOAL JANJI.", "Nanti pasti kutepati.", "Jam 8 aku telepon.", "Janji kecil yang ditepati."),
]
BAL = [  # (kirain, ternyata, pelajaran)
 ("Dia hanya balas “ok”.", "Dia sedang menemani ibunya di rumah sakit.", "Jangan menebak cerita orang."),
 ("Pasangan mendadak dingin.", "Dia kewalahan di kerjaan, bukan menjauh.", "Dingin tidak selalu berarti pergi."),
 ("Terlalu sempurna di awal.", "Itu pencitraan, bukan sifat aslinya.", "Konsisten lebih penting dari manis."),
 ("Aku yang selalu minta maaf.", "Aku yang selama ini dikendalikan.", "Minta maaf terus bukan tanda salah."),
 ("Ditolak itu akhir segalanya.", "Itu menyelamatkanku dari hubungan yang salah.", "Ditolak bisa jadi dilindungi."),
 ("“Kita perlu bicara.”", "Dia hanya ingin bilang terima kasih.", "Jangan langsung menebak yang terburuk."),
]
BAL2 = [
 ("Dia yang paling lucu di grup.", "Dia yang paling butuh didengar.", "Yang tertawa belum tentu baik-baik saja."),
 ("“Aku sibuk.”", "Dia memang menghindar.", "Sibuk bisa alasan, bisa pilihan."),
 ("Posesif karena sayang.", "Takut kehilangan kendali.", "Sayang tidak mengurung."),
 ("“Dia berubah.”", "Kamu baru melihat dia yang asli.", "Awal bisa menipu, pola tidak."),
 ("Mantan yang dibenci.", "Guru yang paling jujur.", "Yang pergi mengajarkan batasmu."),
]
HIT = [  # (angka, satuan, penjelasan, penutup)
 ("3", "KALI", "Dia lupa janji tiga kali berturut-turut.", "Satu kali manusia, tiga kali pola."),
 ("5", "DETIK", "Jeda sebelum membalas saat sedang marah.", "Lima detik menyelamatkan satu malam."),
 ("2", "MENIT", "Waktu yang cukup untuk memberi kabar.", "Dua menit menghemat dua hari curiga."),
 ("24", "JAM", "Aturan sebelum memutuskan untuk putus.", "Besok pagi lebih jernih."),
]
HIT2 = [
 ("10", "MENIT", "Setelah bertengkar, siapa yang mulai bicara menentukan malam itu.", "Sepuluh menit pertama menentukan."),
 ("20", "DETIK", "Peluk dulu, bicara kemudian.", "Peluk menenangkan sebelum kata-kata."),
 ("30", "HARI", "Tanpa menghubungi mantan. Coret kalendernya.", "Hari ke-30, kamu lebih ringan."),
 ("3", "KALIMAT", "Tolong. Maaf. Makasih.", "Tiga kata, setengah hubungan."),
 ("1", "TINDAKAN", "Lebih berat dari seratus kata manis.", "Lihat tindakannya."),
]
BEN = [  # (kiri, kanan, penjelasan, penutup)
 ("MAAF", "PERBAN", "Menutup luka, tapi luka tetap perlu diobati.", "Maaf tanpa obat tidak sembuh."),
 ("BATAS", "PAGAR", "Bukan tembok. Pagar punya pintu.", "Pagar menjaga, tembok memisahkan."),
 ("JANJI", "TABUNGAN", "Disetor sedikit-sedikit, tiap hari.", "Kepercayaan ditabung, bukan dipinjam."),
 ("PERHATIAN", "LILIN", "Dibagi makin terang. Dikurung, padam.", "Cahaya tumbuh saat dibagi."),
 ("LUKA LAMA", "KOPER", "Kamu masih menyeretnya ke mana-mana.", "Letakkan, bukan dikubur."),
 ("PERASAAN", "BATERAI", "Jangan dikuras sampai nol.", "Isi ulang dirimu dulu."),
]

def new(kind, seed, i=0, dx=0):
    bg = fv.photo_bg(kind, seed, LIGHTS[i % 6], dx); ov = fv.overlay(); return bg, ov, fv.ImageDraw.Draw(ov)
def bar(d, text, y=1150, size=29):
    rr(d, 70, y, 1010, y + 88, 22, fill=LIME); T(d, 100, y + 56, text, F(size, "Inter-Bold"), DARK)
def foot(d, left=None):
    if left: T(d, 70, 1300, left, F(26, "Inter-Medium"), GREY)
    T(d, 1010, 1300, fv.BRAND, F(28, "InterDisplay-Bold"), LIME, "rs")
def pill(d, x, y, text, w, filled=False):
    rr(d, x, y, x + w, y + 50, 25, fill=LIME if filled else (8, 10, 14, 170), out=LIME if filled else GREY, w=2)
    T(d, x + 28, y + 35, text, F(22, "InterDisplay-Black"), DARK if filled else GREY)
def counter(d, i, n): T(d, 1010, 106, f"{i:02d} / {n:02d}", F(26, "Inter-SemiBold"), GREY, "rs")

# ---------- A vs B ----------
def draw_ab(d, item, num=None):
    title, a, b, take = item
    f = F(84); lines = fv.wrap(d, title, f, 940)
    for k, l in enumerate(lines): T(d, 70, 640 - (len(lines) - 1 - k) * 92, l, f, LIME)
    for j, (lab, txt, col, tint) in enumerate((("PASANGAN A", a, RED, (60, 28, 32, 190)), ("PASANGAN B", b, LIME, (30, 52, 22, 190)))):
        y0 = 700 + j * 172
        rr(d, 70, y0, 1010, y0 + 150, 24, fill=tint, out=col, w=2); fv.flag(d, 100, y0 + 24, col, 0.55)
        T(d, 158, y0 + 42, lab, F(24, "InterDisplay-Black"), col); T(d, 100, y0 + 112, f"“{txt}”", F(42, "Inter-SemiBold"), WHITE)
    bar(d, take, 1062); fv.dots(d, 905, 1186, n=5)
def ab_single(i, path):
    bg, ov, d = new(1 if i % 2 == 0 else 2, 100 + i, i, (-30, 20, -10, 30, 0, 15)[i % 6])
    pill(d, 70, 70, "A VS B", 170, True); draw_ab(d, AB[i]); foot(d, "Kamu yang mana? A atau B."); fv.finish(bg, ov, path)

# ---------- kirain vs ternyata ----------
def draw_bal(d, item, note=True):
    kir, ter, les = item; y = 470
    pill(d, 70, y, "KIRAIN", 170); y += 100
    lines = fv.wrap(d, kir, F(58), 940)
    for l in lines: T(d, 70, y, l, F(58), WHITE); y += 68
    y += 34; pill(d, 70, y, "TERNYATA", 210, True); y += 100
    for l in fv.wrap(d, ter, F(58), 940): T(d, 70, y, l, F(58), LIME); y += 68
    bar(d, les); 
    if note: T(d, 1010, 1130, "contoh ilustrasi", F(20, "Inter-Medium"), GREY, "rs")
def bal_single(i, path):
    bg, ov, d = new(2 if i % 2 == 0 else 1, 200 + i, i, (10, -20, 25, 0, -15, 30)[i % 6])
    fv.chrome(ov, d, "KIRAIN · TERNYATA · KIRAIN · TERNYATA · "); draw_bal(d, BAL[i]); fv.dots(d, 905, 1056, n=4); fv.finish(bg, ov, path)

# ---------- hitungan ----------
def draw_hit(d, item):
    num, unit, expl, take = item
    T(d, 70, 700, num, F(300), LIME); T(d, 70, 810, unit, F(min(104, int(930 / (len(unit) * 0.64)))), WHITE)
    for k, l in enumerate(fv.wrap(d, expl, F(40, "Inter-SemiBold"), 900)): T(d, 70, 900 + k * 54, l, F(40, "Inter-SemiBold"), GREY)
    bar(d, take)
def hit_single(i, path):
    bg, ov, d = new(1 if i % 2 == 0 else 2, 300 + i, i, (0, 25, -20, 10)[i % 4])
    fv.chrome(ov, d, "ANGKA KECIL · HUBUNGAN SEHAT · ANGKA KECIL · HUBUNGAN SEHAT · "); draw_hit(d, HIT[i]); fv.dots(d, 905, 1056, n=4); fv.finish(bg, ov, path)

# ---------- perumpamaan benda ----------
def draw_ben(d, item):
    kiri, kanan, expl, take = item
    sz = min(112, int(930 / (max(len(kiri), len(kanan) + 2) * 0.64)))
    T(d, 70, 600, kiri, F(sz), WHITE); T(d, 70, 600 + sz + 8, "= " + kanan, F(sz), LIME)
    d.rectangle([70 * S, (600 + sz + 36) * S, 330 * S, (600 + sz + 43) * S], fill=LIME)
    for k, l in enumerate(fv.wrap(d, expl, F(40, "Inter-SemiBold"), 900)): T(d, 70, 600 + sz + 110 + k * 54, l, F(40, "Inter-SemiBold"), GREY)
    bar(d, take)
def ben_single(i, path):
    bg, ov, d = new(2 if i % 2 == 0 else 1, 400 + i, i, (-20, 15, 0, 30, -10, 20)[i % 6])
    fv.chrome(ov, d, "PERUMPAMAAN · CERITA CINTA · PERUMPAMAAN · CERITA CINTA · "); draw_ben(d, BEN[i]); fv.dots(d, 905, 1056, n=4); fv.finish(bg, ov, path)

# ---------- karosel ----------
def car_cover(path, l1, l2, l3, sub, label):
    bg, ov, d = new(1, 500 + len(l1)); fv.chrome(ov, d, label)
    T(d, 70, 560, l1, F(104), WHITE); T(d, 70, 668, l2, F(104), WHITE); T(d, 70, 776, l3, F(104), LIME)
    d.rectangle([70 * S, 800 * S, 330 * S, 807 * S], fill=LIME)
    T(d, 70, 880, sub, F(36, "Inter-SemiBold"), WHITE)
    rr(d, 70, 1170, 400, 1256, 22, fill=LIME); T(d, 100, 1222, "GESER  →", F(30, "Inter-Bold"), DARK); fv.dots(d, 880, 1130); fv.finish(bg, ov, path)
def car_close(path, l1, l2, sub, cta1, cta2):
    bg, ov, d = new(2, 600 + len(l1)); fv.chrome(ov, d, "SIMPAN · KIRIM · SIMPAN · KIRIM · SIMPAN · KIRIM · ")
    sz = min(100, int(960 / (max(len(l1), len(l2)) * 0.66)))
    T(d, 70, 560, l1, F(sz), WHITE); T(d, 70, 664, l2, F(sz), LIME); d.rectangle([70 * S, 690 * S, 330 * S, 697 * S], fill=LIME)
    T(d, 70, 780, sub, F(38, "Inter-SemiBold"), WHITE)
    rr(d, 70, 1150, 800, 1256, 22, fill=LIME); T(d, 100, 1196, cta1, F(28, "Inter-Bold"), DARK); T(d, 100, 1236, cta2, F(28, "Inter-Bold"), DARK)
    fv.dots(d, 880, 1110); fv.finish(bg, ov, path)
def car_slide(path, i, n, label, drawer, item, seed):
    bg, ov, d = new(1 if i % 2 == 0 else 2, seed + i, i, (-30, 20, -10, 30, 0, 15)[i % 6])
    pill(d, 70, 70, label, 230, True); counter(d, i + 2, n); drawer(d, item); foot(d, "geser →"); fv.finish(bg, ov, path)

if __name__ == "__main__":
    for sub in ("harian", "karosel2", "karosel3"): os.makedirs(f"{OUT}/{sub}", exist_ok=True)
    for i in range(len(AB)): ab_single(i, f"{OUT}/harian/ab-{i + 1:02d}.jpg")
    for i in range(len(BAL)): bal_single(i, f"{OUT}/harian/bal-{i + 1:02d}.jpg")
    for i in range(len(HIT)): hit_single(i, f"{OUT}/harian/hit-{i + 1:02d}.jpg")
    for i in range(len(BEN)): ben_single(i, f"{OUT}/harian/ben-{i + 1:02d}.jpg")
    # karosel 2: kirain vs ternyata (cover + 5 + penutup)
    car_cover(f"{OUT}/karosel2/karosel-01.jpg", "KIRAIN", "VS", "TERNYATA.", "5 cerita yang sering salah kita kira", "KIRAIN · TERNYATA · KIRAIN · TERNYATA · ")
    for i, it in enumerate(BAL2): car_slide(f"{OUT}/karosel2/karosel-{i + 2:02d}.jpg", i, 7, f"CERITA {i + 1:02d}", draw_bal, it, 700)
    car_close(f"{OUT}/karosel2/karosel-07.jpg", "PERNAH", "SALAH KIRA?", "Ceritain di komentar.", "Simpan buat pengingat,", "lalu kirim ke dia yang perlu baca.")
    # karosel 3: angka kecil
    car_cover(f"{OUT}/karosel3/karosel-01.jpg", "5 ANGKA", "KECIL YANG", "MENYELAMATKAN.", "Hubungan kadang dijaga oleh hal kecil", "ANGKA KECIL · HUBUNGAN SEHAT · ANGKA KECIL · HUBUNGAN SEHAT · ")
    for i, it in enumerate(HIT2): car_slide(f"{OUT}/karosel3/karosel-{i + 2:02d}.jpg", i, 7, f"ANGKA {i + 1:02d}", draw_hit, it, 800)
    car_close(f"{OUT}/karosel3/karosel-07.jpg", "ANGKA MANA", "YANG KAMU PAKAI?", "Tulis angkanya di komentar.", "Simpan buat pengingat,", "lalu kirim ke dia yang perlu baca.")
    print("ok")
