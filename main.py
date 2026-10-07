"""
Pemuatan Citra dan Utilitas Bersama
-----------------------------------
Berkas ini menyediakan jalur dataset, konversi warna untuk matplotlib, dan
pemuat citra sampel. Logika Operasi PCD berada di pcd_operations.py.

Poster ringkasan (8 berkas PNG) dihasilkan oleh scripts/generate_poster.py.
Tampilan web berada di web/.
"""

import os
import glob
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Ukuran sisi terpanjang citra setelah penurunan skala untuk tampilan web.
MAX_DISPLAY_SIDE = 720


def bgr2rgb(img: np.ndarray) -> np.ndarray:
    """Konversi format BGR OpenCV ke RGB untuk matplotlib."""
    if len(img.shape) == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def ensure_output_dir():
    """Membuat direktori output jika belum ada."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_sample_images():
    """Mengambil 2 citra sampel dari dataset."""
    cat_path = os.path.join(DATASET_DIR, "cat", "cat_1.jpg")
    dog_path = os.path.join(DATASET_DIR, "dog", "dog_1.jpg")

    if not os.path.exists(cat_path):
        # Fallback cari file pertama yang ditemukan
        all_imgs = glob.glob(os.path.join(DATASET_DIR, "*", "*.jpg"))
        if len(all_imgs) >= 2:
            cat_path, dog_path = all_imgs[0], all_imgs[1]
        elif len(all_imgs) == 1:
            cat_path = dog_path = all_imgs[0]
        else:
            raise FileNotFoundError("Tidak ditemukan citra dalam folder dataset/")

    img1 = cv2.imread(cat_path)
    img2 = cv2.imread(dog_path)

    print(f"[INFO] Citra 1 dimuat: {os.path.basename(cat_path)} (Ukuran: {img1.shape})")
    print(f"[INFO] Citra 2 dimuat: {os.path.basename(dog_path)} (Ukuran: {img2.shape})")
    return img1, img2


def list_dataset() -> dict[str, list[dict]]:
    """
    Memetakan kategori dataset ke daftar citra yang tersedia.

    'posisi' adalah urutan berkas di dalam kategori (1-based), bukan nomor pada
    nama berkas. Berkas diurutkan secara leksikografis, sehingga fox_10.jpg
    berada di posisi 2 sementara fox_2.jpg berada di posisi 3.

    Mengembalikan dict: {kategori: [{'posisi': int, 'filename': str,
                                     'width': int, 'height': int}, ...]}
    """
    hasil: dict[str, list[dict]] = {}

    if not os.path.isdir(DATASET_DIR):
        return hasil

    for kategori in sorted(os.listdir(DATASET_DIR)):
        folder = os.path.join(DATASET_DIR, kategori)
        if not os.path.isdir(folder) or kategori.startswith("."):
            continue

        berkas = sorted(
            f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))
        )
        daftar = []
        for posisi, nama in enumerate(berkas, start=1):
            img = cv2.imread(os.path.join(folder, nama))
            if img is None:
                continue
            h, w = img.shape[:2]
            daftar.append({"posisi": posisi, "filename": nama, "width": w, "height": h})

        if daftar:
            hasil[kategori] = daftar

    return hasil


def load_dataset_image(kategori: str, posisi: int) -> tuple[np.ndarray, str]:
    """
    Memuat citra dari dataset berdasarkan kategori dan posisi berkas (1-based).

    'posisi' mengacu pada urutan leksikografis berkas di dalam kategori, bukan
    nomor pada nama berkas. Mengembalikan (citra BGR, nama berkas).
    """
    if not kategori or os.path.basename(kategori) != kategori:
        raise ValueError(f"Kategori '{kategori}' tidak valid.")

    folder = os.path.join(DATASET_DIR, kategori)
    if not os.path.isdir(folder):
        raise ValueError(f"Kategori '{kategori}' tidak ditemukan di dataset.")

    berkas = sorted(
        f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))
    )
    if not berkas:
        raise ValueError(f"Kategori '{kategori}' tidak memuat citra.")

    if not 1 <= posisi <= len(berkas):
        raise ValueError(
            f"Posisi {posisi} di luar jangkauan untuk kategori '{kategori}' "
            f"(tersedia 1-{len(berkas)})."
        )

    nama = berkas[posisi - 1]
    img = cv2.imread(os.path.join(folder, nama))
    if img is None:
        raise ValueError(f"Citra '{nama}' gagal dibaca.")

    return img, nama
