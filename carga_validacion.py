"""
Carga y validación del inventario.

Responsabilidad: leer el CSV, comprobar que es utilizable, aplicar las reglas
del contrato de datos a cada fila y separar registros válidos y rechazados.
También contiene la escritura genérica de CSV que reutilizan otros módulos.
"""

import csv
import math
import re
from datetime import datetime
from pathlib import Path

import config

# Clave interna que se añade a cada fila leída para recordar su número de
# línea en el CSV. No forma parte del contrato, así que no se escribe en
# inventario_actualizado.csv.
CLAVE_LINEA = "linea_csv"


# ---------------------------------------------------------------------------
# Lectura del fichero
# ---------------------------------------------------------------------------
def leer_inventario(ruta):
    """
    Lee el CSV del inventario con el módulo csv.

    Comprueba que el fichero existe, que no está vacío y que contiene todas
    las columnas del contrato. Nunca lanza un error sin controlar.

    Devuelve una tupla (filas, mensaje_error):
      - si todo va bien: (lista de diccionarios, None)
      - si hay un problema: ([], "mensaje claro para el usuario")
    """
    ruta = Path(ruta)

    # 1) ¿Existe? is_file() también descarta que la ruta sea una carpeta.
    if not ruta.is_file():
        return [], f"No se encuentra el fichero: {ruta}"

    try:
        # newline="" es lo que recomienda el módulo csv: así él mismo
        # interpreta los saltos de línea (incluidos los de dentro de comillas).
        with open(ruta, encoding=config.ENCODING_LECTURA, newline="") as fichero:
            # DictReader usa la primera línea como cabecera y devuelve cada
            # fila como diccionario {columna: valor}.
            lector = csv.DictReader(fichero, delimiter=config.SEPARADOR)

            # 2) ¿Vacío? En un fichero de 0 bytes no hay cabecera (None).
            if not lector.fieldnames:
                return [], "El fichero está vacío."

            # Quitamos espacios alrededor de los nombres de columna para que
            # " id_equipo" se reconozca igual que "id_equipo".
            lector.fieldnames = [columna.strip() for columna in lector.fieldnames]

            # 3) ¿Están todas las columnas del contrato?
            faltantes = obtener_columnas_faltantes(lector.fieldnames)
            if faltantes:
                return [], "Faltan columnas obligatorias: " + ", ".join(faltantes)

            filas = []
            for fila in lector:
                # line_num es la línea del fichero donde termina esta fila
                # (la cabecera es la línea 1). La guardamos para errores.csv.
                fila[CLAVE_LINEA] = lector.line_num
                filas.append(fila)

    except UnicodeDecodeError:
        return [], "El fichero no está codificado en UTF-8."
    except csv.Error as error:
        return [], f"El fichero no tiene un formato CSV válido: {error}"
    except OSError as error:
        # Permisos, fichero bloqueado por otro programa, etc.
        return [], f"No se pudo leer el fichero: {error}"

    # 2 bis) Solo cabecera y ninguna fila de datos: también cuenta como vacío.
    if not filas:
        return [], "El fichero no contiene equipos (solo tiene la cabecera)."

    # Columnas que sobran: no impiden trabajar, solo avisamos y se ignoran.
    sobrantes = [c for c in lector.fieldnames if c not in config.COLUMNAS_CONTRATO]
    if sobrantes:
        print("Aviso: se ignoran columnas que no son del contrato: " + ", ".join(sobrantes))

    return filas, None


def obtener_columnas_faltantes(cabecera):
    """
    Compara la cabecera leída con config.COLUMNAS_CONTRATO.

    Devuelve la lista de columnas del contrato que no aparecen en la cabecera
    (lista vacía si están todas).
    """
    # Recorremos el contrato (no la cabecera) para que las columnas
    # faltantes salgan en el orden oficial.
    return [columna for columna in config.COLUMNAS_CONTRATO if columna not in cabecera]


