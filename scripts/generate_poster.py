"""
Penghasil Poster Ringkasan Pengolahan Citra Digital (PCD)
---------------------------------------------------------
Menjalankan tujuh Kelompok Operasi PCD pada citra contoh dan menyimpan delapan
berkas PNG ke folder output/.

Ini adalah satu-satunya berkas yang memakai matplotlib untuk menyusun gambar.
Tampilan web di web/ memakai cv2.imencode dan tidak memanggil berkas ini.

Jalankan:  python scripts/generate_poster.py
"""

import os
import sys

# Agar dapat mengimpor pcd_operations dan main dari akar proyek.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from main import (  # noqa: E402
    OUTPUT_DIR,
    bgr2rgb,
    ensure_output_dir,
    load_sample_images,
)
from pcd_operations import (  # noqa: E402
    adaptive_thresholding,
    brightening,
    citra_negatif,
    ekualisasi_histogram,
    flipping,
    gamma_correction,
    hitung_histogram,
    manual_thresholding,
    operasi_aritmetika,
    otsu_thresholding,
    rgb_to_grayscale,
    rotasi,
    translasi,
    zooming,
)


# ==============================================================================
# POSTER 1: CITRA NEGATIF
# ==============================================================================
def demo_citra_negatif(img: np.ndarray):
    print("\n--- 1. Menjalankan Citra Negatif ---")
    gray = rgb_to_grayscale(img, method="luminosity")

    negatif_warna = citra_negatif(img)
    negatif_gray = citra_negatif(gray)

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle("1. Pembuatan Citra Negatif (s = 255 - r)", fontsize=14, fontweight="bold")

    axes[0, 0].imshow(bgr2rgb(img))
    axes[0, 0].set_title("Citra Asli (Berwarna)")
    axes[0, 0].axis("off")

    axes[0, 1].imshow(bgr2rgb(negatif_warna))
    axes[0, 1].set_title("Citra Negatif Berwarna")
    axes[0, 1].axis("off")

    axes[1, 0].imshow(gray, cmap="gray")
    axes[1, 0].set_title("Citra Asli (Grayscale)")
    axes[1, 0].axis("off")

    axes[1, 1].imshow(negatif_gray, cmap="gray")
    axes[1, 1].set_title("Citra Negatif Grayscale")
    axes[1, 1].axis("off")

    plt.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, "1_citra_negatif.png")
    plt.savefig(save_path, dpi=200)
    plt.close()
    print(f"[OK] Hasil disimpan ke: {save_path}")


# ==============================================================================
# POSTER 2: GRAYSCALE
# ==============================================================================
def demo_grayscale(img: np.ndarray):
    print("\n--- 2. Menjalankan Konversi Grayscale ---")
    gray_lum = rgb_to_grayscale(img, method="luminosity")
    gray_avg = rgb_to_grayscale(img, method="average")
    gray_light = rgb_to_grayscale(img, method="lightness")

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle("2. Konversi Citra Berwarna ke Grayscale", fontsize=14, fontweight="bold")

    axes[0, 0].imshow(bgr2rgb(img))
    axes[0, 0].set_title("Citra Asli (RGB)")
    axes[0, 0].axis("off")

    axes[0, 1].imshow(gray_lum, cmap="gray")
    axes[0, 1].set_title("Luminosity (0.299R + 0.587G + 0.114B)")
    axes[0, 1].axis("off")

    axes[1, 0].imshow(gray_avg, cmap="gray")
    axes[1, 0].set_title("Average ((R + G + B) / 3)")
    axes[1, 0].axis("off")

    axes[1, 1].imshow(gray_light, cmap="gray")
    axes[1, 1].set_title("Lightness ((max + min) / 2)")
    axes[1, 1].axis("off")

    plt.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, "2_grayscale.png")
    plt.savefig(save_path, dpi=200)
    plt.close()
    print(f"[OK] Hasil disimpan ke: {save_path}")


