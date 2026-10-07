"""
Modul Operasi Pengolahan Citra Digital (PCD)
--------------------------------------------
Mencakup implementasi fungsi-fungsi dasar PCD:
1. Citra Negatif
2. Konversi Citra Berwarna ke Grayscale
3. Image Brightening (Pencerahan Citra)
4. Operasi Aritmetika Dua Citra (Penjumlahan, Pengurangan, Perkalian, Pembagian, Blending)
5. Operasi Geometri (Translasi, Rotasi, Flipping, Zooming)
6. Histogram Citra dan Ekualisasi Histogram
7. Thresholding Citra (Manual/Global, Otsu, dan Adaptive)
"""

import cv2
import numpy as np


# ==============================================================================
# 1. MEMBUAT CITRA NEGATIF
# ==============================================================================
def citra_negatif(image: np.ndarray) -> np.ndarray:
    """
    Membuat citra negatif dari citra input (grayscale atau berwarna).
    Rumus matematis:
        s = (L - 1) - r = 255 - r
    di mana r adalah nilai intensitas piksel asli, dan s adalah intensitas baru.
    """
    # 255 - image secara otomatis membalik seluruh nilai piksel per kanal
    return 255 - image


# ==============================================================================
# 2. MENGUBAH CITRA BERWARNA MENJADI GRAYSCALE
# ==============================================================================
def rgb_to_grayscale(image: np.ndarray, method: str = "luminosity") -> np.ndarray:
    """
    Mengubah citra berwarna (BGR/RGB) menjadi citra grayscale.

    Metode yang tersedia:
    - 'luminosity' (CIE / ITU-R BT.601):
        Y = 0.299*R + 0.587*G + 0.114*B
        (Memperhitungkan sensitivitas mata manusia terhadap warna hijau)
    - 'average':
        Y = (R + G + B) / 3
    - 'lightness':
        Y = (max(R, G, B) + min(R, G, B)) / 2
    - 'opencv':
        Menggunakan cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    """
    if len(image.shape) == 2:
        # Sudah grayscale
        return image.copy()

    # OpenCV membaca citra dalam format BGR
    b = image[:, :, 0].astype(np.float32)
    g = image[:, :, 1].astype(np.float32)
    r = image[:, :, 2].astype(np.float32)

    method = method.lower()
    if method == "luminosity":
        gray = 0.299 * r + 0.587 * g + 0.114 * b
    elif method == "average":
        gray = (r + g + b) / 3.0
    elif method == "lightness":
        max_c = np.maximum(np.maximum(r, g), b)
        min_c = np.minimum(np.minimum(r, g), b)
        gray = (max_c + min_c) / 2.0
    elif method == "opencv":
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        raise ValueError(f"Metode grayscale '{method}' tidak dikenali. Pilih: luminosity, average, lightness, opencv")

    # Pastikan hasil dalam rentang [0, 255] dan tipe uint8
    gray_clipped = np.clip(gray, 0, 255).astype(np.uint8)
    return gray_clipped


# ==============================================================================
# 3. IMAGE BRIGHTENING
# ==============================================================================
def brightening(image: np.ndarray, beta: int = 50, alpha: float = 1.0) -> np.ndarray:
    """
    Mengubah kecerahan (dan kontras) citra.
    Rumus transformasi linier:
        g(x, y) = alpha * f(x, y) + beta
    di mana:
        - alpha: faktor pengali kontras (alpha > 1: kontras naik, alpha < 1: kontras turun)
        - beta : nilai bias kecerahan (beta > 0: lebih terang, beta < 0: lebih gelap)
    Hasil dipotong (clipping) pada rentang [0, 255].
    """
    # Gunakan float32 untuk menghindari overflow sebelum clipping
    adjusted = image.astype(np.float32) * alpha + beta
    return np.clip(adjusted, 0, 255).astype(np.uint8)


