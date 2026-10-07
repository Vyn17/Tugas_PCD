/* ==========================================================================
   Laboratorium PCD — logika antarmuka
   Memanggil /api/process dan menggambar hasil. Tidak ada rumus PCD di sini:
   seluruh perhitungan berasal dari backend Python.
   ========================================================================== */

(function () {
  "use strict";

  var WARNA = { r: "#c0392b", g: "#1f6f54", b: "#2a5db0", tunggal: "#5f5e58" };

  var el = {
    statusBadge: document.getElementById("status-badge"),
    statusTeks: document.getElementById("status-teks"),
    kat1: document.getElementById("kat1"),
    idx1: document.getElementById("idx1"),
    info1: document.getElementById("info1"),
    kat2: document.getElementById("kat2"),
    idx2: document.getElementById("idx2"),
    info2: document.getElementById("info2"),
    berkas1: document.getElementById("berkas1"),
    berkas2: document.getElementById("berkas2"),
    kelompokDaftar: document.getElementById("kelompok-daftar"),
    wadah: document.getElementById("kelompok-wadah"),
    catatan: document.getElementById("catatan"),
    catatanDaftar: document.getElementById("catatan-daftar"),
    catatanLipat: document.getElementById("catatan-lipat"),
    galat: document.getElementById("galat"),
    galatTeks: document.getElementById("galat-teks"),
    ringkas: document.getElementById("ringkas"),
    rNama1: document.getElementById("r-nama1"),
    rUkuran1: document.getElementById("r-ukuran1"),
    rNama2: document.getElementById("r-nama2"),
    rUkuran2: document.getElementById("r-ukuran2"),
    rWaktu: document.getElementById("r-waktu"),
    kakiTeks: document.getElementById("kaki-teks"),
    tombolProses: document.getElementById("tombol-proses"),
    tombolReset: document.getElementById("tombol-reset"),
    tombolLipat: document.getElementById("tombol-lipat"),
    kontrolIsi: document.getElementById("kontrol-isi"),
  };

  var PENANDA_SLIDER = {
    beta: function (v) { return v; },
    alpha: function (v) { return Number(v).toFixed(2); },
    gamma: function (v) { return Number(v).toFixed(2); },
    weight1: function (v) { return Number(v).toFixed(2); },
    weight2: function (v) { return Number(v).toFixed(2); },
    tx: function (v) { return v; },
    ty: function (v) { return v; },
    sudut: function (v) { return v; },
    skala: function (v) { return Number(v).toFixed(2); },
    faktor_zoom: function (v) { return Number(v).toFixed(2); },
    threshold: function (v) { return v; },
    block_size: function (v) { return v; },
    c: function (v) { return v; },
    max_val: function (v) { return v; },
  };

  var LABEL_INDEKS = {
    beta: "v-beta", alpha: "v-alpha", gamma: "v-gamma",
    weight1: "v-weight1", weight2: "v-weight2",
    tx: "v-tx", ty: "v-ty", sudut: "v-sudut", skala: "v-skala",
    faktor_zoom: "v-zoom", threshold: "v-threshold",
    block_size: "v-block", c: "v-c", max_val: "v-maxval",
  };

  var penghitungPermintaan = 0;
  var hasilTerakhir = null;

  /* ------------------------------ Utilitas ------------------------------ */

  function setStatus(kondisi, teks) {
    el.statusBadge.dataset.status = kondisi;
    el.statusTeks.textContent = teks;
  }

  function isiPilihanBerkas(selectKategori, selectIndeks, elemenInfo, indeksAwal) {
    var kategori = selectKategori.value;
    var daftar = window.PCD.daftarDataset[kategori] || [];

    selectIndeks.innerHTML = "";
    daftar.forEach(function (berkas, posisi) {
      var opt = document.createElement("option");
      opt.value = berkas.posisi;
      opt.textContent = berkas.filename;
      if (posisi === indeksAwal - 1) { opt.selected = true; }
      selectIndeks.appendChild(opt);
    });

    perbaruiInfo(selectIndeks, elemenInfo, kategori);
  }

  function perbaruiInfo(selectIndeks, elemenInfo, kategori) {
    var daftar = window.PCD.daftarDataset[kategori] || [];
    var dipilih = null;
    for (var i = 0; i < daftar.length; i++) {
      if (String(daftar[i].posisi) === String(selectIndeks.value)) { dipilih = daftar[i]; break; }
    }
    elemenInfo.textContent = dipilih
      ? dipilih.filename + " — " + dipilih.width + " × " + dipilih.height + " px"
      : "";
  }

  function nilaiSlider() {
    var p = {};
    Object.keys(PENANDA_SLIDER).forEach(function (id) {
      var simpul = document.getElementById(id);
      if (simpul) { p[id] = parseFloat(simpul.value); }
    });

    var flip = document.getElementById("mode_flip");
    if (flip) { p.mode_flip = flip.value; }

    var adaptif = document.getElementById("metode_adaptif");
    if (adaptif) { p.metode_adaptif = adaptif.value; }

    var modeT = document.getElementById("mode_threshold");
    if (modeT) { p.mode_threshold = modeT.value; }

    var jaga = document.getElementById("jaga_ukuran");
    if (jaga) { p.jaga_ukuran = jaga.checked; }

    var metode = [];
    document.querySelectorAll(".metode-gray:checked").forEach(function (c) { metode.push(c.value); });
    p.metode_grayscale = metode.length ? metode : ["luminosity"];

    return p;
  }

  function kelompokTerpilih() {
    var daftar = [];
    document.querySelectorAll(".kelompok-centang:checked").forEach(function (c) { daftar.push(c.value); });
    return daftar;
  }

  function sumberCitra1() {
    return { kategori: el.kat1.value, index: parseInt(el.idx1.value, 10) || 1 };
  }

  function sumberCitra2() {
    return { kategori: el.kat2.value, index: parseInt(el.idx2.value, 10) || 1 };
  }

  /* -------------------------------- Galat ------------------------------- */

  function tampilkanGalat(pesan) {
    el.galat.hidden = false;
    el.galatTeks.textContent = " " + pesan;
    setStatus("galat", "galat");
  }

  function sembunyikanGalat() {
    el.galat.hidden = true;
  }

  function tampilkanKerangka() {
    el.wadah.innerHTML = "";
    var kerangka = document.createElement("div");
    kerangka.className = "kerangka";
    kerangka.id = "kerangka";
    for (var i = 0; i < 8; i++) {
      var baris = document.createElement("div");
      baris.className = "kerangka__baris";
      kerangka.appendChild(baris);
    }
    el.wadah.appendChild(kerangka);
  }

  /* ------------------------------ Histogram ----------------------------- */

  function gambarHistogram(kanvas, muatan) {
    var rasio = window.devicePixelRatio || 1;
    var lebarCSS = kanvas.clientWidth || 260;
    var tinggiCSS = 120;
    kanvas.width = lebarCSS * rasio;
    kanvas.height = tinggiCSS * rasio;

    var ctx = kanvas.getContext("2d");
    ctx.setTransform(rasio, 0, 0, rasio, 0, 0);
    ctx.clearRect(0, 0, lebarCSS, tinggiCSS);

    var kiri = 30, kanan = 6, atas = 6, bawah = 16;
    var lebarPlot = lebarCSS - kiri - kanan;
    var tinggiPlot = tinggiCSS - atas - bawah;

    function rangkaian(nilai) {
      return { nilai: nilai, maks: Math.max.apply(null, nilai) || 1 };
    }

    var rangkaianData = muatan.tipe === "rgb"
      ? [rangkaian(muatan.r), rangkaian(muatan.g), rangkaian(muatan.b)]
      : [rangkaian(muatan.nilai)];

    var maks = 0;
    rangkaianData.forEach(function (r) { if (r.maks > maks) { maks = r.maks; } });

    // Sumbu
    ctx.strokeStyle = "#dcdad1";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(kiri, atas);
    ctx.lineTo(kiri, atas + tinggiPlot);
    ctx.lineTo(kiri + lebarPlot, atas + tinggiPlot);
    ctx.stroke();

    // Label sumbu
    ctx.fillStyle = "#8d8c84";
    ctx.font = "9px ui-monospace, monospace";
    ctx.textAlign = "left";
    ctx.fillText("0", 20, atas + tinggiPlot + 4);
    ctx.textAlign = "right";
    ctx.fillText("255", kiri + lebarPlot, atas + tinggiPlot + 12);
    ctx.textAlign = "left";
    ctx.fillText(formatRingkas(maks), 2, atas + 8);

    function formatRingkas(n) {
      if (n >= 1e6) { return (n / 1e6).toFixed(1) + "M"; }
      if (n >= 1e3) { return (n / 1e3).toFixed(0) + "k"; }
      return String(Math.round(n));
    }

    function plot(nilai, warna) {
      ctx.beginPath();
      ctx.strokeStyle = warna;
      ctx.lineWidth = 1.2;
      var langkah = lebarPlot / 256;
      for (var i = 0; i < 256; i++) {
        var x = kiri + i * langkah;
        var y = atas + tinggiPlot - (nilai[i] / maks) * tinggiPlot;
        if (i === 0) { ctx.moveTo(x, y); } else { ctx.lineTo(x, y); }
      }
      ctx.stroke();
    }

    var warna = muatan.tipe === "rgb"
      ? [WARNA.r, WARNA.g, WARNA.b]
      : [WARNA.tunggal];

    rangkaianData.forEach(function (r, i) { plot(r.nilai, warna[i]); });
  }

  function blokHistogram(histogram) {
    if (!histogram) { return null; }

    var bagian = document.createElement("div");
    bagian.className = "histogram";

    var judul = document.createElement("div");
    judul.className = "histogram__kepala";
    judul.textContent = "Histogram";
    bagian.appendChild(judul);

    var kisi = document.createElement("div");
    kisi.className = "histogram__kisi";

    var entri = [
      ["Histogram Grayscale Asli (h(rk) = nk)", histogram.grayscale_asli],
      ["Histogram Setelah Ekualisasi", histogram.grayscale_ekualisasi],
      ["Histogram Kanal Warna RGB", histogram.rgb],
    ];

    entri.forEach(function (pasangan) {
      if (!pasangan[1]) { return; }

      var kotak = document.createElement("div");
      kotak.className = "histogram__kotak";

      var label = document.createElement("div");
      label.className = "histogram__judul";
      label.textContent = pasangan[0];
      kotak.appendChild(label);

      var kanvas = document.createElement("canvas");
      kanvas._muatan = pasangan[1];
      kotak.appendChild(kanvas);

      if (pasangan[1].tipe === "rgb") {
        var legenda = document.createElement("div");
        legenda.className = "legenda";
        legenda.innerHTML =
          '<span><i style="background:' + WARNA.r + '"></i>R</span>' +
          '<span><i style="background:' + WARNA.g + '"></i>G</span>' +
          '<span><i style="background:' + WARNA.b + '"></i>B</span>';
        kotak.appendChild(legenda);
      }

      kisi.appendChild(kotak);

      // Digambar setelah tersambung ke DOM agar clientWidth terukur.
      requestAnimationFrame(function () { gambarHistogram(kanvas, pasangan[1]); });
    });

    bagian.appendChild(kisi);
    return bagian;
  }

  /* -------------------------------- Panel ------------------------------- */

  function panelSimpul(panel) {
    var kotak = document.createElement("figure");
    kotak.className = "panel";
    kotak.style.margin = "0";

    var gambar = document.createElement("img");
    gambar.className = "panel__gambar";
    gambar.src = panel.gambar;
    gambar.alt = panel.judul;
    gambar.loading = "lazy";
    kotak.appendChild(gambar);

    var kaki = document.createElement("figcaption");
    kaki.className = "panel__kaki";

    var judul = document.createElement("span");
    judul.className = "panel__judul";
    judul.textContent = panel.judul;
    kaki.appendChild(judul);

    if (panel.catatan) {
      var tanda = document.createElement("span");
      tanda.className = "panel__tanda";
      tanda.textContent = "catatan";
      tanda.title = panel.catatan;
      kaki.appendChild(tanda);
    }

    kotak.appendChild(kaki);
    return kotak;
  }

  function kisiPanel(daftarPanel) {
    var kisi = document.createElement("div");
    kisi.className = "kisi";
    daftarPanel.forEach(function (p) { kisi.appendChild(panelSimpul(p)); });
    return kisi;
  }

  /* ------------------------------ Rendering ----------------------------- */

  function gambarHasil(hasil, nama1, nama2, detik) {
    el.wadah.innerHTML = "";

    el.rNama1.textContent = nama1 || "—";
    el.rUkuran1.textContent = hasil.ukuran_citra1
      ? hasil.ukuran_citra1.width + " × " + hasil.ukuran_citra1.height + " px" : "—";
    el.rNama2.textContent = nama2 || "—";
    el.rUkuran2.textContent = hasil.ukuran_citra2
      ? hasil.ukuran_citra2.width + " × " + hasil.ukuran_citra2.height + " px" : "—";
    el.rWaktu.textContent = detik.toFixed(2) + " detik";
    el.ringkas.hidden = false;

    // Catatan teknis
    if (hasil.koreksi_senyap && hasil.koreksi_senyap.length) {
      el.catatan.hidden = false;
      el.catatanDaftar.innerHTML = "";
      hasil.koreksi_senyap.forEach(function (k) {
        var li = document.createElement("li");
        li.textContent = k.pesan;
        el.catatanDaftar.appendChild(li);
      });
    } else {
      el.catatan.hidden = true;
    }

    var totalPanel = 0;

    hasil.kelompok.forEach(function (blok) {
      var bagian = document.createElement("section");
      bagian.className = "kelompok";
      bagian.dataset.kelompok = blok.kelompok;

      var kepala = document.createElement("div");
      kepala.className = "kelompok__kepala";

      var judul = document.createElement("h2");
      judul.className = "kelompok__judul";
      judul.textContent = blok.judul || blok.kelompok;
      kepala.appendChild(judul);

      if (blok.rumus) {
        var rumus = document.createElement("code");
        rumus.className = "kelompok__rumus";
        rumus.textContent = blok.rumus;
        kepala.appendChild(rumus);
      }

      var unduh = document.createElement("button");
      unduh.type = "button";
      unduh.className = "tombol tombol--hantu kelompok__unduh";
      unduh.textContent = "unduh kelompok ini";
      unduh.dataset.kelompok = blok.kelompok;
      kepala.appendChild(unduh);

      bagian.appendChild(kepala);

      if (blok.catatan_teknis && blok.catatan_teknis.length) {
        var ul = document.createElement("ul");
        ul.className = "kelompok__catatan";
        blok.catatan_teknis.forEach(function (t) {
          var li = document.createElement("li");
          li.textContent = t;
          ul.appendChild(li);
        });
        bagian.appendChild(ul);
      }

      if (blok.galat) {
        var galat = document.createElement("div");
        galat.className = "kelompok__galat";
        galat.textContent = blok.galat;
        bagian.appendChild(galat);
        el.wadah.appendChild(bagian);
        return;
      }

      if (blok.sub_kelompok) {
        blok.sub_kelompok.forEach(function (sub) {
          var subBagian = document.createElement("div");
          subBagian.className = "sub-kelompok";

          var subKepala = document.createElement("div");
          subKepala.className = "sub-kelompok__kepala";

          var subJudul = document.createElement("span");
          subJudul.className = "sub-kelompok__judul";
          subJudul.textContent = sub.judul;
          subKepala.appendChild(subJudul);

          if (sub.keterangan) {
            var ket = document.createElement("span");
            ket.className = "sub-kelompok__ket";
            ket.textContent = sub.keterangan;
            subKepala.appendChild(ket);
          }

          subBagian.appendChild(subKepala);
          subBagian.appendChild(kisiPanel(sub.panel));
          bagian.appendChild(subBagian);

          totalPanel += sub.panel.length;
        });
      } else {
        bagian.appendChild(kisiPanel(blok.panel || []));
        totalPanel += (blok.panel || []).length;
      }

      if (blok.histogram) {
        var blokHist = blokHistogram(blok.histogram);
        if (blokHist) { bagian.appendChild(blokHist); }
      }

      el.wadah.appendChild(bagian);
    });

    el.kakiTeks.textContent =
      totalPanel + " panel dirender dari " + hasil.kelompok.length + " kelompok.";

    if (hasil.ringkasan_koreksi) {
      el.kakiTeks.textContent += " Beberapa koreksi diterapkan — lihat Catatan Teknis.";
    }
  }

  /* ------------------------------ Permintaan ---------------------------- */

  function modeUnggah() {
    var tabUnggah = document.querySelector('.tab__tombol[data-tab="unggah"]');
    return tabUnggah && tabUnggah.classList.contains("tab__tombol--aktif");
  }

  function kirimPermintaan(kelompokDiminta) {
    var paket = {
      citra1: sumberCitra1(),
      citra2: sumberCitra2(),
      parameter: nilaiSlider(),
      kelompok: kelompokDiminta || null,
    };

    var unggahan1 = el.berkas1.files[0];
    var unggahan2 = el.berkas2.files[0];
    var pakaiUnggahan = modeUnggah() && unggahan1;

    var opsi;
    var alamat;

    if (pakaiUnggahan) {
      var form = new FormData();
      form.append("payload", JSON.stringify(paket));
      form.append("citra1_file", unggahan1);
      if (unggahan2) { form.append("citra2_file", unggahan2); }
      opsi = { method: "POST", body: form };
      alamat = "/api/process-upload";
    } else {
      opsi = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(paket),
      };
      alamat = "/api/process";
    }

    var nomor = ++penghitungPermintaan;
    setStatus("memuat", "memproses");
    tampilkanKerangka();

    var mulai = performance.now();

    return fetch(alamat, opsi)
      .then(function (respons) {
        return respons.json().then(function (data) {
          return { ok: respons.ok, data: data };
        });
      })
      .then(function (hasilRespons) {
        if (nomor !== penghitungPermintaan) { return null; }

        var data = hasilRespons.data;
        if (hasilRespons.ok === false || data.galat) {
          tampilkanGalat(data.galat || "Permintaan gagal.");
          el.wadah.innerHTML = "";
          el.ringkas.hidden = true;
          return null;
        }

        var detik = (performance.now() - mulai) / 1000;
        sembunyikanGalat();
        hasilTerakhir = data;
        gambarHasil(data, data.nama_citra1, data.nama_citra2, detik);
        setStatus("siap", "selesai " + detik.toFixed(2) + "s");
        return data;
      })
      .catch(function (e) {
        if (nomor !== penghitungPermintaan) { return null; }
        tampilkanGalat("Gagal menghubungi server: " + e.message);
        el.wadah.innerHTML = "";
        return null;
      });
  }

  /* ------------------------------- Unduhan ------------------------------ */

  function unduhKelompok(namaKelompok) {
    if (!hasilTerakhir) { return; }
    var kelompok = hasilTerakhir.kelompok.filter(function (b) {
      return b.kelompok === namaKelompok;
    });
    unduhZip(kelompok);
  }

  function unduhZip(kelompok) {
    if (!kelompok.length) { return; }

    setStatus("memuat", "menyiapkan unduhan");

    fetch("/api/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ kelompok: kelompok }),
    })
      .then(function (respons) {
        if (!respons.ok) {
          return respons.json().then(function (d) {
            throw new Error(d.galat || "Unduhan gagal.");
          });
        }
        return respons.blob();
      })
      .then(function (blob) {
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url;
        a.download = "hasil_pcd_" + kelompok.map(function (b) { return b.kelompok; }).join("-") + ".zip";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        setStatus("siap", "terunduh");
      })
      .catch(function (e) {
        tampilkanGalat(e.message);
      });
  }

  /* -------------------------------- Peristiwa --------------------------- */

  function pasangSlider() {
    Object.keys(PENANDA_SLIDER).forEach(function (id) {
      var simpul = document.getElementById(id);
      var label = document.getElementById(LABEL_INDEKS[id]);
      if (!simpul || !label) { return; }

      // Saat digeser: perbarui angka saja, jangan panggil server tiap piksel.
      simpul.addEventListener("input", function () {
        label.textContent = PENANDA_SLIDER[id](simpul.value);
      });

      // Saat dilepas: render ulang agar gambar benar-benar mengikuti slider.
      simpul.addEventListener("change", function () {
        label.textContent = PENANDA_SLIDER[id](simpul.value);
        tundaProses();
      });
    });
  }

  // Tunda pengiriman agar beberapa slider yang diubah beruntun hanya memicu satu permintaan.
  var jedaProses = null;

  function tundaProses(delay) {
    clearTimeout(jedaProses);
    jedaProses = setTimeout(function () {
      prosesSemua();
    }, delay || 180);
  }

  function pasangTab() {
    document.querySelectorAll(".tab__tombol").forEach(function (tombol) {
      tombol.addEventListener("click", function () {
        document.querySelectorAll(".tab__tombol").forEach(function (t) {
          t.classList.remove("tab__tombol--aktif");
          t.setAttribute("aria-selected", "false");
        });
        tombol.classList.add("tab__tombol--aktif");
        tombol.setAttribute("aria-selected", "true");

        var target = tombol.dataset.tab;
        document.querySelectorAll(".tab__isi").forEach(function (isi) {
          isi.classList.toggle("tab__isi--sembunyi", isi.dataset.isi !== target);
        });
        prosesSemua();
      });
    });
  }

  function prosesSemua() {
    return kirimPermintaan(kelompokTerpilih());
  }

  function pasangPeristiwa() {
    el.kat1.addEventListener("change", function () {
      isiPilihanBerkas(el.kat1, el.idx1, el.info1, 1);
      tundaProses(0);
    });
    el.kat2.addEventListener("change", function () {
      isiPilihanBerkas(el.kat2, el.idx2, el.info2, 1);
      tundaProses(0);
    });

    el.idx1.addEventListener("change", function () {
      perbaruiInfo(el.idx1, el.info1, el.kat1.value);
      prosesSemua();
    });
    el.idx2.addEventListener("change", function () {
      perbaruiInfo(el.idx2, el.info2, el.kat2.value);
      prosesSemua();
    });

    el.berkas1.addEventListener("change", prosesSemua);
    el.berkas2.addEventListener("change", prosesSemua);

    el.kelompokDaftar.addEventListener("change", prosesSemua);

    // Metode grayscale memengaruhi kelompok 2 dan 6 sekaligus.
    document.querySelectorAll(".metode-gray").forEach(function (c) {
      c.addEventListener("change", prosesSemua);
    });

    // Menu pilihan pada kelompok geometri dan thresholding.
    ["mode_flip", "mode_threshold", "metode_adaptif", "jaga_ukuran"].forEach(function (id) {
      var simpul = document.getElementById(id);
      if (simpul) { simpul.addEventListener("change", prosesSemua); }
    });

    el.tombolProses.addEventListener("click", prosesSemua);

    el.tombolReset.addEventListener("click", function () {
      var bawaan = {
        beta: 50, alpha: 1, gamma: 1.5, weight1: 0.5, weight2: 0.5,
        tx: 50, ty: 30, sudut: 45, skala: 1, faktor_zoom: 1.5,
        threshold: 127, block_size: 15, c: 3, max_val: 255,
      };
      Object.keys(bawaan).forEach(function (id) {
        var simpul = document.getElementById(id);
        if (simpul) {
          simpul.value = bawaan[id];
          var label = document.getElementById(LABEL_INDEKS[id]);
          if (label) { label.textContent = PENANDA_SLIDER[id](simpul.value); }
        }
      });
      document.getElementById("mode_flip").value = "horizontal";
      document.getElementById("mode_threshold").value = "binary";
      document.getElementById("metode_adaptif").value = "mean";
      document.getElementById("jaga_ukuran").checked = true;
      document.querySelectorAll(".metode-gray").forEach(function (c) { c.checked = true; });
      document.querySelectorAll(".kelompok-centang").forEach(function (c) { c.checked = true; });
      prosesSemua();
    });

    el.catatanLipat.addEventListener("click", function () {
      var tersembunyi = el.catatanDaftar.hasAttribute("hidden");
      if (tersembunyi) {
        el.catatanDaftar.removeAttribute("hidden");
        el.catatanLipat.textContent = "sembunyikan";
      } else {
        el.catatanDaftar.setAttribute("hidden", "");
        el.catatanLipat.textContent = "tampilkan";
      }
    });

    el.tombolLipat.addEventListener("click", function () {
      var tertutup = el.kontrolIsi.hasAttribute("hidden");
      if (tertutup) {
        el.kontrolIsi.removeAttribute("hidden");
        el.tombolLipat.textContent = "lipat";
        el.tombolLipat.setAttribute("aria-expanded", "true");
      } else {
        el.kontrolIsi.setAttribute("hidden", "");
        el.tombolLipat.textContent = "buka";
        el.tombolLipat.setAttribute("aria-expanded", "false");
      }
    });

    // Unduh per kelompok (delegasi agar berlaku pada panel yang dibuat dinamis).
    el.wadah.addEventListener("click", function (ev) {
      var tombol = ev.target.closest(".kelompok__unduh");
      if (!tombol) { return; }
      unduhKelompok(tombol.dataset.kelompok);
    });

    // Gambar ulang histogram saat ukuran berubah.
    var jeda;
    window.addEventListener("resize", function () {
      clearTimeout(jeda);
      jeda = setTimeout(function () {
        if (!hasilTerakhir) { return; }
        document.querySelectorAll(".histogram canvas").forEach(function (kanvas) {
          var muatan = kanvas._muatan;
          if (muatan) { gambarHistogram(kanvas, muatan); }
        });
      }, 200);
    });
  }

  /* --------------------------------- Mulai ------------------------------ */

  function mulai() {
    isiPilihanBerkas(el.kat1, el.idx1, el.info1, 1);
    isiPilihanBerkas(el.kat2, el.idx2, el.info2, 1);

    pasangSlider();
    pasangTab();
    pasangPeristiwa();

    prosesSemua();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mulai);
  } else {
    mulai();
  }
})();