# ==============================================================================
# POSTER 3: IMAGE BRIGHTENING
# ==============================================================================
def demo_brightening(img: np.ndarray):
    print("\n--- 3. Menjalankan Image Brightening ---")
    terang_bias = brightening(img, beta=60, alpha=1.0)
    gelap_bias = brightening(img, beta=-60, alpha=1.0)
    kontras_terang = brightening(img, beta=40, alpha=1.3)
    gamma_terang = gamma_correction(img, gamma=1.8)

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    fig.suptitle("3. Image Brightening (Pencerahan Citra)", fontsize=14, fontweight="bold")

    axes[0, 0].imshow(bgr2rgb(img))
    axes[0, 0].set_title("Citra Asli")
    axes[0, 0].axis("off")

    axes[0, 1].imshow(bgr2rgb(terang_bias))
    axes[0, 1].set_title("Pencerahan Bias (g = f + 60)")
    axes[0, 1].axis("off")

    axes[0, 2].imshow(bgr2rgb(gelap_bias))
    axes[0, 2].set_title("Penggelapan Bias (g = f - 60)")
    axes[0, 2].axis("off")

    axes[1, 0].imshow(bgr2rgb(img))
    axes[1, 0].set_title("Citra Asli")
    axes[1, 0].axis("off")

    axes[1, 1].imshow(bgr2rgb(kontras_terang))
    axes[1, 1].set_title("Linier (g = 1.3*f + 40)")
    axes[1, 1].axis("off")

    axes[1, 2].imshow(bgr2rgb(gamma_terang))
    axes[1, 2].set_title("Gamma Correction (gamma = 1.8)")
    axes[1, 2].axis("off")

    plt.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, "3_brightening.png")
    plt.savefig(save_path, dpi=200)
    plt.close()
    print(f"[OK] Hasil disimpan ke: {save_path}")


# ==============================================================================
# POSTER 4: OPERASI ARITMETIKA DUA CITRA
# ==============================================================================
def demo_aritmetika(img1: np.ndarray, img2: np.ndarray):
    print("\n--- 4. Menjalankan Operasi Aritmetika Dua Buah Citra ---")
    tambah = operasi_aritmetika(img1, img2, operasi="penjumlahan")
    kurang = operasi_aritmetika(img1, img2, operasi="pengurangan")
    kali = operasi_aritmetika(img1, img2, operasi="perkalian")
    bagi = operasi_aritmetika(img1, img2, operasi="pembagian")
    blend = operasi_aritmetika(img1, img2, operasi="blending", weight1=0.6, weight2=0.4)

    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    fig.suptitle("4. Operasi Aritmetika Dua Citra", fontsize=14, fontweight="bold")

    axes[0, 0].imshow(bgr2rgb(img1))
    axes[0, 0].set_title("Citra 1 (f1)")
    axes[0, 0].axis("off")

    axes[0, 1].imshow(bgr2rgb(img2))
    axes[0, 1].set_title("Citra 2 (f2)")
    axes[0, 1].axis("off")

    axes[0, 2].imshow(bgr2rgb(tambah))
    axes[0, 2].set_title("Penjumlahan (f1 + f2)")
    axes[0, 2].axis("off")

    axes[0, 3].imshow(bgr2rgb(kurang))
    axes[0, 3].set_title("Pengurangan (|f1 - f2|)")
    axes[0, 3].axis("off")

    axes[1, 0].imshow(bgr2rgb(kali))
    axes[1, 0].set_title("Perkalian ((f1 * f2) / 255)")
    axes[1, 0].axis("off")

    axes[1, 1].imshow(bgr2rgb(bagi))
    axes[1, 1].set_title("Pembagian ((f1 / (f2+1)) * 255)")
    axes[1, 1].axis("off")

    axes[1, 2].imshow(bgr2rgb(blend))
    axes[1, 2].set_title("Blending (0.6*f1 + 0.4*f2)")
    axes[1, 2].axis("off")

    # Kosongkan subplot terakhir untuk estetika
    axes[1, 3].axis("off")

    plt.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, "4_aritmetika.png")
    plt.savefig(save_path, dpi=200)
    plt.close()
    print(f"[OK] Hasil disimpan ke: {save_path}")


