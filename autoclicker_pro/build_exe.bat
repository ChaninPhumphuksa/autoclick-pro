@echo off
REM =========================================================
REM  Build script: แปลง Auto Clicker Pro เป็นไฟล์ .exe ตัวเดียว
REM  รันไฟล์นี้บนเครื่อง Windows เท่านั้น (PyInstaller ไม่รองรับ
REM  การ cross-compile ข้ามระบบปฏิบัติการ)
REM =========================================================

echo กำลังติดตั้งไลบรารีที่จำเป็น...
pip install -r requirements.txt

echo กำลังสร้างไฟล์ .exe ด้วย PyInstaller...
pyinstaller --noconfirm --onefile --windowed ^
    --name "AutoClickerPro" ^
    --icon "assets\icon.ico" ^
    --add-data "assets;assets" ^
    main.py

echo.
echo เสร็จสิ้น! ไฟล์ .exe อยู่ที่ dist\AutoClickerPro.exe
pause
