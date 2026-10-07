# 0001 — Backend Python sebagai satu sumber rumus

**Status:** Diterima

## Konteks

Tampilan web untuk demonstrasi Pengolahan Citra Digital harus menampilkan 15 Operasi PCD yang
sudah ada di `pcd_operations.py`, lengkap dengan kontrol parameternya.

Tersedia dua arah arsitektur:

1. **Frontend murni** — implementasi ulang rumus PCD dalam JavaScript, tanpa backend. Aplikasi
   bisa dijalankan dari berkas statis, tanpa proses server.
2. **Backend Python** — `pcd_operations.py` tetap menjadi satu-satunya implementasi rumus, dan
   web memanggilnya.

Kendala lingkungan: tidak ada kerangka kerja web yang terpasang. Python 3.14.2 tersedia dengan
`opencv-python`, `numpy`, `matplotlib`, dan `pillow`. Node v24 dan npm 11 juga tersedia.

## Keputusan

Rumus PCD tetap berada di `pcd_operations.py`. Web memanggil fungsi-fungsi itu lewat backend
Python (Flask). Setiap Operasi PCD di web melewati Rumus Kanonik; tidak ada implementasi rumus
kedua di sisi peramban.

## Konsekuensi

**Positif**

- Satu sumber kebenaran. Berkas di `output/` dan tampilan web tidak dapat menyimpang, karena
  keduanya memanggil kode yang sama.
- Seluruh 12 unit test yang sudah ada menguji kode yang benar-benar melayani web.
- Klaim "program bekerja" dapat dipertahankan di depan penguji: logika yang diuji adalah logika
  yang dipamerkan.

**Negatif**

- Aplikasi memerlukan proses server Python. Tidak bisa dibuka sebagai berkas statis, dan tidak
  bisa disebarkan ke hosting statis.
- Interaksi menuntut perjalanan pulang-pergi ke server. Karena itu citra diturunkan skalanya
  sebelum diproses, dan satu permintaan dapat meminta sebagian Kelompok saja.
- Bergantung pada Flask, satu dependensi yang harus dapat dipasang di mesin yang dipakai.

## Alternatif yang ditolak

**Rumus ditulis ulang dalam JavaScript.** Ditolak karena menghasilkan dua sumber kebenaran.
Setiap perubahan pada `pcd_operations.py` menuntut perubahan yang sama di sisi peramban, dan
selisih di antara keduanya hanya akan terlihat sebagai citra keluaran yang berbeda tipis —
kelas cacat yang sulit dideteksi mata. Pada konteks akademik, risiko ini tidak sebanding dengan
keuntungan menghilangkan proses server.
