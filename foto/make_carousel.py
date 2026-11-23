"""Karosel 8 slide 1080x1350: 'Sama masalah, beda cara' (6 situasi Pasangan A vs B). Gaya sama dengan make_foto_v2.py.
Pakai: python3 make_carousel.py <folder-keluaran>"""
import importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
sys.argv = [sys.argv[0]]
spec = importlib.util.spec_from_file_location("fv", HERE + "/make_foto_v2.py"); fv = importlib.util.module_from_spec(spec); spec.loader.exec_module(fv)
F, T, rr, W, H, S, LIME, WHITE, GREY, RED = fv.F, fv.T, fv.rr, fv.W, fv.H, fv.S, fv.LIME, fv.WHITE, fv.GREY, fv.RED
DARK = (22, 30, 12)
N = 8
SITUASI = [
 ("CHAT BELUM DIBALAS.", "Aku kan sibuk.", "Maaf, aku bales sekarang.", "Kabar kecil, rasa aman besar."),
 ("SAAT CEMBURU DATANG.", "Kamu berlebihan.", "Makasih udah jujur.", "Cemburu dibicarakan, bukan diselidiki."),
 ("TELAT JEMPUT.", "Gitu aja marah.", "Maaf, harusnya kukabari.", "Maaf yang tulus menyebut kesalahannya."),
 ("SAAT DIKRITIK.", "Kamu terlalu sensitif.", "Aku mau perbaiki ya.", "Kritik didengar, bukan dibalas serangan."),
 ("MINTA RUANG.", "Terserah.", "Seru-seruan, kabarin ya.", "Memberi ruang bukan membiarkan."),
 ("PASANGAN CAPEK.", "Aku juga capek!", "Sini, aku temani.", "Capek tidak jadi alasan menyakiti."),
]
LIGHTS = [(900, 140), (820, 200), (960, 120), (760, 160), (930, 220), (850, 100)]

def cover(path):
    bg = fv.photo_bg(1, 31); ov = fv.overlay(); d = fv.ImageDraw.Draw(ov)
    fv.chrome(ov, d, "PASANGAN A · PASANGAN B · PASANGAN A · PASANGAN B · ")
    T(d, 70, 560, "SAMA", F(110), WHITE); T(d, 70, 672, "MASALAH.", F(110), WHITE); T(d, 70, 784, "BEDA CARA.", F(110), LIME)
    d.rectangle([70 * S, 810 * S, 330 * S, 817 * S], fill=LIME)
    T(d, 70, 880, "6 situasi pasangan A vs B", F(36, "Inter-SemiBold"), WHITE)
    T(d, 70, 930, "Kamu yang mana?", F(36, "Inter-Medium"), GREY)
    rr(d, 70, 1170, 400, 1256, 22, fill=LIME); T(d, 100, 1222, "GESER  →", F(30, "Inter-Bold"), DARK)
    fv.dots(d, 880, 1130); fv.finish(bg, ov, path)

def situasi(i, path):
    title, a, b, take = SITUASI[i]
    bg = fv.photo_bg(1 if i % 2 == 0 else 2, 40 + i, LIGHTS[i], dx=(-30, 20, -10, 30, 0, 15)[i]); ov = fv.overlay(); d = fv.ImageDraw.Draw(ov)
    rr(d, 70, 70, 70 + 230, 70 + 54, 27, fill=(8, 10, 14, 170), out=LIME, w=2); T(d, 100, 106, "SITUASI " + f"{i + 1:02d}", F(24, "InterDisplay-Black"), LIME)
    T(d, 1010, 106, f"{i + 2:02d} / {N:02d}", F(26, "Inter-SemiBold"), GREY, "rs")
    f = F(84); lines = fv.wrap(d, title, f, 940)
    for k, l in enumerate(lines): T(d, 70, 640 - (len(lines) - 1 - k) * 92, l, f, LIME)
    for j, (lab, txt, col, tint) in enumerate((("PASANGAN A", a, RED, (60, 28, 32, 190)), ("PASANGAN B", b, LIME, (30, 52, 22, 190)))):
        y0 = 700 + j * 172
        rr(d, 70, y0, 1010, y0 + 150, 24, fill=tint, out=col, w=2)
        fv.flag(d, 100, y0 + 24, col, 0.55); T(d, 158, y0 + 42, lab, F(24, "InterDisplay-Black"), col)
        T(d, 100, y0 + 112, f"“{txt}”", F(42, "Inter-SemiBold"), WHITE)
    rr(d, 70, 1062, 1010, 1148, 22, fill=LIME); T(d, 100, 1114, take, F(29, "Inter-Bold"), DARK)
    T(d, 70, 1300, "geser →", F(26, "Inter-Medium"), GREY); fv.dots(d, 905, 1186, n=5)
    T(d, 1010, 1300, fv.BRAND, F(28, "InterDisplay-Bold"), LIME, "rs")
    fv.finish(bg, ov, path)

def closing(path):
    bg = fv.photo_bg(2, 77); ov = fv.overlay(); d = fv.ImageDraw.Draw(ov)
    fv.chrome(ov, d, "KAMU YANG MANA · A ATAU B · KAMU YANG MANA · A ATAU B · ")
    T(d, 70, 560, "KAMU YANG", F(104), WHITE); T(d, 70, 668, "MANA?", F(104), LIME)
    d.rectangle([70 * S, 692 * S, 330 * S, 699 * S], fill=LIME)
    T(d, 70, 780, "Tulis A atau B di komentar.", F(38, "Inter-SemiBold"), WHITE)
    T(d, 70, 836, "Sama masalahnya. Beda cara menanggapinya.", F(30, "Inter-Medium"), GREY)
    rr(d, 70, 1150, 800, 1256, 22, fill=LIME)
    T(d, 100, 1196, "Simpan buat pengingat,", F(28, "Inter-Bold"), DARK); T(d, 100, 1236, "lalu kirim ke dia yang perlu baca.", F(28, "Inter-Bold"), DARK)
    fv.dots(d, 880, 1110); fv.finish(bg, ov, path)

if __name__ == "__main__":
    os.makedirs(OUTDIR, exist_ok=True)
    cover(f"{OUTDIR}/karosel-01.jpg")
    for i in range(6): situasi(i, f"{OUTDIR}/karosel-{i + 2:02d}.jpg")
    closing(f"{OUTDIR}/karosel-08.jpg"); print("ok")
