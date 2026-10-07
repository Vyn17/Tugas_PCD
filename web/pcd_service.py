"""
Layanan Render PCD
------------------
Menjembatani Rumus Kanonik di pcd_operations.py dengan tampilan web.

Tanggung jawab:
1. Menurunkan skala citra untuk tampilan (mencatatnya sebagai Koreksi Senyap).
2. Memanggil Operasi PCD sesuai Kelompok yang diminta.
3. Mengubah citra hasil menjadi PNG in-memory (cv2.imencode), bukan savefig.
4. Mengembalikan data histogram mentah untuk digambar di peramban.

Berkas ini tidak mendefinisikan rumus apa pun. Seluruh perhitungan berasal dari
pcd_operations.py.
"""

import base64
import math
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import cv2
import numpy as np

from main import MAX_DISPLAY_SIDE, bgr2rgb
from pcd_operations import (
    adaptive_thresholding,
    brightening,
    citra_negatif,
    ekualisasi_histogram,
    flipping,
    gamma_correction,
    hitung_histogram,
    manual_thresholding,
    match_dimensions,
    operasi_aritmetika,
    otsu_thresholding,
    rgb_to_grayscale,
    rotasi,
    translasi,
    zooming,
)

# Urutan kanonik tujuh Kelompok.
KELOMPOK_URUTAN = [
    "negatif",
    "grayscale",
    "brightening",
    "aritmetika",
    "geometri",
    "histogram",
    "thresholding",
]

LABEL_KELOMPOK = {
    "negatif": "1. Citra Negatif",
    "grayscale": "2. Grayscale",
    "brightening": "3. Brightening",
    "aritmetika": "4. Aritmetika Dua Citra",
    "geometri": "5. Operasi Geometri",
    "histogram": "6. Histogram & Ekualisasi",
    "thresholding": "7. Thresholding",
}

METODE_GRAYSCALE = ["luminosity", "average", "lightness", "opencv"]
MODE_THRESHOLD = ["binary", "binary_inv", "trunc", "tozero", "tozero_inv"]
MODE_FLIP = ["horizontal", "vertikal", "keduanya"]
OPERASI_ARITMETIKA = ["penjumlahan", "pengurangan", "perkalian", "pembagian"]


# ==============================================================================
# KOREKSI SENYAP
# ==============================================================================
class KoreksiSenyap:
    """Mencatat setiap perubahan yang dilakukan kode terhadap masukan pengguna."""

    def __init__(self):
        self._catatan: list[dict] = []

    def tambah(self, jenis: str, pesan: str, kelompok: str | None = None):
        self._catatan.append({"jenis": jenis, "pesan": pesan, "kelompok": kelompok})

    def daftar(self) -> list[dict]:
        return list(self._catatan)

    def ringkasan(self) -> str | None:
        if not self._catatan:
            return None
        return " ".join(c["pesan"] for c in self._catatan)

    def untuk_kelompok(self, kelompok: str) -> list[str]:
        return [c["pesan"] for c in self._catatan if c["kelompok"] == kelompok]


# ==============================================================================
# ENCODING
# ==============================================================================
def _png_bytes(img: np.ndarray) -> bytes:
    """Mengubah array NumPy (BGR atau grayscale) menjadi byte PNG."""
    sukses, buffer = cv2.imencode(".png", img)
    if not sukses:
        raise RuntimeError("Gagal mengubah citra menjadi PNG.")
    return buffer.tobytes()


def _data_uri(img: np.ndarray) -> str:
    """Mengubah citra menjadi data URI PNG agar dapat langsung dipakai di HTML."""
    return "data:image/png;base64," + base64.b64encode(_png_bytes(img)).decode("ascii")


def _untuk_tampilan(img: np.ndarray) -> np.ndarray:
    """Konversi BGR ke RGB hanya untuk keperluan penyandian warna di peramban."""
    return bgr2rgb(img)


