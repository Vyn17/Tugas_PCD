# PCD — Pengolahan Citra Digital

Demonstrasi tujuh kelompok Operasi PCD dengan lima belas fungsi, tersedia dalam dua
antarmuka: CLI klasik (menghasilkan poster PNG) dan aplikasi web interaktif.

Seluruh perhitungan berasal dari satu sumber: `pcd_operations.py`.

---

## Menjalankan

### Aplikasi web (interaktif)

```
run_web.bat
```

Skrip ini membuat virtualenv `.venv` bila belum ada, memasang dependensi, lalu membuka
server. Setelah itu buka <http://127.0.0.1:5000>.

Menjalankan secara manual:

```
python -m pip install flask
python web/app.py
```

### Poster PNG (untuk laporan)

```
python scripts/generate_poster.py
```

Menghasilkan delapan berkas PNG di `output/`:

| Berkas | Isi |
|---|---|
| `1_citra_negatif.png` | Negatif berwarna dan grayscale |
| `2_grayscale.png` | Tiga metode konversi grayscale |
| `3_brightening.png` | Bias, linier, dan gamma correction |
| `4_aritmetika.png` | Lima operasi aritmetika dua citra |
| `5_geometri.png` | Translasi, rotasi, flipping, zooming |
| `6_histogram.png` | Histogram dan ekualisasi |
| `7_thresholding.png` | Manual, Otsu, dan adaptive |
| `summary_all.png` | Poster ringkasan sembilan panel |

### CLI

```
python run_pcd.py --category1 cat --index1 1 --category2 dog --index2 1
python run_pcd.py --interactive
```

Opsi: `--category1/-c1`, `--index1/-i1`, `--category2/-c2`, `--index2/-i2`.

### Test

```
python -m unittest test_pcd
```

Dua belas test memverifikasi rumus matematis setiap operasi.

---

## Dependensi

| Paket | Kegunaan |
|---|---|
| `opencv-python` | Operasi citra dan penyandian PNG |
| `numpy` | Aritmetika array |
| `matplotlib` | Hanya untuk poster di `scripts/generate_poster.py` |
| `flask` | Server aplikasi web |
| `playwright` | Hanya untuk verifikasi peramban (opsional) |

`pcd_operations.py` hanya membutuhkan `opencv-python` dan `numpy`.

---

## Struktur

```
PCD/
├── CONTEXT.md                  Glosarium istilah proyek
├── docs/adr/                   Catatan keputusan arsitektur
├── pcd_operations.py           Lima belas Operasi PCD — sumber rumus tunggal
├── main.py                     Pemuat citra dan utilitas bersama
├── test_pcd.py                 Dua belas unit test
├── run_pcd.py                  Antarmuka CLI
├── run_web.bat                 Peluncur aplikasi web
├── scripts/
│   └── generate_poster.py      Penghasil delapan poster PNG
├── web/
│   ├── app.py                  Server Flask dan endpoint API
│   ├── pcd_service.py          Lapisan render: Operasi PCD menjadi PNG/histogram
│   ├── templates/index.html    Halaman tunggal
│   └── static/                 Gaya dan logika antarmuka
├── dataset/                    5 kategori × 10 citra
└── output/                     Keluaran poster (dihasilkan, bukan disimpan)
```

---

## Aplikasi Web

### Kelompok yang tersedia

Ketujuh kelompok ditampilkan sekaligus. Setiap kelompok dapat dimatikan untuk mempercepat
pemuatan:

1. **Citra Negatif** — rumus `s = 255 - r`
2. **Grayscale** — empat metode yang dapat dipilih
3. **Brightening** — slider beta, alpha, dan gamma
4. **Aritmetika Dua Citra** — empat operasi dasar dan blending berbobot
5. **Operasi Geometri** — translasi, rotasi, flipping, zooming
6. **Histogram & Ekualisasi** — histogram digambar interaktif di peramban
7. **Thresholding** — manual (lima mode), Otsu, dan adaptive

### Sumber citra

Dua mode pada panel kontrol:

- **Dataset** — pilih kategori dan berkas. Lima kategori tersedia (cat, dog, fox, hamster,
  rabbit), masing-masing sepuluh citra.
- **Unggah** — berkas PNG atau JPG sendiri, maksimum 12 MB per berkas.

Operasi aritmetika memerlukan Citra 2. Kelompok lain cukup dengan Citra 1.

### Catatan Teknis

Program melakukan tiga penyesuaian otomatis. Ketiganya **selalu dilaporkan** sebagai Catatan
Teknis di atas hasil:

1. **Penurunan skala** — citra dengan sisi terpanjang di atas 720 piksel diperkecil agar
   tampilan tetap responsif.
2. **Penyejajaran dimensi** — pada operasi aritmetika, Citra 2 disesuaikan ukurannya dengan
   Citra 1.
3. **Pembulatan `block_size`** — thresholding adaptive menuntut ukuran blok bernilai ganjil.

### Unduhan

Tombol **unduh kelompok ini** pada setiap kelompok mengirim berkas ZIP berisi seluruh panel
PNG kelompok tersebut.

### Endpoint API

| Metode | Alamat | Kegunaan |
|---|---|---|
| `GET` | `/` | Halaman aplikasi |
| `GET` | `/api/dataset` | Daftar kategori dan citra |
| `GET` | `/api/image/<kategori>/<posisi>` | Citra sumber sebagai PNG |
| `POST` | `/api/process` | Memproses citra dari dataset |
| `POST` | `/api/process-upload` | Memproses citra yang diunggah |
| `POST` | `/api/download` | ZIP berisi panel hasil |

Contoh:

```json
POST /api/process
{
  "citra1": {"kategori": "cat", "index": 1},
  "citra2": {"kategori": "dog", "index": 1},
  "kelompok": ["negatif", "brightening"],
  "parameter": {"beta": -60, "alpha": 1.3, "gamma": 1.8}
}
```

Field `kelompok` bersifat opsional. Bila dihilangkan, ketujuh kelompok dirender. Hasil selalu
dikembalikan dalam urutan kanonik, bukan urutan permintaan.

Catatan: `posisi` adalah urutan berkas di dalam kategori, bukan nomor pada nama berkas.
Berkas diurutkan secara leksikografis, sehingga `fox_10.jpg` berada di posisi 2 sementara
`fox_2.jpg` berada di posisi 3. Antarmuka web menampilkan nama berkas, jadi perbedaan ini
tidak terlihat oleh pengguna.

---

## Operasi PCD

Lima belas fungsi di `pcd_operations.py`:

| Kelompok | Fungsi |
|---|---|
| Negatif | `citra_negatif` |
| Grayscale | `rgb_to_grayscale` (4 metode) |
| Brightening | `brightening`, `gamma_correction` |
| Aritmetika | `operasi_aritmetika` (5 operasi), `match_dimensions` |
| Geometri | `translasi`, `rotasi`, `flipping`, `zooming` |
| Histogram | `hitung_histogram`, `ekualisasi_histogram` |
| Thresholding | `manual_thresholding` (5 mode), `otsu_thresholding`, `adaptive_thresholding` |

Setiap fungsi memuat rumus matematisnya pada docstring.

---

## Catatan Pengembangan

**Satu sumber rumus.** Aplikasi web tidak mengimplementasikan ulang rumus apa pun. Ia
memanggil `pcd_operations.py` yang sama dengan yang diuji `test_pcd.py`. Keputusan ini
beserta alasannya ada di `docs/adr/0001-python-backend-sebagai-satu-sumber-rumus.md`.

**Gambar poster adalah keluaran.** Folder `output/` tidak disimpan bersama sumber. Jalankan
`python scripts/generate_poster.py` untuk menghasilkannya kembali.

**Verifikasi peramban.** Skrip `web/_verify_browser.py` menjalankan 43 pemeriksaan perilaku
lewat Playwright, mencakup penggantian citra, pergeseran slider, penyaringan kelompok,
unduhan ZIP, dan tata letak mobile:

```
python -m playwright install chromium
python web/_verify_browser.py
```
