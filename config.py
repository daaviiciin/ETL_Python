"""
Configuración general del proyecto IT Asset Manager.

Aquí se centralizan TODAS las constantes: rutas, contrato de datos, umbrales
y listas de valores. Ningún otro módulo debe escribir estos valores a mano;
siempre los importa desde aquí. Este módulo no ejecuta nada al importarse.
"""

from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Fecha de referencia
# ---------------------------------------------------------------------------
# None  -> el programa usa date.today() (funcionamiento normal).
# date(2026, 11, 2) -> fecha fija para repetir los cálculos y comprobarlos.
FECHA_REFERENCIA_FIJA = None

# ---------------------------------------------------------------------------
# Rutas (relativas a la carpeta del proyecto, funcionan en cualquier equipo)
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "datos"
OUTPUT_DIR = BASE_DIR / "salida"

# Entrada: CSV que se propone por defecto al cargar (se puede elegir otro)
INVENTORY_FILE = DATA_DIR / "inventario.csv"
TEST_FILE = DATA_DIR / "inventario_prueba.csv"

# Ficheros que genera el programa. Todos dentro de salida/
ERRORS_FILE = OUTPUT_DIR / "errores.csv"
UPDATED_FILE = OUTPUT_DIR / "inventario_actualizado.csv"
AUDIT_REPORT_FILE = OUTPUT_DIR / "informe_auditoria.txt"
OBSOLETE_OS_FILE = OUTPUT_DIR / "equipos_so_obsoleto.csv"
WARRANTY_FILE = OUTPUT_DIR / "garantias_proximas.csv"
CHART_DEPARTMENTS_FILE = OUTPUT_DIR / "grafico_departamentos.png"
CHART_STATES_FILE = OUTPUT_DIR / "grafico_estados.png"
CHART_AGE_FILE = OUTPUT_DIR / "grafico_antiguedad.png"

# ---------------------------------------------------------------------------
# Formato del CSV
# ---------------------------------------------------------------------------
# "utf-8-sig" lee igual que "utf-8" pero además elimina la marca BOM que
# añade Excel al guardar. Sin esto, la primera columna se leería como
# "﻿id_equipo" y la comprobación de columnas fallaría.
ENCODING_LECTURA = "utf-8-sig"
ENCODING_ESCRITURA = "utf-8"
SEPARADOR = ","

# ---------------------------------------------------------------------------
# Contrato de datos. El ORDEN importa: si una fila incumple
# varias reglas, se informa de la primera según este orden.
# ---------------------------------------------------------------------------
COLUMNAS_CONTRATO = (
    "id_equipo",
    "hostname",
    "tipo",
    "marca_modelo",
    "sistema_operativo",
    "version_so",
    "direccion_ip",
    "departamento",
    "usuario_asignado",
    "fecha_compra",
    "fin_garantia",
    "estado",
    "precio_eur",
)

TIPOS_VALIDOS = ("portatil", "sobremesa", "servidor", "movil")
ESTADOS_VALIDOS = ("activo", "almacen", "reparacion", "baja")
ESTADO_BAJA = "baja"

FORMATO_FECHA = "%Y-%m-%d"

# Patrones (expresiones regulares) que debe cumplir el TEXTO completo.
# Se usa [0-9] en vez de \d porque \d también acepta dígitos de otros
# alfabetos (por ejemplo "٣"), y aquí solo valen los del 0 al 9.
# Fecha: exactamente 4-2-2 cifras con guiones ("2022-3-5" no cumple).
PATRON_FECHA = r"[0-9]{4}-[0-9]{2}-[0-9]{2}"
# Precio: cifras, y opcionalmente un punto seguido de más cifras.
# Vale "1500" y "1500.50"; no vale "1500,50", "-3", "abc", "nan" ni "inf".
PATRON_PRECIO = r"[0-9]+(\.[0-9]+)?"
# Cada una de las partes de una IP: de 1 a 3 cifras.
PATRON_PARTE_IP = r"[0-9]{1,3}"
IP_NUM_PARTES = 4
IP_VALOR_MAXIMO = 255

# Columnas extra que se añaden a cada fila en errores.csv
COLUMNAS_EXTRA_ERRORES = ("linea_csv", "codigo_error", "motivo")

# Códigos de error y su motivo legible, en el MISMO orden que el contrato.
MOTIVOS_ERROR = {
    "ID_VACIO": "id_equipo vacío",
    "ID_DUPLICADO": "Identificador repetido (se conserva la primera aparición)",
    "HOSTNAME_VACIO": "hostname vacío",
    "TIPO_INVALIDO": "Tipo fuera de portatil, sobremesa, servidor, movil",
    "SO_VACIO": "sistema_operativo vacío",
    "IP_INVALIDA": "direccion_ip no tiene 4 números entre 0 y 255",
    "IP_DUPLICADA": "Dirección IP ya usada por un equipo válido anterior",
    "DEPARTAMENTO_VACIO": "departamento vacío",
    "FECHA_COMPRA_INVALIDA": "fecha_compra sin formato AAAA-MM-DD válido",
    "FIN_GARANTIA_INVALIDA": "fin_garantia sin formato AAAA-MM-DD válido",
    "GARANTIA_ANTERIOR_COMPRA": "fin_garantia no es posterior a fecha_compra",
    "ESTADO_INVALIDO": "Estado fuera de activo, almacen, reparacion, baja",
    "PRECIO_INVALIDO": "precio_eur no es un número mayor que 0",
}

# ---------------------------------------------------------------------------
# Gestión del inventario
# ---------------------------------------------------------------------------
CAMPOS_BUSQUEDA = ("id_equipo", "hostname", "departamento", "tipo")
CAMPOS_MODIFICABLES = ("estado", "departamento", "usuario_asignado")

# ---------------------------------------------------------------------------
# Umbrales de la auditoría
# ---------------------------------------------------------------------------
DIAS_AVISO_GARANTIA = 90
DIAS_POR_ANIO = 365.25
DECIMALES = 2

# ---------------------------------------------------------------------------
# Sistemas operativos obsoletos
# Cada regla: (sistema_operativo, comparación, versión límite)
# Supuesto adoptado: "Ubuntu Server" se trata igual que "Ubuntu".
# Windows 10, Windows Server, iOS y Android se consideran vigentes.
# ---------------------------------------------------------------------------
SO_OBSOLETOS = (
    ("Windows", "==", "7"),
    ("Windows", "==", "8.1"),
    ("macOS", "<", "12"),
    ("Ubuntu", "<=", "18.04"),
    ("Ubuntu Server", "<=", "18.04"),
)