# ---------------------------------------------------------------------------
# Reglas sueltas (cada una comprueba un único valor)
# ---------------------------------------------------------------------------
def esta_vacio(valor):
    """Devuelve True si el valor es None o solo contiene espacios."""
    # None aparece cuando a una fila le faltan comas al final: DictReader
    # rellena las columnas que no llegan con None.
    if valor is None:
        return True
    # "   " cuenta como vacío. Ojo: aquí solo miramos si hay contenido;
    # el valor original NO se modifica.
    return valor.strip() == ""


def convertir_fecha(texto):
    """
    Convierte un texto AAAA-MM-DD (con ceros) en un objeto date.

    Devuelve el date si el formato es exacto y la fecha existe en el
    calendario; None en caso contrario (por ejemplo "2022-3-5" o "2023-02-30").
    """
    if texto is None:
        return None
    # Paso 1: la FORMA. strptime aceptaría "2022-3-5" sin ceros, por eso
    # primero exigimos con el patrón exactamente 4-2-2 cifras.
    if not re.fullmatch(config.PATRON_FECHA, texto):
        return None
    # Paso 2: que la fecha EXISTA. "2023-02-30" tiene buena forma pero no
    # existe; strptime lanza ValueError y lo convertimos en None.
    try:
        return datetime.strptime(texto, config.FORMATO_FECHA).date()
    except ValueError:
        return None


def es_ip_valida(texto):
    """
    Devuelve True si el texto son 4 números enteros entre 0 y 255
    separados por puntos (por ejemplo "10.4.102.165").
    """
    if texto is None:
        return False
    partes = texto.split(".")
    # Tienen que salir exactamente 4 trozos: "10.1.1" o "10.1.1.1.1" no valen.
    if len(partes) != config.IP_NUM_PARTES:
        return False
    for parte in partes:
        # Solo cifras (descarta "-1", "", " 5", "a"), y como mucho 3.
        if not re.fullmatch(config.PATRON_PARTE_IP, parte):
            return False
        # Ya sabemos que son cifras, así que int() no puede fallar.
        if int(parte) > config.IP_VALOR_MAXIMO:
            return False
    return True


def es_precio_valido(texto):
    """
    Devuelve True si el texto es un número con punto decimal mayor que 0.

    Rechaza texto, coma decimal, 0, negativos, "nan" e "inf".
    """
    if texto is None:
        return False
    # El patrón ya descarta "abc", "1500,50", "-3", "nan", "inf" y "1e5":
    # float() aceptaría varios de ellos, por eso no basta con probar float().
    if not re.fullmatch(config.PATRON_PRECIO, texto):
        return False
    precio = float(texto)
    # math.isfinite es una segunda red de seguridad: un número con cientos
    # de cifras se convierte en "inf" al pasarlo a float.
    return math.isfinite(precio) and precio > 0


