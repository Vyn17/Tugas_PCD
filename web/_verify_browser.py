"""
Verifikasi peramban untuk aplikasi web PCD.

Menguji perilaku, bukan sekadar tampilan: mengubah citra, menggeser slider,
memilih kelompok, mengunduh ZIP, dan memeriksa Catatan Teknis.
"""

import io
import os
import sys
import zipfile

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5000"
GALAT = []


def tunggu_proses(halaman, jeda=700):
    """Menunggu respons /api/process berikutnya, lalu jeda agar DOM selesai."""
    with halaman.expect_response(lambda r: "/api/process" in r.url, timeout=90000):
        pass
    halaman.wait_for_timeout(jeda)


def cek(nama, kondisi, rincian=""):
    tanda = "LULUS" if kondisi else "GAGAL"
    print(f"  [{tanda}] {nama}" + (f" — {rincian}" if rincian else ""))
    if not kondisi:
        GALAT.append(nama)


def jalankan():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        konteks = browser.new_context(viewport={"width": 1440, "height": 900})
        halaman = konteks.new_page()

        pesan_konsol = []
        halaman.on("console", lambda m: pesan_konsol.append(f"{m.type}: {m.text}"))
        halaman.on("pageerror", lambda e: pesan_konsol.append(f"pageerror: {e}"))

        print("\n=== 1. PEMUATAN AWAL ===")
        halaman.goto(BASE, wait_until="networkidle", timeout=90000)
        halaman.wait_for_selector(".kelompok", timeout=90000)

        jumlah_kelompok = halaman.locator(".kelompok").count()
        cek("tujuh kelompok tampil", jumlah_kelompok == 7, f"ditemukan {jumlah_kelompok}")

        for nama in ["negatif", "grayscale", "brightening", "aritmetika",
                     "geometri", "histogram", "thresholding"]:
            cek(f"kelompok '{nama}' ada",
                halaman.locator(f'.kelompok[data-kelompok="{nama}"]').count() == 1)

        panel_awal = halaman.locator(".panel").count()
        cek("panel awal terender", panel_awal >= 30, f"{panel_awal} panel")

        kanvas = halaman.locator(".histogram canvas").count()
        cek("kanvas histogram digambar", kanvas == 3, f"{kanvas} kanvas")

        # Kanvas benar-benar terisi piksel, bukan kosong.
        terisi = halaman.evaluate(
            """() => {
                const c = document.querySelector('.histogram canvas');
                if (!c) return false;
                const ctx = c.getContext('2d');
                const d = ctx.getImageData(0, 0, c.width, c.height).data;
                let n = 0;
                for (let i = 3; i < d.length; i += 4) { if (d[i] > 0) n++; }
                return n > 500;
            }"""
        )
        cek("histogram punya piksel tergambar", terisi)

        cek("Catatan Teknis tampil (dimensi default berbeda)",
            halaman.locator("#catatan").is_visible())
        catatan_teks = halaman.locator("#catatan-daftar li").all_inner_texts()
        cek("catatan memuat koreksi penurunan skala",
            any("diturunkan skalanya" in t for t in catatan_teks),
            f"{len(catatan_teks)} catatan")
        cek("catatan memuat penyejajaran dimensi",
            any("disejajarkan" in t for t in catatan_teks))

        cek("badge status 'siap'", halaman.locator('#status-badge[data-status="siap"]').count() == 1)

        print("\n=== 2. GANTI CITRA 1 -> fox_5.jpg (1080x1709) ===")
        halaman.select_option("#kat1", "fox")
        halaman.wait_for_timeout(600)
        with halaman.expect_response(lambda r: "/api/process" in r.url, timeout=90000):
            # Pilih berdasarkan label berkas, bukan nomor posisi.
            halaman.select_option("#idx1", label="fox_5.jpg")
        halaman.wait_for_timeout(900)

        nama1 = halaman.locator("#r-nama1").inner_text()
        cek("ringkasan menampilkan fox_5.jpg", "fox_5" in nama1, nama1)
        ukuran1 = halaman.locator("#r-ukuran1").inner_text()
        cek("ukuran diproses <= 720px", "720" in ukuran1, ukuran1)

        print("\n=== 3. GESER SLIDER beta -> -120 (input lalu change) ===")
        panel_sebelum = halaman.locator('.kelompok[data-kelompok="brightening"] .panel__gambar').nth(1).get_attribute("src")

        # Fase input: label harus berubah tanpa memanggil server.
        halaman.evaluate(
            """() => {
                const s = document.getElementById('beta');
                s.value = -120;
                s.dispatchEvent(new Event('input', {bubbles: true}));
            }"""
        )
        halaman.wait_for_timeout(250)
        label_beta = halaman.locator("#v-beta").inner_text()
        cek("label slider beta diperbarui saat digeser", label_beta == "-120", label_beta)

        # Fase change: gambar harus benar-benar terender ulang.
        with halaman.expect_response(lambda r: "/api/process" in r.url, timeout=90000):
            halaman.evaluate(
                """() => {
                    const s = document.getElementById('beta');
                    s.dispatchEvent(new Event('change', {bubbles: true}));
                }"""
            )
        halaman.wait_for_timeout(900)

        judul_panel = halaman.locator('.kelompok[data-kelompok="brightening"] .panel__judul').nth(1).inner_text()
        cek("judul panel memuat beta baru", "-120" in judul_panel, judul_panel)

        panel_sesudah = halaman.locator('.kelompok[data-kelompok="brightening"] .panel__gambar').nth(1).get_attribute("src")
        cek("gambar brightening benar-benar berubah setelah slider dilepas",
            panel_sebelum != panel_sesudah)

        print("\n=== 4. SLIDER threshold -> 210, block_size -> 14, mode trunc ===")
        with halaman.expect_response(lambda r: "/api/process" in r.url, timeout=90000):
            halaman.evaluate(
                """() => {
                    document.getElementById('mode_threshold').value = 'trunc';
                    document.getElementById('mode_threshold').dispatchEvent(
                        new Event('change', {bubbles: true}));
                    const t = document.getElementById('threshold');
                    t.value = 210;
                    t.dispatchEvent(new Event('input', {bubbles: true}));
                    t.dispatchEvent(new Event('change', {bubbles: true}));
                    const b = document.getElementById('block_size');
                    b.value = 14;
                    b.dispatchEvent(new Event('input', {bubbles: true}));
                    b.dispatchEvent(new Event('change', {bubbles: true}));
                }"""
            )
        halaman.wait_for_timeout(1400)

        judul_th = halaman.locator('.kelompok[data-kelompok="thresholding"] .panel__judul').all_inner_texts()
        cek("mode trunc + T=210 terpakai", any("trunc" in j and "210" in j for j in judul_th), str(judul_th))
        cek("block_size 14 dibulatkan ke 15 di label", any("block 15" in j for j in judul_th), str(judul_th))

        catatan_th = halaman.locator('.kelompok[data-kelompok="thresholding"] .kelompok__catatan li').all_inner_texts()
        cek("catatan pembulatan block_size tampil",
            any("dibulatkan" in t for t in catatan_th), str(catatan_th))

        print("\n=== 5. SLIDER PALSU: bobot hanya pada sub-panel blending ===")
        with halaman.expect_response(lambda r: "/api/process" in r.url, timeout=90000):
            halaman.evaluate(
                """() => {
                    const w = document.getElementById('weight1');
                    w.value = 0.9;
                    w.dispatchEvent(new Event('input', {bubbles: true}));
                    w.dispatchEvent(new Event('change', {bubbles: true}));
                }"""
            )
        halaman.wait_for_timeout(1200)

        sub_judul = halaman.locator('.kelompok[data-kelompok="aritmetika"] .sub-kelompok__judul').all_inner_texts()
        cek("aritmetika terbagi dua sub-panel", len(sub_judul) == 2, str(sub_judul))
        cek("ada sub-panel blending terpisah",
            any("blending" in s.lower() for s in sub_judul), str(sub_judul))

        panel_dasar = halaman.locator('.kelompok[data-kelompok="aritmetika"] .sub-kelompok').nth(0)
        judul_dasar = panel_dasar.locator(".panel__judul").all_inner_texts()
        cek("sub-panel dasar tidak memuat slider bobot",
            not any("0.90" in j for j in judul_dasar), str(judul_dasar))

        panel_blend = halaman.locator('.kelompok[data-kelompok="aritmetika"] .sub-kelompok').nth(1)
        judul_blend = panel_blend.locator(".panel__judul").all_inner_texts()
        cek("sub-panel blending memuat bobot 0.90",
            any("0.90" in j for j in judul_blend), str(judul_blend))

        print("\n=== 6. CITRA 2 DIHAPUS -> aritmetika galat rapi, kelompok lain tetap ===")
        halaman.evaluate(
            """() => {
                // Meniru pilihan kosong dengan memaksa index di luar jangkauan.
                const s = document.getElementById('idx2');
                const opt = document.createElement('option');
                opt.value = '999';
                opt.textContent = 'kosong';
                s.appendChild(opt);
                s.value = '999';
                s.dispatchEvent(new Event('change', {bubbles: true}));
            }"""
        )
        halaman.wait_for_timeout(1200)
        galat_terlihat = halaman.locator("#galat").is_visible()
        cek("permintaan tidak sah memunculkan galat halaman", galat_terlihat)
        if galat_terlihat:
            teks = halaman.locator("#galat-teks").inner_text()
            cek("pesan galat Bahasa Indonesia jelas", "luar jangkauan" in teks, teks)

        # Kembalikan citra 2 yang sah untuk uji unduhan.
        with halaman.expect_response(lambda r: "/api/process" in r.url, timeout=90000):
            halaman.evaluate(
                """() => {
                    const s = document.getElementById('idx2');
                    s.value = s.options[0].value;
                    s.dispatchEvent(new Event('change', {bubbles: true}));
                }"""
            )
        halaman.wait_for_timeout(800)

        print("\n=== 7. UNDUH ZIP ===")
        with halaman.expect_download(timeout=90000) as info_unduh:
            halaman.locator(".kelompok__unduh").first.click()
        unduhan = info_unduh.value
        jalur = unduhan.path()
        ukuran = os.path.getsize(jalur)
        cek("berkas terunduh", ukuran > 1000, f"{ukuran} byte")
        cek("nama berkas .zip", unduhan.suggested_filename.endswith(".zip"),
            unduhan.suggested_filename)
        with zipfile.ZipFile(jalur) as zf:
            isi = zf.namelist()
        cek("zip memuat berkas PNG", len(isi) >= 1 and all(n.endswith(".png") for n in isi),
            f"{len(isi)} berkas: {isi[:2]}")

        print("\n=== 8. UNCHECK KELOMPOK -> panel berkurang ===")
        with halaman.expect_response(lambda r: "/api/process" in r.url, timeout=90000):
            halaman.locator('.kelompok-centang[value="geometri"]').uncheck()
        halaman.wait_for_timeout(700)
        with halaman.expect_response(lambda r: "/api/process" in r.url, timeout=90000):
            halaman.locator('.kelompok-centang[value="thresholding"]').uncheck()
        halaman.wait_for_timeout(700)
        cek("geometri hilang dari hasil",
            halaman.locator('.kelompok[data-kelompok="geometri"]').count() == 0)
        cek("thresholding hilang dari hasil",
            halaman.locator('.kelompok[data-kelompok="thresholding"]').count() == 0)
        cek("kelompok tersisa lima", halaman.locator(".kelompok").count() == 5,
            str(halaman.locator(".kelompok").count()))

        print("\n=== 9. TOMBOL NILAI DEFAULT ===")
        with halaman.expect_response(lambda r: "/api/process" in r.url, timeout=90000):
            halaman.click("#tombol-reset")
        halaman.wait_for_timeout(700)
        cek("beta kembali 50", halaman.locator("#v-beta").inner_text() == "50",
            halaman.locator("#v-beta").inner_text())
        cek("tujuh kelompok kembali", halaman.locator(".kelompok").count() == 7,
            str(halaman.locator(".kelompok").count()))
        cek("catatan teknis tetap muncul",
            halaman.locator("#catatan").is_visible())

        print("\n=== 10. TAB UNGGAH -> kembali ke DATASET ===")
        halaman.click('.tab__tombol[data-tab="unggah"]')
        halaman.wait_for_timeout(1200)
        cek("form unggah tampil", halaman.locator("#berkas1").is_visible())
        with halaman.expect_response(lambda r: "/api/process" in r.url, timeout=90000):
            halaman.click('.tab__tombol[data-tab="dataset"]')
        halaman.wait_for_timeout(700)
        cek("kelompok kembali tampil setelah balik ke dataset",
            halaman.locator(".kelompok").count() == 7,
            str(halaman.locator(".kelompok").count()))

        halaman.screenshot(path="web/_bukti_desktop.png", full_page=False)

        print("\n=== 11. MOBILE 390x844 ===")
        halaman.set_viewport_size({"width": 390, "height": 844})
        halaman.wait_for_timeout(900)

        posisi_kolom = halaman.evaluate(
            """() => {
                const k = document.getElementById('kontrol').getBoundingClientRect();
                const h = document.getElementById('hasil').getBoundingClientRect();
                return {kontrolLebar: Math.round(k.width), hasilLebar: Math.round(h.width),
                        kontrolAtas: Math.round(k.top), hasilAtas: Math.round(h.top)};
            }"""
        )
        cek("layout mobile satu kolom (kontrol di atas hasil)",
            posisi_kolom["hasilAtas"] >= posisi_kolom["kontrolAtas"],
            str(posisi_kolom))
        cek("kontrol selebar layar mobile",
            posisi_kolom["kontrolLebar"] <= 400, str(posisi_kolom["kontrolLebar"]))

        meluber = halaman.evaluate(
            """() => {
                const d = document.documentElement;
                return d.scrollWidth - d.clientWidth;
            }"""
        )
        cek("tidak ada luapan horizontal", meluber <= 2, f"kelebihan {meluber}px")

        halaman.screenshot(path="web/_bukti_mobile.png", full_page=False)

        # Panel tetap terender di mobile
        cek("panel tetap terender di mobile", halaman.locator(".panel").count() >= 30,
            str(halaman.locator(".panel").count()))

        print("\n=== 12. KONSOL PERAMBAN ===")
        # Uji nomor 6 sengaja memicu HTTP 400, sehingga satu galat konsol wajar muncul.
        # Galat lain (mis. ReferenceError, TypeError) tetap dianggap kegagalan.
        galat_konsol = [m for m in pesan_konsol if m.startswith("pageerror")]
        cek("tidak ada galat JavaScript (pageerror)", len(galat_konsol) == 0, str(galat_konsol[:5]))

        galat_jaringan = [m for m in pesan_konsol if m.startswith("error")]
        cek("galat jaringan hanya dari uji 400 yang disengaja",
            len(galat_jaringan) <= 1, str(galat_jaringan[:3]))

        browser.close()

    print("\n" + "=" * 62)
    if GALAT:
        print(f"HASIL: {len(GALAT)} PEMERIKSAAN GAGAL")
        for g in GALAT:
            print("   -", g)
    else:
        print("HASIL: SELURUH PEMERIKSAAN LULUS")
    print("=" * 62)
    return 1 if GALAT else 0


if __name__ == "__main__":
    sys.exit(jalankan())