# ==============================================================================
# POSTER 5: OPERASI GEOMETRI
# ==============================================================================
def demo_geometri(img: np.ndarray):
    print("\n--- 5. Menjalankan Operasi Geometri ---")
    # Translasi
    img_trans = translasi(img, tx=120, ty=80)
    # Rotasi
    img_rot45 = rotasi(img, angle=45)
    img_rot90 = rotasi(img, angle=90)
    # Flipping
    img_flip_h = flipping(img, mode="horizontal")
    img_flip_v = flipping(img, mode="vertikal")
    img_flip_hv = flipping(img, mode="keduanya")
    # Zooming
    img_zoom_in = zooming(img, factor=1.7, maintain_size=True)
    img_zoom_out = zooming(img, factor=0.5, maintain_size=True)

    fig, axes = plt.subplots(3, 3, figsize=(14, 12))
    fig.suptitle("5. Operasi Geometri Citra", fontsize=14, fontweight="bold")

    axes[0, 0].imshow(bgr2rgb(img))
    axes[0, 0].set_title("Citra Asli")
    axes[0, 0].axis("off")

    axes[0, 1].imshow(bgr2rgb(img_trans))
    axes[0, 1].set_title("Translasi (tx=120, ty=80)")
    axes[0, 1].axis("off")

    axes[0, 2].imshow(bgr2rgb(img_rot45))
    axes[0, 2].set_title("Rotasi (45 Derajat)")
    axes[0, 2].axis("off")

    axes[1, 0].imshow(bgr2rgb(img_rot90))
    axes[1, 0].set_title("Rotasi (90 Derajat)")
    axes[1, 0].axis("off")

    axes[1, 1].imshow(bgr2rgb(img_flip_h))
    axes[1, 1].set_title("Flipping Horizontal")
    axes[1, 1].axis("off")

    axes[1, 2].imshow(bgr2rgb(img_flip_v))
    axes[1, 2].set_title("Flipping Vertikal")
    axes[1, 2].axis("off")

    axes[2, 0].imshow(bgr2rgb(img_flip_hv))
    axes[2, 0].set_title("Flipping Horizontal & Vertikal")
    axes[2, 0].axis("off")

    axes[2, 1].imshow(bgr2rgb(img_zoom_in))
    axes[2, 1].set_title("Zoom In (1.7x)")
    axes[2, 1].axis("off")

    axes[2, 2].imshow(bgr2rgb(img_zoom_out))
    axes[2, 2].set_title("Zoom Out (0.5x)")
    axes[2, 2].axis("off")

    plt.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, "5_geometri.png")
    plt.savefig(save_path, dpi=200)
    plt.close()
    print(f"[OK] Hasil disimpan ke: {save_path}")