def gamma_correction(image: np.ndarray, gamma: float = 1.5) -> np.ndarray:
    """
    Pencerahan non-linier menggunakan Power-Law (Gamma Correction).
    Rumus:
        s = c * (r / 255) ^ (1 / gamma) * 255
    - gamma > 1.0: mencerahkan area bayangan/gelap tanpa overexpose area terang
    - gamma < 1.0: menggelapkan citra
    """
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype(np.uint8)
    return cv2.LUT(image, table)


# ==============================================================================
# 4. OPERASI ARITMETIKA DUA BUAH CITRA
# ==============================================================================
def match_dimensions(img1: np.ndarray, img2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Menyamakan dimensi dua citra agar operasi aritmetika per-piksel dapat dilakukan.
    Citra kedua di-resize agar cocok dengan citra pertama.
    """
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]

    # Sesuaikan ukuran jika berbeda
    if (h1, w1) != (h2, w2):
        img2_matched = cv2.resize(img2, (w1, h1), interpolation=cv2.INTER_LINEAR)
    else:
        img2_matched = img2.copy()

    # Sesuaikan jumlah kanal jika berbeda (misal 1 grayscale dan 1 berwarna)
    if len(img1.shape) == 3 and len(img2_matched.shape) == 2:
        img2_matched = cv2.cvtColor(img2_matched, cv2.COLOR_GRAY2BGR)
    elif len(img1.shape) == 2 and len(img2_matched.shape) == 3:
        img1 = cv2.cvtColor(img1, cv2.COLOR_GRAY2BGR)

    return img1, img2_matched


def operasi_aritmetika(
    img1: np.ndarray,
    img2: np.ndarray,
    operasi: str = "penjumlahan",
    weight1: float = 0.5,
    weight2: float = 0.5,
) -> np.ndarray:
    """
    Melakukan operasi aritmetika antara dua citra.

    Operasi:
    - 'penjumlahan' / 'add':
        g(x, y) = clip(f1(x, y) + f2(x, y), 0, 255)
    - 'pengurangan' / 'subtract':
        g(x, y) = clip(|f1(x, y) - f2(x, y)|, 0, 255)
    - 'perkalian' / 'multiply':
        g(x, y) = clip((f1(x, y) * f2(x, y)) / 255, 0, 255)
    - 'pembagian' / 'divide':
        g(x, y) = clip((f1(x, y) / (f2(x, y) + 1)) * 255, 0, 255)
    - 'blending' / 'weighted':
        g(x, y) = clip(w1 * f1(x, y) + w2 * f2(x, y), 0, 255)
    """
    im1, im2 = match_dimensions(img1, img2)
    f1 = im1.astype(np.float32)
    f2 = im2.astype(np.float32)

    op = operasi.lower()
    if op in ["penjumlahan", "add"]:
        res = f1 + f2
    elif op in ["pengurangan", "subtract"]:
        res = np.abs(f1 - f2)
    elif op in ["perkalian", "multiply"]:
        res = (f1 * f2) / 255.0
    elif op in ["pembagian", "divide"]:
        # Tambahkan epsilon kecil (+1.0) untuk menghindari pembagian dengan nol
        res = (f1 / (f2 + 1.0)) * 255.0
    elif op in ["blending", "weighted"]:
        res = (weight1 * f1) + (weight2 * f2)
    else:
        raise ValueError(
            f"Operasi '{operasi}' tidak dikenali. Pilihan: penjumlahan, pengurangan, perkalian, pembagian, blending"
        )

    return np.clip(res, 0, 255).astype(np.uint8)


# ==============================================================================
# 5. OPERASI GEOMETRI
# ==============================================================================
def translasi(image: np.ndarray, tx: int = 50, ty: int = 30) -> np.ndarray:
    """
    Translasi citra sejauh tx (horizontal) dan ty (vertikal).
    Matriks Transformasi Affine:
        T = [[1, 0, tx],
             [0, 1, ty]]
    """
    h, w = image.shape[:2]
    matriks_translasi = np.float32([[1, 0, tx], [0, 1, ty]])
    hasil = cv2.warpAffine(image, matriks_translasi, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    return hasil


def rotasi(image: np.ndarray, angle: float = 45.0, scale: float = 1.0) -> np.ndarray:
    """
    Rotasi citra sebesar sudut 'angle' (derajat berlawanan arah jarum jam)
    terhadap titik pusat citra.
    """
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    matriks_rotasi = cv2.getRotationMatrix2D(center, angle, scale)
    hasil = cv2.warpAffine(image, matriks_rotasi, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    return hasil


def flipping(image: np.ndarray, mode: str = "horizontal") -> np.ndarray:
    """
    Pencerminan (Flipping) citra:
    - 'horizontal': pencerminan terhadap sumbu vertikal (kiri <-> kanan)
    - 'vertikal' / 'vertical': pencerminan terhadap sumbu horizontal (atas <-> bawah)
    - 'keduanya' / 'both': pencerminan horizontal sekaligus vertikal
    """
    m = mode.lower()
    if m in ["horizontal", "h"]:
        # Sumbu Y (1 pada cv2.flip atau image[:, ::-1])
        return cv2.flip(image, 1)
    elif m in ["vertikal", "vertical", "v"]:
        # Sumbu X (0 pada cv2.flip atau image[::-1, :])
        return cv2.flip(image, 0)
    elif m in ["keduanya", "both", "hv", "vh"]:
        # Kedua sumbu (-1 pada cv2.flip)
        return cv2.flip(image, -1)
    else:
        raise ValueError(f"Mode flipping '{mode}' tidak valid. Pilihan: horizontal, vertikal, keduanya")


def zooming(image: np.ndarray, factor: float = 1.5, maintain_size: bool = True) -> np.ndarray:
    """
    Perbesaran / Pengecilan citra (Zooming):
    - factor > 1.0 : Zoom In
    - factor < 1.0 : Zoom Out
    - maintain_size = True : Citra hasil dipertahankan berukuran sama dengan citra asli
                             (Zoom In: crop area tengah lalu resize ke ukuran asli,
                              Zoom Out: resize lebih kecil lalu beri padding border hitam).
    - maintain_size = False: Citra hasil langsung berukuran faktor * dimensi asli.
    """
    h, w = image.shape[:2]

    if not maintain_size:
        new_w = max(1, int(w * factor))
        new_h = max(1, int(h * factor))
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    if factor >= 1.0:
        # Zoom In mempertahankan ukuran kanvas:
        # Ambil ROI (Region of Interest) di tengah kemudian di-upscale ke (w, h)
        crop_w = int(w / factor)
        crop_h = int(h / factor)
        start_x = (w - crop_w) // 2
        start_y = (h - crop_h) // 2
        cropped = image[start_y : start_y + crop_h, start_x : start_x + crop_w]
        return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)
    else:
        # Zoom Out mempertahankan ukuran kanvas:
        # Resize lebih kecil lalu tempatkan di tengah kanvas hitam
        small_w = int(w * factor)
        small_h = int(h * factor)
        small_img = cv2.resize(image, (small_w, small_h), interpolation=cv2.INTER_AREA)

        # Buat canvas kosong
        if len(image.shape) == 3:
            canvas = np.zeros((h, w, image.shape[2]), dtype=np.uint8)
        else:
            canvas = np.zeros((h, w), dtype=np.uint8)

        start_x = (w - small_w) // 2
        start_y = (h - small_h) // 2
        canvas[start_y : start_y + small_h, start_x : start_x + small_w] = small_img
        return canvas


# ==============================================================================
# 6. HISTOGRAM DAN HISTOGRAM EQUALIZATION
# ==============================================================================
def hitung_histogram(image: np.ndarray, normalize: bool = False) -> np.ndarray | dict[str, np.ndarray]:
    """
    Menghitung histogram citra.

    Rumus Matematis:
        h(r_k) = n_k
    di mana:
        - r_k : tingkat intensitas ke-k (k = 0, 1, ..., 255 untuk citra 8-bit)
        - n_k : banyaknya piksel yang bernilai intensitas r_k
        - M x N: dimensi citra (total piksel)

    Jika normalize=True (Probability Density Function):
        p(r_k) = n_k / (M * N)

    Output:
    - np.ndarray (panjang 256) jika citra grayscale (2D)
    - dict {'b': array, 'g': array, 'r': array} jika citra berwarna (3D BGR)
    """
    if len(image.shape) == 2:
        # Grayscale
        hist = np.bincount(image.ravel(), minlength=256).astype(np.float32)
        if normalize:
            hist /= float(image.size)
        return hist
    else:
        # Berwarna (BGR)
        total_pixels = float(image.shape[0] * image.shape[1])
        hist_b = np.bincount(image[:, :, 0].ravel(), minlength=256).astype(np.float32)
        hist_g = np.bincount(image[:, :, 1].ravel(), minlength=256).astype(np.float32)
        hist_r = np.bincount(image[:, :, 2].ravel(), minlength=256).astype(np.float32)

        if normalize:
            hist_b /= total_pixels
            hist_g /= total_pixels
            hist_r /= total_pixels

        return {"b": hist_b, "g": hist_g, "r": hist_r}


def ekualisasi_histogram(image: np.ndarray) -> np.ndarray:
    """
    Melakukan ekualisasi histogram (Histogram Equalization) untuk meningkatkan kontras citra.

    Rumus Matematis:
    1. Fungsi Distribusi Kumulatif (CDF):
        CDF(r_k) = sum_{j=0}^{k} p(r_j)
    2. Transformasi Perataan (Mapping):
        s_k = round( (CDF(r_k) - CDF_min) / ((M * N) - CDF_min) * (L - 1) )
       di mana L = 256 (intensitas maksimum + 1).

    Untuk citra berwarna (3D BGR):
    Citra dikonversi ke ruang warna YCrCb, ekualisasi diterapkan hanya pada kanal Y (Luminance),
    lalu dikembalikan ke format BGR agar warna tidak mengalami pergeseran saturasi/hue liar.
    """
    if len(image.shape) == 2:
        # Grayscale: gunakan implementasi CDF murni atau cv2.equalizeHist
        return cv2.equalizeHist(image)
    else:
        # Citra Berwarna: Ekualisasi pada kanal Luminance (Y) ruang warna YCrCb
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
        return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)


# ==============================================================================
# 7. THRESHOLDING CITRA (MANUAL, OTSU, DAN ADAPTIVE)
# ==============================================================================
def manual_thresholding(
    image: np.ndarray,
    threshold: int = 127,
    max_val: int = 255,
    mode: str = "binary",
) -> np.ndarray:
    """
    Melakukan segmentasi pengambangan (thresholding) global manual pada citra grayscale.

    Rumus Matematis untuk setiap mode (dengan nilai ambang T = threshold, M = max_val):

    1. 'binary':
        g(x, y) = M   jika f(x, y) > T
                  0   jika f(x, y) <= T

    2. 'binary_inv':
        g(x, y) = 0   jika f(x, y) > T
                  M   jika f(x, y) <= T

    3. 'trunc':
        g(x, y) = T       jika f(x, y) > T
                  f(x, y) jika f(x, y) <= T

    4. 'tozero':
        g(x, y) = f(x, y) jika f(x, y) > T
                  0       jika f(x, y) <= T

    5. 'tozero_inv':
        g(x, y) = 0       jika f(x, y) > T
                  f(x, y) jika f(x, y) <= T
    """
    if len(image.shape) == 3:
        gray = rgb_to_grayscale(image, method="luminosity")
    else:
        gray = image.copy()

    mode_map = {
        "binary": cv2.THRESH_BINARY,
        "binary_inv": cv2.THRESH_BINARY_INV,
        "trunc": cv2.THRESH_TRUNC,
        "tozero": cv2.THRESH_TOZERO,
        "tozero_inv": cv2.THRESH_TOZERO_INV,
    }

    m = mode.lower()
    if m not in mode_map:
        raise ValueError(f"Mode thresholding '{mode}' tidak dikenali. Pilihan: {list(mode_map.keys())}")

    _, thresh_img = cv2.threshold(gray, threshold, max_val, mode_map[m])
    return thresh_img


def otsu_thresholding(image: np.ndarray, max_val: int = 255) -> tuple[np.ndarray, float]:
    """
    Pengambangan otomatis menggunakan Metode Otsu (Otsu's Thresholding).

    Prinsip dan Rumus Matematis:
    Mencari nilai ambang batas optimal T* yang memaksimalkan variansi antar-kelas (between-class variance sigma_B^2):
        sigma_B^2(T) = w0(T) * w1(T) * (mu0(T) - mu1(T))^2
    di mana:
        - w0(T) = sum_{i=0}^T p(i) : Probabilitas kemunculan kelas background
        - w1(T) = sum_{i=T+1}^{L-1} p(i) : Probabilitas kemunculan kelas foreground
        - mu0(T) = sum_{i=0}^T (i * p(i)) / w0(T) : Rata-rata intensitas kelas background
        - mu1(T) = sum_{i=T+1}^{L-1} (i * p(i)) / w1(T) : Rata-rata intensitas kelas foreground

    Nilai ambang optimal T* diperoleh dari:
        T* = argmax_{0 <= T < L-1} [ sigma_B^2(T) ]

    Return:
        (citra_hasil_biner, optimal_threshold)
    """
    if len(image.shape) == 3:
        gray = rgb_to_grayscale(image, method="luminosity")
    else:
        gray = image.copy()

    optimal_t, thresh_img = cv2.threshold(gray, 0, max_val, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh_img, optimal_t


def adaptive_thresholding(
    image: np.ndarray,
    max_val: int = 255,
    method: str = "mean",
    block_size: int = 11,
    c: int = 2,
) -> np.ndarray:
    """
    Adaptive Thresholding (Pengambangan Lokal / Adaptif).
    Nilai ambang dihitung secara independen untuk setiap lingkungan (window/block) piksel.

    Rumus Matematis:
        T(x, y) = Local_Mean(x, y) - C  (untuk method='mean')
        T(x, y) = Gaussian_Weighted_Mean(x, y) - C (untuk method='gaussian')

        g(x, y) = max_val   jika f(x, y) > T(x, y)
                  0         jika f(x, y) <= T(x, y)

    Parameter:
        - method: 'mean' (cv2.ADAPTIVE_THRESH_MEAN_C) atau 'gaussian' (cv2.ADAPTIVE_THRESH_GAUSSIAN_C)
        - block_size: Ukuran neighborhood piksel (harus bernilai ganjil, misal 3, 5, 11, 21)
        - c: Konstanta pengurang dari rata-rata lokal untuk fine-tuning sensitivitas ambang
    """
    if len(image.shape) == 3:
        gray = rgb_to_grayscale(image, method="luminosity")
    else:
        gray = image.copy()

    if block_size % 2 == 0:
        block_size += 1

    method_lower = method.lower()
    if method_lower == "mean":
        adaptive_method = cv2.ADAPTIVE_THRESH_MEAN_C
    elif method_lower == "gaussian":
        adaptive_method = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
    else:
        raise ValueError(f"Metode adaptive '{method}' tidak dikenali. Pilih 'mean' atau 'gaussian'")

    return cv2.adaptiveThreshold(
        gray,
        max_val,
        adaptive_method,
        cv2.THRESH_BINARY,
        block_size,
        c,
    )