# ---------------------------------------------------------------------------
# Validación de filas e inventario completo
# ---------------------------------------------------------------------------
def validar_fila(fila, ids_validos, ips_validas):
    """
    Aplica las reglas del contrato a una fila, en el orden de las columnas.

    ids_validos e ips_validas son conjuntos (set) con los identificadores e
    IP de los equipos ya aceptados, para detectar duplicados.

    Devuelve None si la fila es válida, o el código de la PRIMERA regla que
    falla (una clave de config.MOTIVOS_ERROR).
    """
    # Las comprobaciones van en el mismo orden que las columnas del
    # contrato. En cuanto una falla hacemos return: así solo se informa de
    # la primera regla incumplida, aunque la fila tenga más errores.

    # id_equipo: obligatorio y sin repetir entre los equipos ya aceptados.
    if esta_vacio(fila["id_equipo"]):
        return "ID_VACIO"
    if fila["id_equipo"] in ids_validos:
        return "ID_DUPLICADO"

    # hostname: obligatorio.
    if esta_vacio(fila["hostname"]):
        return "HOSTNAME_VACIO"

    # tipo: tiene que ser EXACTAMENTE uno de la lista (" portatil" no vale).
    if fila["tipo"] not in config.TIPOS_VALIDOS:
        return "TIPO_INVALIDO"

    # sistema_operativo: obligatorio.
    if esta_vacio(fila["sistema_operativo"]):
        return "SO_VACIO"

    # direccion_ip: es OPCIONAL. Solo se comprueba si viene rellena.
    if not esta_vacio(fila["direccion_ip"]):
        if not es_ip_valida(fila["direccion_ip"]):
            return "IP_INVALIDA"
        if fila["direccion_ip"] in ips_validas:
            return "IP_DUPLICADA"

    # departamento: obligatorio.
    if esta_vacio(fila["departamento"]):
        return "DEPARTAMENTO_VACIO"

    # fechas: convertir_fecha devuelve un date o None.
    fecha_compra = convertir_fecha(fila["fecha_compra"])
    if fecha_compra is None:
        return "FECHA_COMPRA_INVALIDA"
    fin_garantia = convertir_fecha(fila["fin_garantia"])
    if fin_garantia is None:
        return "FIN_GARANTIA_INVALIDA"
    # Aquí es donde necesitamos los date: para poder compararlos.
    # "Posterior" significa estrictamente mayor: el mismo día no vale.
    if fin_garantia <= fecha_compra:
        return "GARANTIA_ANTERIOR_COMPRA"

    # estado: tiene que ser EXACTAMENTE uno de la lista.
    if fila["estado"] not in config.ESTADOS_VALIDOS:
        return "ESTADO_INVALIDO"

    # precio_eur: número con punto decimal mayor que 0.
    if not es_precio_valido(fila["precio_eur"]):
        return "PRECIO_INVALIDO"

    # Ha pasado todas las reglas.
    return None


def validar_inventario(filas):
    """
    Valida todas las filas leídas y las separa.

    Conserva la primera aparición de un id o IP repetidos y rechaza las
    siguientes. Devuelve una tupla (validos, rechazados):
      - validos: lista de diccionarios que cumplen el contrato
      - rechazados: lista de diccionarios con las columnas originales más
        linea_csv, codigo_error y motivo
    """
    validos = []
    rechazados = []
    # Conjuntos con los id e IP de los equipos YA ACEPTADOS. Un set permite
    # preguntar "¿está ya?" al instante, aunque haya miles de equipos.
    ids_validos = set()
    ips_validas = set()

    for fila in filas:
        codigo = validar_fila(fila, ids_validos, ips_validas)
        if codigo is None:
            validos.append(fila)
            # Solo registramos id e IP de las filas válidas: así una fila
            # rechazada nunca bloquea a otra posterior con el mismo valor.
            ids_validos.add(fila["id_equipo"])
            if not esta_vacio(fila["direccion_ip"]):
                ips_validas.add(fila["direccion_ip"])
        else:
            # Copiamos la fila original (con su linea_csv) y le añadimos el
            # código y el motivo. Con dict(fila) no modificamos la original.
            rechazada = dict(fila)
            rechazada["codigo_error"] = codigo
            rechazada["motivo"] = config.MOTIVOS_ERROR[codigo]
            rechazados.append(rechazada)

    return validos, rechazados


def contar_errores_por_regla(rechazados):
    """Devuelve un diccionario {codigo_error: número de filas rechazadas}."""
    # Empezamos con TODAS las reglas a 0, en el orden del contrato, para
    # que el resumen muestre también las que no han fallado ninguna vez.
    conteo = {codigo: 0 for codigo in config.MOTIVOS_ERROR}
    for fila in rechazados:
        conteo[fila["codigo_error"]] += 1
    return conteo