def downscale(img: np.ndarray, koreksi: KoreksiSenyap, label: str) -> np.ndarray:
    """
    Menurunkan skala citra agar sisi terpanjangnya tidak melebihi MAX_DISPLAY_SIDE.

    Ini adalah Koreksi Senyap: perubahan ukuran dicatat agar dapat dilaporkan.
    """
    if img is None:
        return img

    h, w = img.shape[:2]
    sisi_terpanjang = max(h, w)

    if sisi_terpanjang <= MAX_DISPLAY_SIDE:
        return img

    skala = MAX_DISPLAY_SIDE / float(sisi_terpanjang)
    lebar_baru = max(1, int(round(w * skala)))
    tinggi_baru = max(1, int(round(h * skala)))

    hasil = cv2.resize(img, (lebar_baru, tinggi_baru), interpolation=cv2.INTER_AREA)
    koreksi.tambah(
        "penurunan_skala",
        f"{label} diturunkan skalanya dari {w}x{h} menjadi {lebar_baru}x{tinggi_baru} "
        f"(batas {MAX_DISPLAY_SIDE}px).",
    )
    return hasil


def _panel(judul: str, img: np.ndarray, catatan: str | None = None) -> dict:
    """Membentuk satu panel keluaran berisi data URI PNG dan judulnya."""
    return {
        "judul": judul,
        "gambar": _data_uri(_untuk_tampilan(img)),
        "catatan": catatan,
        "tipe": "gambar",
    }


def _histogram_payload(hist) -> dict:
    """Menyiapkan data histogram agar mudah digambar oleh peramban."""
    if isinstance(hist, dict):
        return {
            "tipe": "rgb",
            "r": [float(v) for v in hist["r"]],
            "g": [float(v) for v in hist["g"]],
            "b": [float(v) for v in hist["b"]],
        }
    return {"tipe": "tunggal", "nilai": [float(v) for v in hist]}


# ==============================================================================
# RENDER PER KELOMPOK
# ==============================================================================
def _render_negatif(img: np.ndarray, prm: dict, koreksi: KoreksiSenyap) -> dict:
    gray = rgb_to_grayscale(img, method="luminosity")

    return {
        "kelompok": "negatif",
        "judul": LABEL_KELOMPOK["negatif"],
        "rumus": "s = (L - 1) - r = 255 - r",
        "panel": [
            _panel("Citra Asli (Berwarna)", img),
            _panel("Negatif Berwarna", citra_negatif(img)),
            _panel("Citra Asli (Grayscale)", gray),
            _panel("Negatif Grayscale", citra_negatif(gray)),
        ],
    }


def _render_grayscale(img: np.ndarray, prm: dict, koreksi: KoreksiSenyap) -> dict:
    dipilih = prm.get("metode_grayscale", METODE_GRAYSCALE)
    if isinstance(dipilih, str):
        dipilih = [dipilih]
    dipilih = [m for m in dipilih if m in METODE_GRAYSCALE] or ["luminosity"]

    keterangan = {
        "luminosity": "Y = 0.299R + 0.587G + 0.114B",
        "average": "Y = (R + G + B) / 3",
        "lightness": "Y = (max(R,G,B) + min(R,G,B)) / 2",
        "opencv": "cv2.cvtColor(COLOR_BGR2GRAY)",
    }

    panel = [_panel("Citra Asli (RGB)", img)]
    for metode in dipilih:
        gray = rgb_to_grayscale(img, method=metode)
        panel.append(_panel(f"{metode.capitalize()} — {keterangan[metode]}", gray))

    return {
        "kelompok": "grayscale",
        "judul": LABEL_KELOMPOK["grayscale"],
        "rumus": "Y = 0.299R + 0.587G + 0.114B",
        "panel": panel,
        "metode_dirender": dipilih,
    }


def _render_brightening(img: np.ndarray, prm: dict, koreksi: KoreksiSenyap) -> dict:
    beta = int(prm.get("beta", 50))
    alpha = float(prm.get("alpha", 1.0))
    gamma = float(prm.get("gamma", 1.5))

    return {
        "kelompok": "brightening",
        "judul": LABEL_KELOMPOK["brightening"],
        "rumus": "g = alpha * f + beta   dan   s = c * (r / 255) ^ (1 / gamma) * 255",
        "panel": [
            _panel("Citra Asli", img),
            _panel(f"Linier (g = {alpha:.2f}*f + {beta})", brightening(img, beta=beta, alpha=alpha)),
            _panel(f"Gamma Correction (gamma = {gamma:.2f})", gamma_correction(img, gamma=gamma)),
        ],
        "nilai": {"beta": beta, "alpha": alpha, "gamma": gamma},
    }


