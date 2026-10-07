@echo off
REM ===========================================================================
REM  Peluncur aplikasi web Pengolahan Citra Digital (PCD)
REM  Membuat virtualenv bila belum ada, memasang dependensi, lalu menjalankan.
REM ===========================================================================

setlocal
cd /d "%~dp0"

set VENV=.venv
set PY=%VENV%\Scripts\python.exe

echo =================================================================
echo    APLIKASI WEB PENGOLAHAN CITRA DIGITAL (PCD)
echo =================================================================

REM --- 1. Siapkan virtualenv -------------------------------------------------
if not exist "%PY%" (
    echo [1/3] Membuat virtualenv di %VENV% ...
    python -m venv "%VENV%"
    if errorlevel 1 (
        echo.
        echo [GAGAL] Tidak dapat membuat virtualenv.
        echo         Pastikan Python 3.10 atau lebih baru terpasang dan ada di PATH.
        pause
        exit /b 1
    )
) else (
    echo [1/3] Virtualenv sudah ada.
)

REM --- 2. Pasang dependensi --------------------------------------------------
echo [2/3] Memeriksa dependensi ...
"%PY%" -c "import flask, cv2, numpy" >nul 2>&1
if errorlevel 1 (
    echo       Memasang paket yang dibutuhkan ^(perlu koneksi internet^) ...
    "%PY%" -m pip install --quiet --upgrade pip
    "%PY%" -m pip install --quiet flask opencv-python numpy matplotlib
    if errorlevel 1 (
        echo.
        echo [GAGAL] Pemasangan dependensi tidak berhasil.
        echo         Periksa koneksi internet lalu jalankan ulang berkas ini.
        pause
        exit /b 1
    )
) else (
    echo       Semua dependensi sudah tersedia.
)

REM --- 3. Jalankan server ----------------------------------------------------
echo [3/3] Menjalankan server ...
echo.
echo   Buka di peramban:  http://127.0.0.1:5000
echo   Hentikan server  :  tekan Ctrl+C
echo.

start "" http://127.0.0.1:5000
"%PY%" web\app.py

echo.
echo Server telah berhenti.
pause
