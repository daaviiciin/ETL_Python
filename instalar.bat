@echo off
REM ===========================================================================
REM  IT Asset Manager - instalación y arranque en Windows
REM  Crea el entorno virtual .venv, instala requirements.txt y lanza src\main.py.
REM  Uso: doble clic en este fichero, o "instalar.bat" desde una terminal.
REM ===========================================================================
setlocal
REM UTF-8 en la consola para que se vean bien las tildes del programa.
chcp 65001 >nul
REM Trabajar siempre desde la carpeta del proyecto (donde está este .bat).
cd /d "%~dp0"

REM --- 1. Buscar Python 3 ("python" o el lanzador "py") ----------------------
set "PYTHON="
python --version >nul 2>&1 && set "PYTHON=python"
if not defined PYTHON (
    py -3 --version >nul 2>&1 && set "PYTHON=py -3"
)
if not defined PYTHON (
    echo [ERROR] No se ha encontrado Python 3.
    echo Instalalo desde https://www.python.org/downloads/ marcando "Add python.exe to PATH".
    pause
    exit /b 1
)

REM --- 2. Comprobar la versión mínima (pandas 3 necesita Python 3.11) ---------
%PYTHON% -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
if errorlevel 1 (
    echo [ERROR] Se necesita Python 3.11 o superior. Version encontrada:
    %PYTHON% --version
    pause
    exit /b 1
)

REM --- 3. Crear el entorno virtual si no existe ------------------------------
if not exist ".venv\Scripts\python.exe" (
    echo Creando el entorno virtual .venv ...
    %PYTHON% -m venv .venv
    if errorlevel 1 goto :error
)

REM --- 4. Instalar las dependencias ------------------------------------------
echo Instalando dependencias de requirements.txt ...
".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
if errorlevel 1 goto :error
echo Dependencias instaladas.
echo.

REM --- 5. Arrancar el programa -----------------------------------------------
REM El código está en src\; se lanza desde la raíz y config.py calcula las
REM rutas de datos\ y salida\ por su cuenta.
".venv\Scripts\python.exe" src\main.py
pause
exit /b 0

:error
echo.
echo [ERROR] La instalacion no se ha completado. Revisa los mensajes de arriba.
pause
exit /b 1
