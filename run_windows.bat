@echo off
REM Windows baslatici, cift tiklayin / Windows launcher, double-click to run
setlocal
set "DIR=%~dp0"
set "VENV=%DIR%.venv"

REM Marker Python 3.10+ ister, py launcher varsa onu kullan / Marker needs 3.10+
where py >nul 2>nul
if %errorlevel%==0 (
    set "PY=py -3"
) else (
    set "PY=python"
)

REM Venv yoksa olustur ve bagimliliklari kur / create venv and install deps if missing
if not exist "%VENV%" (
    echo Ortam olusturuluyor...
    %PY% -m venv "%VENV%"
    "%VENV%\Scripts\python.exe" -m pip install --upgrade pip
    echo Kutuphaneler kuruluyor ^(Marker buyuk bir indirme, ilk kurulum birkac dakika surebilir^)...
    "%VENV%\Scripts\pip.exe" install -r "%DIR%requirements.txt"
)

REM Uygulamayi baslat / launch the app
"%VENV%\Scripts\python.exe" "%DIR%app.py"
endlocal