def _render_aritmetika(img: np.ndarray, img2: np.ndarray, prm: dict, koreksi: KoreksiSenyap) -> dict:
    if img2 is None:
        raise ValueError(
            "Kelompok Aritmetika memerlukan citra kedua. Pilih Citra 2 terlebih dahulu."
        )

    weight1 = float(prm.get("weight1", 0.5))
    weight2 = float(prm.get("weight2", 0.5))

    # match_dimensions dipanggil sekali; hasilnya dipakai ulang untuk semua operasi
    # agar tidak terjadi pengulangan penyesuaian ukuran yang sia-sia.
    if img.shape[:2] != img2.shape[:2]:
        h1, w1 = img.shape[:2]
        h2, w2 = img2.shape[:2]
        koreksi.tambah(
            "penyesuaian_dimensi",
            f"Citra 2 disejajarkan dari {w2}x{h2} menjadi {w1}x{h1} agar dapat dioperasikan "
            f"per-piksel dengan Citra 1.",
            "aritmetika",
        )

    im1, im2 = match_dimensions(img.copy(), img2.copy())

    # Sub-panel 1: empat operasi dasar tanpa slider.
    panel_dasar = [_panel("Citra 1 (f1)", im1), _panel("Citra 2 (f2)", im2)]
    label_dasar = {
        "penjumlahan": "Penjumlahan (f1 + f2)",
        "pengurangan": "Pengurangan (|f1 - f2|)",
        "perkalian": "Perkalian ((f1 * f2) / 255)",
        "pembagian": "Pembagian ((f1 / (f2 + 1)) * 255)",
    }
    for operasi in OPERASI_ARITMETIKA:
        panel_dasar.append(
            _panel(label_dasar[operasi], operasi_aritmetika(im1, im2, operasi=operasi))
        )

    # Sub-panel 2: blending, satu-satunya yang dipengaruhi slider bobot.
    panel_blending = [
        _panel("Citra 1 (f1)", im1),
        _panel("Citra 2 (f2)", im2),
        _panel(
            f"Blending ({weight1:.2f}*f1 + {weight2:.2f}*f2)",
            operasi_aritmetika(im1, im2, operasi="blending", weight1=weight1, weight2=weight2),
        ),
    ]

    return {
        "kelompok": "aritmetika",
        "judul": LABEL_KELOMPOK["aritmetika"],
        "rumus": "g = clip(w1 * f1 + w2 * f2, 0, 255)",
        "sub_kelompok": [
            {
                "judul": "Operasi Dasar",
                "keterangan": "Tidak dipengaruhi slider bobot.",
                "panel": panel_dasar,
            },
            {
                "judul": "Blending Berbobot",
                "keterangan": "Slider bobot hanya berlaku pada blok ini.",
                "panel": panel_blending,
            },
        ],
        "nilai": {"weight1": weight1, "weight2": weight2},
    }