# ---------------------------------------------------------------------------
# Salidas de la carga
# ---------------------------------------------------------------------------
def escribir_csv(ruta, filas, columnas):
    """
    Escribe una lista de diccionarios en un CSV con las columnas indicadas.

    Crea la carpeta de destino si no existe. Se reutiliza para errores.csv,
    inventario_actualizado.csv y los listados de informes.

    Devuelve None si se ha escrito bien, o un mensaje de error si no.
    """
    ruta = Path(ruta)
    try:
        # Crea salida/ si no existe. exist_ok=True: si ya existe, no pasa nada.
        ruta.parent.mkdir(parents=True, exist_ok=True)
        # "w" sobrescribe el fichero: las salidas se regeneran en cada ejecución.
        with open(ruta, "w", encoding=config.ENCODING_ESCRITURA, newline="") as fichero:
            # extrasaction="ignore": si una fila tiene claves que no están en
            # columnas (por ejemplo una columna extra del CSV), se ignoran.
            escritor = csv.DictWriter(
                fichero,
                fieldnames=columnas,
                delimiter=config.SEPARADOR,
                extrasaction="ignore",
            )
            escritor.writeheader()
            escritor.writerows(filas)
    except OSError as error:
        # Lo más habitual: el fichero está abierto en Excel y no se puede escribir.
        return f"No se pudo escribir {ruta.name}: {error}"
    return None


def guardar_errores(rechazados):
    """
    Guarda los registros rechazados en config.ERRORS_FILE.

    Devuelve None si se ha guardado bien, o un mensaje de error si no.
    """
    # Columnas originales del contrato + linea_csv, codigo_error y motivo.
    columnas = config.COLUMNAS_CONTRATO + config.COLUMNAS_EXTRA_ERRORES
    return escribir_csv(config.ERRORS_FILE, rechazados, columnas)


def ruta_para_mostrar(ruta):
    """
    Devuelve la ruta relativa a la carpeta del proyecto si está dentro de
    ella (más corta de leer), o la ruta completa si está fuera.
    """
    try:
        return Path(ruta).relative_to(config.BASE_DIR)
    except ValueError:
        return ruta


def mostrar_resumen_carga(ruta, total_leidas, validos, rechazados):
    """
    Muestra por consola el resumen de la carga: filas leídas, válidas,
    rechazadas y número de errores por tipo de regla.
    """
    conteo = contar_errores_por_regla(rechazados)
    # Ancho del código más largo, para alinear los números en columna.
    ancho = max(len(codigo) for codigo in conteo)

    print()
    print("=== RESUMEN DE LA CARGA ===")
    print(f"Fichero: {ruta_para_mostrar(ruta)}")
    # :>4 alinea el número a la derecha en 4 posiciones.
    print(f"Filas leídas:     {total_leidas:>4}")
    print(f"Filas válidas:    {len(validos):>4}")
    print(f"Filas rechazadas: {len(rechazados):>4}")
    print()
    print("Errores por tipo de regla:")
    for codigo, cantidad in conteo.items():
        # :<{ancho} rellena el código con espacios hasta el ancho máximo.
        print(f"  {codigo:<{ancho}}  {cantidad:>4}")


def cargar_y_validar(ruta):
    """
    Ejecuta la carga completa: leer, validar, guardar errores.csv y
    mostrar el resumen.

    Devuelve la lista de equipos válidos, o None si el fichero no se pudo
    cargar (en ese caso ya se ha mostrado el mensaje al usuario).
    """
    # 1) Leer. Si el fichero no sirve, avisamos y devolvemos None.
    filas, error = leer_inventario(ruta)
    if error is not None:
        print(f"Error al cargar: {error}")
        return None

    # 2) Validar y separar.
    validos, rechazados = validar_inventario(filas)

    # 3) Guardar errores.csv (aunque no haya rechazados: así el fichero de
    #    una carga anterior nunca se queda con datos viejos).
    error_guardado = guardar_errores(rechazados)

    # 4) Resumen por consola.
    mostrar_resumen_carga(ruta, len(filas), validos, rechazados)
    print()
    if error_guardado is None:
        print(f"Rechazados guardados en {ruta_para_mostrar(config.ERRORS_FILE)}")
    else:
        # El inventario se ha cargado igualmente; solo falló el fichero.
        print(f"Aviso: {error_guardado}")

    return validos
