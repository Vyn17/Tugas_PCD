# PCD — Glossary

Konteks tunggal. Istilah di bawah ini adalah bahasa kanonik proyek; jangan pakai sinonim
yang terdaftar sebagai "hindari".

## Operasi

**Operasi PCD** — satu transformasi citra tunggal, diimplementasikan sebagai satu fungsi di
`pcd_operations.py`. Operasi PCD murni: ia menerima array NumPy dan mengembalikan array NumPy,
tanpa I/O. Program ini mendefinisikan 15 Operasi PCD.

**Kelompok (Grup)** — pengelompokan Operasi PCD untuk keperluan tampilan, berjumlah **tujuh**.
Kelompok adalah konsep antarmuka; Operasi PCD adalah konsep matematis. Satu Kelompok dapat
memuat lebih dari satu Operasi PCD. Hindari: "kategori", "modul", "operasi" (saat yang dimaksud
Kelompok).

**Titik Transformasi** *(point transformation)* — Operasi PCD yang menghitung nilai keluaran
tiap piksel hanya dari nilai piksel masukan pada koordinat yang sama. Negatif, Grayscale,
Brightening, dan Thresholding adalah Titik Transformasi. Hindari: "operasi piksel".

**Transformasi Geometri** — Operasi PCD yang memindahkan posisi piksel. Translasi, rotasi,
flipping, dan zooming adalah Transformasi Geometri.

## Koreksi Senyap

**Koreksi Senyap** — setiap perubahan yang dilakukan kode terhadap masukan atau parameter
pengguna tanpa meminta persetujuan. Proyek ini mengenali tiga Koreksi Senyap: penyesuaian
dimensi pada operasi aritmetika, pembulatan `block_size` genap pada thresholding adaptif, dan
penurunan skala citra untuk keperluan tampilan.

**Koreksi Senyap tidak boleh diam.** Setiap Koreksi Senyap wajib dilaporkan ke pengguna sebagai
**Catatan Teknis**, baik sebagai ringkasan di atas hasil maupun sebagai penanda pada panel yang
terkena. Pelaporan ini adalah fitur, bukan pemberitahuan galat: pada konteks akademik, koreksi
inilah yang menunjukkan pemahaman bahwa operasi PCD bergantung pada ukuran citra.

## Presentasi

**Rumus Kanonik** — satu-satunya implementasi rumus PCD yang sah, yaitu yang ada di
`pcd_operations.py`. Seluruh antarmuka, termasuk web, wajib memanggil Rumus Kanonik. Hindari:
"logika inti", "engine".

**Nilai Default Demo** — parameter yang dipakai poster ringkasan dan CLI. Web tidak memakai
Nilai Default Demo ketika pengguna telah mengubah kontrol.

**Slider Palsu** — kontrol antarmuka yang tampak mengendalikan sesuatu yang sebenarnya tidak
terpengaruh olehnya. Slider Palsu dilarang; kontrol yang tidak relevan pada konteks berjalan
harus dinonaktifkan dengan keterangan, atau dipisahkan ke bloknya sendiri.

**Poster Ringkasan** — satu berkas PNG berisi grid semua Kelompok, tujuan penyajian akademik.
Poster Ringkasan adalah Keluaran, bukan Aset.