def _render_geometri(img: np.ndarray, prm: dict, koreksi: KoreksiSenyap) -> dict:
    tx = int(prm.get("tx", 50))
    ty = int(prm.get("ty", 30))
    sudut = float(prm.get("sudut", 45.0))
    skala = float(prm.get("skala", 1.0))
    mode_flip = prm.get("mode_flip", "horizontal")
    if mode_flip not in MODE_FLIP:
        mode_flip = "horizontal"
    faktor_zoom = float(prm.get("faktor_zoom", 1.5))
    jaga_ukuran = bool(prm.get("jaga_ukuran", True))

    h, w = img.shape[:2]
    catatan_translasi = None
    if tx < 0 or ty < 0 or tx > w or ty > h:
        catatan_translasi = (
            f"Translasi ({tx}, {ty}) melampaui batas citra {w}x{h} sehingga sebagian "
            f"citra keluar dari kanvas."
        )

    catatan_zoom = None
    if not jaga_ukuran and faktor_zoom != 1.0:
        lebar_baru = max(1, int(w * faktor_zoom))
        tinggi_baru = max(1, int(h * faktor_zoom))
        catatan_zoom = f"Zoom mengubah ukuran keluaran menjadi {lebar_baru}x{tinggi_baru}."

    return {
        "kelompok": "geometri",
        "judul": LABEL_KELOMPOK["geometri"],
        "rumus": "T = [[1, 0, tx], [0, 1, ty]]   dan   M = getRotationMatrix2D(center, sudut, skala)",
        "panel": [
            _panel("Citra Asli", img),
            _panel(f"Translasi (tx={tx}, ty={ty})", translasi(img, tx=tx, ty=ty), catatan_translasi),
            _panel(f"Rotasi ({sudut:.1f} derajat, skala={skala:.2f})", rotasi(img, angle=sudut, scale=skala)),
            _panel(f"Flipping ({mode_flip})", flipping(img, mode=mode_flip)),
            _panel(
                f"Zooming ({faktor_zoom:.2f}x, {'ukuran dijaga' if jaga_ukuran else 'ukuran berubah'})",
                zooming(img, factor=faktor_zoom, maintain_size=jaga_ukuran),
                catatan_zoom,
            ),
        ],
        "nilai": {
            "tx": tx,
            "ty": ty,
            "sudut": sudut,
            "skala": skala,
            "mode_flip": mode_flip,
            "faktor_zoom": faktor_zoom,
            "jaga_ukuran": jaga_ukuran,
        },
    }


def _render_histogram(img: np.ndarray, prm: dict, koreksi: KoreksiSenyap) -> dict:
    metode = prm.get("metode_grayscale", "luminosity")
    if isinstance(metode, list):
        metode = metode[0] if metode else "luminosity"
    if metode not in METODE_GRAYSCALE:
        metode = "luminosity"

    gray = rgb_to_grayscale(img, method=metode)
    gray_eq = ekualisasi_histogram(gray)

    return {
        "kelompok": "histogram",
        "judul": LABEL_KELOMPOK["histogram"],
        "rumus": "h(rk) = nk   dan   sk = round((CDF(rk) - CDFmin) / (M*N - CDFmin) * (L - 1))",
        "panel": [
            _panel(f"Grayscale ({metode})", gray),
            _panel("Hasil Ekualisasi Histogram", gray_eq),
            _panel("Citra Berwarna (RGB)", img),
        ],
        "histogram": {
            "grayscale_asli": _histogram_payload(hitung_histogram(gray)),
            "grayscale_ekualisasi": _histogram_payload(hitung_histogram(gray_eq)),
            "rgb": _histogram_payload(hitung_histogram(img)),
        },
        "metode_grayscale": metode,
    }


def _render_thresholding(img: np.ndarray, prm: dict, koreksi: KoreksiSenyap) -> dict:
    threshold = int(prm.get("threshold", 127))
    max_val = int(prm.get("max_val", 255))
    mode = prm.get("mode_threshold", "binary")
    if mode not in MODE_THRESHOLD:
        mode = "binary"
    metode_adaptif = prm.get("metode_adaptif", "mean")
    if metode_adaptif not in ("mean", "gaussian"):
        metode_adaptif = "mean"
    block_size = int(prm.get("block_size", 15))
    c = int(prm.get("c", 3))

    thresh_diminta = block_size
    if block_size % 2 == 0:
        block_size += 1
        koreksi.tambah(
            "pembulatan_block_size",
            f"block_size {thresh_diminta} dibulatkan menjadi {block_size} karena harus bernilai ganjil.",
            "thresholding",
        )
    if block_size < 3:
        block_size = 3

    gray = rgb_to_grayscale(img, method="luminosity")
    thresh_otsu, optimal_t = otsu_thresholding(gray)

    return {
        "kelompok": "thresholding",
        "judul": LABEL_KELOMPOK["thresholding"],
        "rumus": "g(x, y) = max_val jika f(x, y) > T, selain itu 0",
        "panel": [
            _panel("Grayscale Input", gray),
            _panel(f"Manual ({mode}, T = {threshold})", manual_thresholding(gray, threshold=threshold, max_val=max_val, mode=mode)),
            _panel(f"Otsu (T* = {optimal_t:.1f})", thresh_otsu),
            _panel(
                f"Adaptive {metode_adaptif.capitalize()} (block {block_size}, C={c})",
                adaptive_thresholding(gray, max_val=max_val, method=metode_adaptif, block_size=block_size, c=c),
            ),
        ],
        "nilai": {
            "threshold": threshold,
            "max_val": max_val,
            "mode_threshold": mode,
            "metode_adaptif": metode_adaptif,
            "block_size": block_size,
            "block_size_diminta": thresh_diminta,
            "c": c,
            "otsu_optimal": float(optimal_t),
        },
    }


