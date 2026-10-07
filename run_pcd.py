"""
CLI Interaktif untuk Pengolahan Citra Digital (PCD)
---------------------------------------------------
Memungkinkan pengguna memilih kategori citra (cat, dog, fox, hamster, rabbit)
dan indeks citra untuk menerapkan dan melihat operasi PCD.
"""

import argparse
import os
import sys
import cv2

from pcd_operations import (
    citra_negatif,
    rgb_to_grayscale,
    brightening,
    gamma_correction,
    operasi_aritmetika,
    translasi,
    rotasi,
    flipping,
    zooming,
)
from main import (
    bgr2rgb,
    ensure_output_dir,
    BASE_DIR,
    DATASET_DIR,
    OUTPUT_DIR,
)
from scripts.generate_poster import (
    demo_citra_negatif,
    demo_grayscale,
    demo_brightening,
    demo_aritmetika,
    demo_geometri,
    demo_histogram,
    demo_thresholding,
    demo_summary,
)


def list_categories():
    categories = [
        d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d)) and not d.startswith(".")
    ]
    return sorted(categories)


def get_image_path(category: str, index: int = 1) -> str:
    path = os.path.join(DATASET_DIR, category, f"{category}_{index}.jpg")
    if not os.path.exists(path):
        # Coba format ekstensi lain jika ada
        candidates = [
            f for f in os.listdir(os.path.join(DATASET_DIR, category)) if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        if candidates:
            path = os.path.join(DATASET_DIR, category, candidates[min(index - 1, len(candidates) - 1)])
        else:
            raise FileNotFoundError(f"Tidak ada citra dalam kategori '{category}'")
    return path


def interactive_menu():
    categories = list_categories()
    print("\n" + "=" * 50)
    print("      MENU INTERAKTIF OPERASI CITRA DIGITAL")
    print("=" * 50)
    print("Kategori dataset yang tersedia:")
    for i, cat in enumerate(categories, 1):
        print(f"  [{i}] {cat.capitalize()}")

    try:
        cat_choice = int(input("\nPilih kategori citra pertama (nomor): ").strip())
        cat1 = categories[cat_choice - 1]
    except (ValueError, IndexError):
        cat1 = "cat"
        print(f"Pilihan tidak valid, default ke '{cat1}'.")

    try:
        idx1 = int(input(f"Pilih indeks citra {cat1} (1-10) [default 1]: ").strip() or "1")
    except ValueError:
        idx1 = 1

    try:
        cat2_choice = int(input("\nPilih kategori citra kedua untuk operasi aritmetika (nomor): ").strip())
        cat2 = categories[cat2_choice - 1]
    except (ValueError, IndexError):
        cat2 = "dog"
        print(f"Pilihan tidak valid, default ke '{cat2}'.")

    try:
        idx2 = int(input(f"Pilih indeks citra {cat2} (1-10) [default 1]: ").strip() or "1")
    except ValueError:
        idx2 = 1

    path1 = get_image_path(cat1, idx1)
    path2 = get_image_path(cat2, idx2)

    img1 = cv2.imread(path1)
    img2 = cv2.imread(path2)

    print(f"\nMemproses Citra 1: {path1}")
    print(f"Memproses Citra 2: {path2}")

    ensure_output_dir()
    demo_citra_negatif(img1)
    demo_grayscale(img1)
    demo_brightening(img1)
    demo_aritmetika(img1, img2)
    demo_geometri(img1)
    demo_histogram(img1)
    demo_thresholding(img1)
    demo_summary(img1, img2)

    print("\n[SELESAI] Hasil visualisasi telah disimpan di folder:", OUTPUT_DIR)


def main_cli():
    parser = argparse.ArgumentParser(description="Program Pengolahan Citra Digital (PCD)")
    parser.add_argument(
        "--category1",
        "-c1",
        default="cat",
        help="Kategori citra pertama (cat, dog, fox, hamster, rabbit)",
    )
    parser.add_argument("--index1", "-i1", type=int, default=1, help="Indeks citra pertama (1-10)")
    parser.add_argument(
        "--category2",
        "-c2",
        default="dog",
        help="Kategori citra kedua untuk operasi aritmetika",
    )
    parser.add_argument("--index2", "-i2", type=int, default=1, help="Indeks citra kedua (1-10)")
    parser.add_argument("--interactive", action="store_true", help="Jalankan dalam mode menu interaktif")

    args = parser.parse_args()

    if args.interactive:
        interactive_menu()
        return

    path1 = get_image_path(args.category1, args.index1)
    path2 = get_image_path(args.category2, args.index2)

    img1 = cv2.imread(path1)
    img2 = cv2.imread(path2)

    ensure_output_dir()
    demo_citra_negatif(img1)
    demo_grayscale(img1)
    demo_brightening(img1)
    demo_aritmetika(img1, img2)
    demo_geometri(img1)
    demo_histogram(img1)
    demo_thresholding(img1)
    demo_summary(img1, img2)


if __name__ == "__main__":
    main_cli()
