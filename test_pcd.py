"""
Unit Tests untuk pcd_operations.py
----------------------------------
Memverifikasi kebenaran matematis dan fungsionalitas seluruh operasi PCD.
"""

import unittest
import numpy as np
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
    hitung_histogram,
    ekualisasi_histogram,
    manual_thresholding,
    otsu_thresholding,
    adaptive_thresholding,
)


class TestPCDOperations(unittest.TestCase):
    def setUp(self):
        # Buat citra sintetis berukuran 50x50 kanal 3 (BGR)
        np.random.seed(42)
        self.color_img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        self.gray_img = np.random.randint(0, 256, (50, 50), dtype=np.uint8)

    def test_citra_negatif(self):
        # Test Grayscale: s + r == 255
        neg_gray = citra_negatif(self.gray_img)
        self.assertTrue(np.all(neg_gray.astype(int) + self.gray_img.astype(int) == 255))

        # Test Color
        neg_color = citra_negatif(self.color_img)
        self.assertTrue(np.all(neg_color.astype(int) + self.color_img.astype(int) == 255))

    def test_rgb_to_grayscale(self):
        gray_lum = rgb_to_grayscale(self.color_img, method="luminosity")
        self.assertEqual(gray_lum.shape, (50, 50))
        self.assertEqual(gray_lum.dtype, np.uint8)

        # Uji formula luminosity: 0.299*R + 0.587*G + 0.114*B (input adalah BGR)
        b = self.color_img[:, :, 0].astype(np.float32)
        g = self.color_img[:, :, 1].astype(np.float32)
        r = self.color_img[:, :, 2].astype(np.float32)
        expected = np.clip(0.299 * r + 0.587 * g + 0.114 * b, 0, 255).astype(np.uint8)
        np.testing.assert_array_equal(gray_lum, expected)

    def test_brightening(self):
        # Uji bias positif
        bright = brightening(self.gray_img, beta=50, alpha=1.0)
        self.assertTrue(np.all(bright >= self.gray_img))
        self.assertTrue(np.all(bright <= 255))

        # Uji bias negatif
        dark = brightening(self.gray_img, beta=-50, alpha=1.0)
        self.assertTrue(np.all(dark <= self.gray_img))
        self.assertTrue(np.all(dark >= 0))

    def test_gamma_correction(self):
        gamma_img = gamma_correction(self.gray_img, gamma=1.5)
        self.assertEqual(gamma_img.shape, self.gray_img.shape)
        self.assertEqual(gamma_img.dtype, np.uint8)

    def test_operasi_aritmetika(self):
        img1 = np.full((50, 50, 3), 100, dtype=np.uint8)
        img2 = np.full((50, 50, 3), 50, dtype=np.uint8)

        # Penjumlahan
        add = operasi_aritmetika(img1, img2, "penjumlahan")
        self.assertEqual(add[0, 0, 0], 150)

        # Pengurangan
        sub = operasi_aritmetika(img1, img2, "pengurangan")
        self.assertEqual(sub[0, 0, 0], 50)

        # Perkalian: (100 * 50) / 255 = 19.6 -> 19
        mul = operasi_aritmetika(img1, img2, "perkalian")
        self.assertEqual(mul[0, 0, 0], int((100 * 50) / 255))

        # Blending: 0.7 * 100 + 0.3 * 50 = 70 + 15 = 85
        blend = operasi_aritmetika(img1, img2, "blending", weight1=0.7, weight2=0.3)
        self.assertEqual(blend[0, 0, 0], 85)

    def test_geometri_flipping(self):
        # Horizontal flip
        flip_h = flipping(self.color_img, "horizontal")
        np.testing.assert_array_equal(flip_h, self.color_img[:, ::-1, :])

        # Vertical flip
        flip_v = flipping(self.color_img, "vertikal")
        np.testing.assert_array_equal(flip_v, self.color_img[::-1, :, :])

    def test_geometri_translasi_rotasi_zooming(self):
        trans = translasi(self.color_img, tx=10, ty=5)
        self.assertEqual(trans.shape, self.color_img.shape)

        rot = rotasi(self.color_img, angle=45)
        self.assertEqual(rot.shape, self.color_img.shape)

        zoom_in = zooming(self.color_img, factor=1.5, maintain_size=True)
        self.assertEqual(zoom_in.shape, self.color_img.shape)

        zoom_out = zooming(self.color_img, factor=0.5, maintain_size=True)
        self.assertEqual(zoom_out.shape, self.color_img.shape)

    def test_hitung_histogram(self):
        # Grayscale
        hist_gray = hitung_histogram(self.gray_img, normalize=False)
        self.assertEqual(len(hist_gray), 256)
        self.assertEqual(int(np.sum(hist_gray)), self.gray_img.size)

        hist_gray_norm = hitung_histogram(self.gray_img, normalize=True)
        self.assertAlmostEqual(float(np.sum(hist_gray_norm)), 1.0, places=5)

        # Color
        hist_color = hitung_histogram(self.color_img, normalize=False)
        self.assertIn("b", hist_color)
        self.assertIn("g", hist_color)
        self.assertIn("r", hist_color)
        self.assertEqual(int(np.sum(hist_color["r"])), self.color_img.shape[0] * self.color_img.shape[1])

    def test_ekualisasi_histogram(self):
        eq_gray = ekualisasi_histogram(self.gray_img)
        self.assertEqual(eq_gray.shape, self.gray_img.shape)
        self.assertEqual(eq_gray.dtype, np.uint8)

        eq_color = ekualisasi_histogram(self.color_img)
        self.assertEqual(eq_color.shape, self.color_img.shape)
        self.assertEqual(eq_color.dtype, np.uint8)

    def test_manual_thresholding(self):
        # Sample array: [50, 100, 150, 200]
        sample = np.array([[50, 100], [150, 200]], dtype=np.uint8)
        T = 120

        # Binary: > T -> 255, <= T -> 0
        bin_res = manual_thresholding(sample, threshold=T, mode="binary")
        expected_bin = np.array([[0, 0], [255, 255]], dtype=np.uint8)
        np.testing.assert_array_equal(bin_res, expected_bin)

        # Binary Inv: > T -> 0, <= T -> 255
        bin_inv_res = manual_thresholding(sample, threshold=T, mode="binary_inv")
        expected_bin_inv = np.array([[255, 255], [0, 0]], dtype=np.uint8)
        np.testing.assert_array_equal(bin_inv_res, expected_bin_inv)

        # Truncate: > T -> T, <= T -> f
        trunc_res = manual_thresholding(sample, threshold=T, mode="trunc")
        expected_trunc = np.array([[50, 100], [T, T]], dtype=np.uint8)
        np.testing.assert_array_equal(trunc_res, expected_trunc)

        # Tozero: > T -> f, <= T -> 0
        tozero_res = manual_thresholding(sample, threshold=T, mode="tozero")
        expected_tozero = np.array([[0, 0], [150, 200]], dtype=np.uint8)
        np.testing.assert_array_equal(tozero_res, expected_tozero)

    def test_otsu_thresholding(self):
        # Bimodal image: half 30, half 220
        bimodal = np.zeros((40, 40), dtype=np.uint8)
        bimodal[:20, :] = 30
        bimodal[20:, :] = 220

        thresh_otsu, opt_t = otsu_thresholding(bimodal)
        self.assertEqual(thresh_otsu.shape, (40, 40))
        # Optimal threshold should separate 30 and 220
        self.assertTrue(30 <= opt_t < 220)
        # Background pixels should be 0, foreground pixels 255
        self.assertTrue(np.all(thresh_otsu[:20, :] == 0))
        self.assertTrue(np.all(thresh_otsu[20:, :] == 255))

    def test_adaptive_thresholding(self):
        adapt_mean = adaptive_thresholding(self.gray_img, method="mean", block_size=11, c=2)
        self.assertEqual(adapt_mean.shape, self.gray_img.shape)
        # Check that output is binary (only 0 and 255)
        unique_vals = set(np.unique(adapt_mean))
        self.assertTrue(unique_vals.issubset({0, 255}))

        adapt_gauss = adaptive_thresholding(self.gray_img, method="gaussian", block_size=11, c=2)
        self.assertEqual(adapt_gauss.shape, self.gray_img.shape)
        unique_vals_g = set(np.unique(adapt_gauss))
        self.assertTrue(unique_vals_g.issubset({0, 255}))


if __name__ == "__main__":
    unittest.main()