# ==============================================================================
# TITIK MASUK
# ==============================================================================
def render_kelompok(
    kelompok: str,
    img: np.ndarray,
    img2: np.ndarray | None,
    prm: dict,
    koreksi: KoreksiSenyap,
) -> dict:
    """Merender satu Kelompok berdasarkan namanya."""
    if kelompok == "negatif":
        return _render_negatif(img, prm, koreksi)
    if kelompok == "grayscale":
        return _render_grayscale(img, prm, koreksi)
    if kelompok == "brightening":
        return _render_brightening(img, prm, koreksi)
    if kelompok == "aritmetika":
        return _render_aritmetika(img, img2, prm, koreksi)
    if kelompok == "geometri":
        return _render_geometri(img, prm, koreksi)
    if kelompok == "histogram":
        return _render_histogram(img, prm, koreksi)
    if kelompok == "thresholding":
        return _render_thresholding(img, prm, koreksi)
    raise ValueError(f"Kelompok '{kelompok}' tidak dikenali.")


def proses(
    img: np.ndarray,
    img2: np.ndarray | None,
    prm: dict,
    kelompok_diminta: list[str] | None = None,
) -> dict:
    """
    Memproses citra untuk sekumpulan Kelompok.

    Mengembalikan dict berisi label, ukuran, daftar kelompok hasil, dan
    seluruh Koreksi Senyap yang terjadi.
    """
    koreksi = KoreksiSenyap()

    img = downscale(img, koreksi, "Citra 1")
    if img2 is not None:
        img2 = downscale(img2, koreksi, "Citra 2")

    if kelompok_diminta:
        tidak_dikenal = [k for k in kelompok_diminta if k not in KELOMPOK_URUTAN]
        if tidak_dikenal:
            raise ValueError(
                f"Kelompok {tidak_dikenal} tidak dikenali. Pilihan: {KELOMPOK_URUTAN}"
            )
        dipilih = [k for k in KELOMPOK_URUTAN if k in kelompok_diminta]
    else:
        dipilih = list(KELOMPOK_URUTAN)

    hasil = []
    for kelompok in dipilih:
        try:
            blok = render_kelompok(kelompok, img, img2, prm, koreksi)
            blok["galat"] = None
        except ValueError as exc:
            blok = {
                "kelompok": kelompok,
                "judul": LABEL_KELOMPOK[kelompok],
                "panel": [],
                "galat": str(exc),
            }
        # Sertakan catatan teknis milik kelompok ini.
        blok["catatan_teknis"] = koreksi.untuk_kelompok(kelompok)
        hasil.append(blok)

    h, w = img.shape[:2]
    return {
        "ukuran_citra1": {"width": w, "height": h},
        "ukuran_citra2": (
            {"width": img2.shape[1], "height": img2.shape[0]} if img2 is not None else None
        ),
        "kelompok": hasil,
        "koreksi_senyap": koreksi.daftar(),
        "ringkasan_koreksi": koreksi.ringkasan(),
        "kelompok_tersedia": KELOMPOK_URUTAN,
    }