# ==============================================================================
# POSTER 6: HISTOGRAM DAN HISTOGRAM EQUALIZATION
# ==============================================================================
def demo_histogram(img: np.ndarray):
    print("\n--- 6. Menjalankan Histogram & Histogram Equalization ---")
    gray = rgb_to_grayscale(img, method="luminosity")
    gray_eq = ekualisasi_histogram(gray)

    hist_gray = hitung_histogram(gray)
    hist_gray_eq = hitung_histogram(gray_eq)
    hist_color = hitung_histogram(img)

    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    fig.suptitle("6. Histogram dan Ekualisasi Histogram Citra", fontsize=15, fontweight="bold")

    # Baris 1: Citra Grayscale Asli dan Histogramnya
    axes[0, 0].imshow(gray, cmap="gray")
    axes[0, 0].set_title("Citra Grayscale Asli")
    axes[0, 0].axis("off")

    axes[0, 1].bar(range(256), hist_gray, color="gray", width=1.0)
    axes[0, 1].set_title("Histogram Citra Grayscale Asli (h(rk) = nk)")
    axes[0, 1].set_xlim([0, 255])
    axes[0, 1].set_xlabel("Tingkat Intensitas Piksel (r)")
    axes[0, 1].set_ylabel("Frekuensi (n)")
    axes[0, 1].grid(True, linestyle="--", alpha=0.5)

    # Baris 2: Citra Hasil Ekualisasi dan Histogramnya
    axes[1, 0].imshow(gray_eq, cmap="gray")
    axes[1, 0].set_title("Hasil Ekualisasi Histogram (Peningkatan Kontras)")
    axes[1, 0].axis("off")

    axes[1, 1].bar(range(256), hist_gray_eq, color="black", width=1.0)
    axes[1, 1].set_title("Histogram Setelah Ekualisasi (Distribusi Merata)")
    axes[1, 1].set_xlim([0, 255])
    axes[1, 1].set_xlabel("Tingkat Intensitas Piksel (s)")
    axes[1, 1].set_ylabel("Frekuensi (n)")
    axes[1, 1].grid(True, linestyle="--", alpha=0.5)

    # Baris 3: Citra Berwarna dan Histogram Kanal RGB
    axes[2, 0].imshow(bgr2rgb(img))
    axes[2, 0].set_title("Citra Berwarna (RGB)")
    axes[2, 0].axis("off")

    axes[2, 1].plot(hist_color["r"], color="red", label="Red (R)", linewidth=1.5)
    axes[2, 1].plot(hist_color["g"], color="green", label="Green (G)", linewidth=1.5)
    axes[2, 1].plot(hist_color["b"], color="blue", label="Blue (B)", linewidth=1.5)
    axes[2, 1].set_title("Histogram Kanal Warna RGB")
    axes[2, 1].set_xlim([0, 255])
    axes[2, 1].set_xlabel("Tingkat Intensitas Piksel (0 - 255)")
    axes[2, 1].set_ylabel("Frekuensi")
    axes[2, 1].legend(loc="upper right")
    axes[2, 1].grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, "6_histogram.png")
    plt.savefig(save_path, dpi=200)
    plt.close()
    print(f"[OK] Hasil disimpan ke: {save_path}")


# ==============================================================================
# POSTER 7: THRESHOLDING CITRA (MANUAL, OTSU, ADAPTIVE)
# ==============================================================================
def demo_thresholding(img: np.ndarray):
    print("\n--- 7. Menjalankan Thresholding Citra ---")
    gray = rgb_to_grayscale(img, method="luminosity")

    # Manual Thresholding
    thresh_bin = manual_thresholding(gray, threshold=127, mode="binary")
    thresh_bin_inv = manual_thresholding(gray, threshold=127, mode="binary_inv")
    thresh_trunc = manual_thresholding(gray, threshold=127, mode="trunc")
    thresh_tozero = manual_thresholding(gray, threshold=127, mode="tozero")
    thresh_tozero_inv = manual_thresholding(gray, threshold=127, mode="tozero_inv")

    # Otsu & Adaptive Thresholding
    thresh_otsu, optimal_t = otsu_thresholding(gray)
    thresh_adapt_mean = adaptive_thresholding(gray, method="mean", block_size=15, c=3)
    thresh_adapt_gauss = adaptive_thresholding(gray, method="gaussian", block_size=15, c=3)

    fig, axes = plt.subplots(3, 3, figsize=(14, 12))
    fig.suptitle("7. Thresholding Citra (Manual, Otsu, dan Adaptive)", fontsize=15, fontweight="bold")

    axes[0, 0].imshow(gray, cmap="gray")
    axes[0, 0].set_title("Citra Grayscale Input")
    axes[0, 0].axis("off")

    axes[0, 1].imshow(thresh_bin, cmap="gray")
    axes[0, 1].set_title("Binary (T = 127)")
    axes[0, 1].axis("off")

    axes[0, 2].imshow(thresh_bin_inv, cmap="gray")
    axes[0, 2].set_title("Binary Inverted (T = 127)")
    axes[0, 2].axis("off")

    axes[1, 0].imshow(thresh_trunc, cmap="gray")
    axes[1, 0].set_title("Truncate (T = 127)")
    axes[1, 0].axis("off")

    axes[1, 1].imshow(thresh_tozero, cmap="gray")
    axes[1, 1].set_title("Threshold to Zero (T = 127)")
    axes[1, 1].axis("off")

    axes[1, 2].imshow(thresh_tozero_inv, cmap="gray")
    axes[1, 2].set_title("Threshold to Zero Inverted (T = 127)")
    axes[1, 2].axis("off")

    axes[2, 0].imshow(thresh_otsu, cmap="gray")
    axes[2, 0].set_title(f"Otsu Thresholding (T* = {optimal_t:.1f})")
    axes[2, 0].axis("off")

    axes[2, 1].imshow(thresh_adapt_mean, cmap="gray")
    axes[2, 1].set_title("Adaptive Mean (Block 15, C=3)")
    axes[2, 1].axis("off")

    axes[2, 2].imshow(thresh_adapt_gauss, cmap="gray")
    axes[2, 2].set_title("Adaptive Gaussian (Block 15, C=3)")
    axes[2, 2].axis("off")

    plt.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, "7_thresholding.png")
    plt.savefig(save_path, dpi=200)
    plt.close()
    print(f"[OK] Hasil disimpan ke: {save_path}")


