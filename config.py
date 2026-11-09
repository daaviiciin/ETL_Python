from pathlib import Path

# Carpeta principal (ruta donde almacena)
BASE_DIR = Path(__file__).resolve().parent

# carpeta del proyecto (para que pueda leerlo sin necesidad de una dirección concreta)
DATA_DIR = BASE_DIR / "datos"
OUTPUT_DIR = BASE_DIR / "salida"

INVENTORY_FILE = DATA_DIR / "inventario.csv"
TEST_FILE = DATA_DIR / "inventario_prueba.csv"
UPDATED_FILE = DATA_DIR / "inventario_actualizado.csv"

#comprbación para ver si reconoce los CSV (no hace nada en el proyecto, se puede eliminar)
print("Carpeta principal:", BASE_DIR)
print("Archivo de inventario:", INVENTORY_FILE)
print("¿Existe el inventario?", INVENTORY_FILE.exists())
print("¿Existe el archivo de pruebas?", TEST_FILE.exists())