"""
Aplikasi Web Pengolahan Citra Digital (PCD)
-------------------------------------------
Tampilan web untuk 15 Operasi PCD. Seluruh perhitungan diteruskan ke Rumus
Kanonik di pcd_operations.py melalui web/pcd_service.py.

Jalankan:  python web/app.py     lalu buka http://127.0.0.1:5000
"""

import io
import json
import os
import sys
import zipfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request, send_file

from main import DATASET_DIR, list_dataset, load_dataset_image
import pcd_service
from pcd_service import KELOMPOK_URUTAN, LABEL_KELOMPOK, METODE_GRAYSCALE, MODE_FLIP, MODE_THRESHOLD, OPERASI_ARITMETIKA

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024  # 12 MB per unggahan


# ==============================================================================
# PEMUATAN CITRA
# ==============================================================================
def _baca_unggahan(field: str) -> np.ndarray | None:
    """Membaca citra yang diunggah dari form, bila ada."""
    berkas = request.files.get(field)
    if berkas is None or not berkas.filename:
        return None

    data = np.frombuffer(berkas.read(), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(
            f"Berkas '{berkas.filename}' tidak dapat dibaca sebagai citra. "
            f"Gunakan format JPG atau PNG."
        )
    return img


def _muat_citra(sumber: dict, unggahan: np.ndarray | None, label: str) -> tuple[np.ndarray | None, str | None]:
    """
    Memuat satu citra dari unggahan bila ada, atau dari dataset.

    Mengembalikan (citra, nama) atau (None, None) bila tidak ada sumber.
    """
    if unggahan is not None:
        return unggahan, f"{label} (unggahan)"

    kategori = sumber.get("kategori")
    if not kategori:
        return None, None

    index = int(sumber.get("index", 1))
    img, nama = load_dataset_image(kategori, index)
    return img, nama


def _prm_dari_request(data: dict) -> dict:
    """Menyusun kamus parameter dari permintaan."""
    return {
        "metode_grayscale": data.get("metode_grayscale", METODE_GRAYSCALE),
        "beta": data.get("beta", 50),
        "alpha": data.get("alpha", 1.0),
        "gamma": data.get("gamma", 1.5),
        "weight1": data.get("weight1", 0.5),
        "weight2": data.get("weight2", 0.5),
        "tx": data.get("tx", 50),
        "ty": data.get("ty", 30),
        "sudut": data.get("sudut", 45.0),
        "skala": data.get("skala", 1.0),
        "mode_flip": data.get("mode_flip", "horizontal"),
        "faktor_zoom": data.get("faktor_zoom", 1.5),
        "jaga_ukuran": data.get("jaga_ukuran", True),
        "threshold": data.get("threshold", 127),
        "max_val": data.get("max_val", 255),
        "mode_threshold": data.get("mode_threshold", "binary"),
        "metode_adaptif": data.get("metode_adaptif", "mean"),
        "block_size": data.get("block_size", 15),
        "c": data.get("c", 3),
    }


# ==============================================================================
# ENDPOINT
# ==============================================================================
@app.route("/")
def index():
    return render_template(
        "index.html",
        daftar_dataset=list_dataset(),
        kelompok=[{"id": k, "label": LABEL_KELOMPOK[k]} for k in KELOMPOK_URUTAN],
        metode_grayscale=METODE_GRAYSCALE,
        mode_flip=MODE_FLIP,
        mode_threshold=MODE_THRESHOLD,
        operasi_aritmetika=OPERASI_ARITMETIKA,
    )


@app.route("/api/dataset")
def api_dataset():
    """Daftar kategori dan citra yang tersedia di dataset."""
    return jsonify(list_dataset())


@app.route("/api/image/<kategori>/<int:index>")
def api_image(kategori: str, index: int):
    """Mengirim citra sumber dari dataset untuk pratinjau."""
    try:
        img, nama = load_dataset_image(kategori, index)
    except ValueError as exc:
        return jsonify({"galat": str(exc)}), 404

    from pcd_service import _png_bytes

    return send_file(
        io.BytesIO(_png_bytes(img)),
        mimetype="image/png",
        download_name=nama,
    )


@app.route("/api/process", methods=["POST"])
def api_process():
    """
    Memproses citra untuk sekumpulan Kelompok.

    Menerima JSON:
        {
          "citra1": {"kategori": "cat", "index": 1},
          "citra2": {"kategori": "dog", "index": 1},
          "kelompok": ["negatif", "grayscale"],   # opsional
          "parameter": {...}
        }
    """
    try:
        data = request.get_json(silent=True) or {}
        prm = _prm_dari_request(data.get("parameter", {}))

        citra1_data = data.get("citra1", {}) or {}
        citra2_data = data.get("citra2", {}) or {}

        img1, nama1 = _muat_citra(citra1_data, None, "Citra 1")
        if img1 is None:
            return jsonify({"galat": "Citra 1 belum dipilih."}), 400

        img2, nama2 = _muat_citra(citra2_data, None, "Citra 2")

        hasil = pcd_service.proses(
            img1,
            img2,
            prm,
            kelompok_diminta=data.get("kelompok"),
        )
        hasil["nama_citra1"] = nama1
        hasil["nama_citra2"] = nama2
        return jsonify(hasil)

    except ValueError as exc:
        return jsonify({"galat": str(exc)}), 400
    except Exception as exc:  # noqa: BLE001
        app.logger.exception("Kesalahan saat memproses citra")
        return jsonify({"galat": f"Terjadi kesalahan tak terduga: {exc}"}), 500


@app.route("/api/process-upload", methods=["POST"])
def api_process_upload():
    """
    Sama seperti /api/process, tetapi menerima berkas citra yang diunggah.

    Menggunakan multipart/form-data dengan field 'citra1_file' dan opsional
    'citra2_file', plus field 'payload' berisi JSON parameter.
    """
    try:
        payload = json.loads(request.form.get("payload", "{}"))
        prm = _prm_dari_request(payload.get("parameter", {}))

        unggah1 = _baca_unggahan("citra1_file")
        unggah2 = _baca_unggahan("citra2_file")

        citra1_data = payload.get("citra1", {}) or {}
        citra2_data = payload.get("citra2", {}) or {}

        img1, nama1 = _muat_citra(citra1_data, unggah1, "Citra 1")
        if img1 is None:
            return jsonify({"galat": "Citra 1 belum dipilih atau diunggah."}), 400

        img2, nama2 = _muat_citra(citra2_data, unggah2, "Citra 2")

        hasil = pcd_service.proses(
            img1,
            img2,
            prm,
            kelompok_diminta=payload.get("kelompok"),
        )
        hasil["nama_citra1"] = nama1
        hasil["nama_citra2"] = nama2
        return jsonify(hasil)

    except ValueError as exc:
        return jsonify({"galat": str(exc)}), 400
    except Exception as exc:  # noqa: BLE001
        app.logger.exception("Kesalahan saat memproses citra unggahan")
        return jsonify({"galat": f"Terjadi kesalahan tak terduga: {exc}"}), 500


@app.route("/api/download", methods=["POST"])
def api_download():
    """
    Mengirim berkas ZIP berisi seluruh panel gambar dari hasil yang dikirim.

    Menerima JSON hasil /api/process, sehingga tidak perlu menghitung ulang.
    """
    import base64

    data = request.get_json(silent=True) or {}
    kelompok = data.get("kelompok", [])
    if not kelompok:
        return jsonify({"galat": "Tidak ada hasil untuk diunduh."}), 400

    buffer = io.BytesIO()
    jumlah = 0

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for blok in kelompok:
            judul = blok.get("judul", blok.get("kelompok", "kelompok"))
            if blok.get("galat"):
                continue

            daftar_panel = []
            if blok.get("sub_kelompok"):
                for sub in blok["sub_kelompok"]:
                    for panel in sub.get("panel", []):
                        daftar_panel.append((f"{sub['judul']}/{panel['judul']}", panel))
            else:
                for panel in blok.get("panel", []):
                    daftar_panel.append((panel["judul"], panel))

            for nomor, (nama_panel, panel) in enumerate(daftar_panel, start=1):
                uri = panel.get("gambar", "")
                if "," not in uri:
                    continue
                mentah = base64.b64decode(uri.split(",", 1)[1])
                aman = "".join(
                    ch if ch.isalnum() or ch in " -_" else "_" for ch in nama_panel
                ).strip()
                zf.writestr(f"{judul}/{nomor:02d}_{aman}.png", mentah)
                jumlah += 1

        if jumlah == 0:
            return jsonify({"galat": "Tidak ada panel gambar yang dapat diunduh."}), 400

    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="hasil_pcd.zip",
    )


if __name__ == "__main__":
    print("=" * 65)
    print("   APLIKASI WEB PENGOLAHAN CITRA DIGITAL (PCD)")
    print("=" * 65)
    print(f"   Dataset : {DATASET_DIR}")
    print("   Buka    : http://127.0.0.1:5000")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5000, debug=False)
