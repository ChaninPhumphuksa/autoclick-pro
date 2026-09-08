@echo off
REM ============================================================
REM  build.bat - แปลง AutoClicker Pro ให้เป็นไฟล์ .exe (รันบน Windows เท่านั้น)
REM ============================================================

echo [1/3] กำลังติดตั้งไลบรารีที่จำเป็น...
pip install -r requirements.txt

echo [2/3] กำลังสร้างไฟล์ .exe ด้วย PyInstaller...
pyinstaller --noconfirm --onefile --windowed ^
  --name "AutoClickerPro" ^
  --add-data "profiles;profiles" ^
  --add-data "macros;macros" ^
  main.py

echo [3/3] เสร็จสิ้น! ไฟล์ .exe อยู่ที่ dist\AutoClickerPro.exe
pause
