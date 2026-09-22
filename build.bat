@echo off
chcp 65001 >nul
title Dung app Tu Vi (.exe)
cd /d "%~dp0"

echo ============================================================
echo    Dong goi bo tra cuu tu vi thanh .exe chay doc lap
echo ============================================================
echo.

python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [1/3] Dang cai PyInstaller...
    python -m pip install pyinstaller
) else (
    echo [1/3] PyInstaller da co.
)

python -c "import webview" 2>nul
if errorlevel 1 (
    echo [2/3] Dang cai pywebview (cua so rieng)...
    python -m pip install pywebview
) else (
    echo [2/3] pywebview da co.
)

echo.
echo [3/3] Dang dung... mat khoang 1-2 phut, dung tat cua so.
echo.
python -m PyInstaller tuvi.spec --noconfirm
if errorlevel 1 (
    echo.
    echo [LOI] Dung that bai. Xem log ben tren.
    pause
    exit /b 1
)

echo.
echo Dang tu kiem ban vua dung...
dist\Tu-Vi\Tu-Vi.exe --kiem-tra
if errorlevel 1 (
    echo [LOI] Ban dung bi hong o phan tu kiem. Xem dist\Tu-Vi\tuvi.log
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   XONG! App nam tai:  dist\Tu-Vi\Tu-Vi.exe
echo.
echo   Chep ca thu muc dist\Tu-Vi di dau cung chay duoc,
echo   khong can cai Python.
echo   Muon dung luan giai AI: dat file .env (co GEMINI_API_KEY)
echo   canh file Tu-Vi.exe.
echo ============================================================
echo.
pause