# ==============================================================================
# POSTER RINGKASAN: SEMUA OPERASI DALAM 1 POSTER GRID
# ==============================================================================
def demo_summary(img1: np.ndarray, img2: np.ndarray):
    print("\n--- Membuat Poster Ringkasan Semua Operasi PCD ---")
    neg = citra_negatif(img1)
    gray = rgb_to_grayscale(img1, method="luminosity")
    terang = brightening(img1, beta=50, alpha=1.2)
    blend = operasi_aritmetika(img1, img2, operasi="blending", weight1=0.5, weight2=0.5)
    trans = translasi(img1, tx=80, ty=50)
    rot = rotasi(img1, angle=30)
    zoom = zooming(img1, factor=1.5, maintain_size=True)
    gray_eq = ekualisasi_histogram(gray)
    otsu_img, opt_t = otsu_thresholding(gray)

    fig, axes = plt.subplots(3, 3, figsize=(15, 13))
    fig.suptitle("Ringkasan Operasi Lengkap Pengolahan Citra Digital (PCD)", fontsize=16, fontweight="bold")

    daftar_visual = [
        ("1. Citra Asli (RGB)", bgr2rgb(img1), None),
        ("2. Citra Negatif (s = 255 - r)", bgr2rgb(neg), None),
        ("3. Grayscale (Luminosity)", gray, "gray"),
        ("4. Brightening (Alpha 1.2, Beta 50)", bgr2rgb(terang), None),
        ("5. Aritmetika: Blending Citra 1 & 2", bgr2rgb(blend), None),
        ("6. Geometri: Translasi (+80, +50)", bgr2rgb(trans), None),
        ("7. Geometri: Zoom In (1.5x)", bgr2rgb(zoom), None),
        ("8. Ekualisasi Histogram (Kontras)", gray_eq, "gray"),
        (f"9. Otsu Thresholding (T*={opt_t:.1f})", otsu_img, "gray"),
    ]

    for idx, (title, img_data, cmap) in enumerate(daftar_visual):
        r, c = divmod(idx, 3)
        if cmap:
            axes[r, c].imshow(img_data, cmap=cmap)
        else:
            axes[r, c].imshow(img_data)
        axes[r, c].set_title(title, fontsize=12, fontweight="bold")
        axes[r, c].axis("off")

    plt.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, "summary_all.png")
    plt.savefig(save_path, dpi=200)
    plt.close()
    print(f"[OK] Poster ringkasan disimpan ke: {save_path}")


def main():
    print("=================================================================")
    print("     GENERATOR POSTER PENGOLAHAN CITRA DIGITAL (PCD)             ")
    print("=================================================================")

    ensure_output_dir()
    img1, img2 = load_sample_images()

    demo_citra_negatif(img1)
    demo_grayscale(img1)
    demo_brightening(img1)
    demo_aritmetika(img1, img2)
    demo_geometri(img1)
    demo_histogram(img1)
    demo_thresholding(img1)
    demo_summary(img1, img2)

    print("\n=================================================================")
    print("[SUKSES] Seluruh poster selesai dibuat!")
    print(f"Semua berkas disimpan di: {OUTPUT_DIR}")
    print("=================================================================")


if __name__ == "__main__":
    main()
