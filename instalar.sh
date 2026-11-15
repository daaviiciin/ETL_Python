#!/usr/bin/env bash
# ===========================================================================
#  IT Asset Manager - instalación y arranque en Linux / macOS
#  Crea el entorno virtual .venv, instala requirements.txt y lanza main.py.
#  Uso:  bash instalar.sh
# ===========================================================================
set -e

# Trabajar siempre desde la carpeta del proyecto (donde está este script).
cd "$(dirname "$0")"

# --- 1 y 2. Buscar un Python 3.11 o superior que funcione de verdad ----------
# No basta con que el comando exista: en Windows "python3" puede ser un
# atajo de la Microsoft Store que no ejecuta nada. Por eso probamos cada
# candidato y nos quedamos con el primero que arranca y cumple la versión
# mínima (pandas 3 necesita Python 3.11).
PYTHON=""
for candidato in python3 python; do
    if "$candidato" -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >/dev/null 2>&1; then
        PYTHON="$candidato"
        break
    fi
done
if [ -z "$PYTHON" ]; then
    echo "[ERROR] Se necesita Python 3.11 o superior y no se ha encontrado."
    echo "Instálalo (por ejemplo: sudo apt install python3 python3-venv, o desde python.org)."
    exit 1
fi

# --- 3. Crear el entorno virtual si no existe --------------------------------
# En Linux/macOS el intérprete queda en .venv/bin; en Git Bash de Windows,
# en .venv/Scripts. Usamos el que exista.
venv_python() {
    if [ -x ".venv/bin/python" ]; then
        echo ".venv/bin/python"
    elif [ -x ".venv/Scripts/python.exe" ]; then
        echo ".venv/Scripts/python.exe"
    fi
}

if [ -z "$(venv_python)" ]; then
    echo "Creando el entorno virtual .venv ..."
    "$PYTHON" -m venv .venv
fi
VENV_PY="$(venv_python)"

# --- 4. Instalar las dependencias --------------------------------------------
echo "Instalando dependencias de requirements.txt ..."
"$VENV_PY" -m pip install --upgrade pip --quiet
"$VENV_PY" -m pip install -r requirements.txt --quiet
echo "Dependencias instaladas."
echo

# --- 5. Arrancar el programa -------------------------------------------------
# Se lanza desde la carpeta del proyecto y config.py calcula las
# rutas de datos/ y salida/ por su cuenta.
"$VENV_PY" main.py
