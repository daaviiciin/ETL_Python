"""
Auditoría, informes y gráficos del inventario.

Responsabilidad: calcular los indicadores a partir del inventario válido,
escribir los ficheros de informe y generar los gráficos PNG. Todos los
cálculos reciben la fecha de referencia como parámetro.

Los repartos, medias y sumas por grupo se calculan con pandas a partir de la
lista de diccionarios; la carga y la gestión no dependen de pandas.
"""

import operator
from datetime import timedelta

# "Agg" dibuja directamente en ficheros, sin abrir ventanas. Debe fijarse
# ANTES de importar pyplot; así funciona igual en cualquier ordenador.
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (tiene que ir después de use)
import pandas as pd  # noqa: E402

import carga_validacion  # noqa: E402
import config  # noqa: E402

# Traduce el texto de comparación de config.SO_OBSOLETOS a la operación real.
# operator.lt(a, b) equivale a "a < b", operator.le a "a <= b", etc.
COMPARACIONES = {
    "==": operator.eq,
    "<": operator.lt,
    "<=": operator.le,
}


# ---------------------------------------------------------------------------
# Auditoría
# ---------------------------------------------------------------------------
def crear_dataframe(equipos):
    """
    Convierte la lista de diccionarios en un DataFrame de pandas con las
    columnas del contrato y el precio ya convertido a número.
    """
    # columns= fija el orden y deja fuera claves internas como linea_csv.
    tabla = pd.DataFrame(equipos, columns=list(config.COLUMNAS_CONTRATO))
    # Los equipos ya están validados, así que el precio siempre es numérico.
    tabla["precio_eur"] = pd.to_numeric(tabla["precio_eur"])
    return tabla


def contar_por_campo(tabla, campo):
    """
    Devuelve un diccionario {valor: número de equipos} para un campo,
    ordenado alfabéticamente por el valor.
    """
    # value_counts cuenta cuántas veces aparece cada valor; sort_index
    # ordena por el valor (no por la cantidad). int() pasa el número de
    # numpy a entero normal de Python.
    conteo = tabla[campo].value_counts().sort_index()
    return {valor: int(cantidad) for valor, cantidad in conteo.items()}


def version_a_tupla(texto):
    """
    Convierte una versión en tupla de enteros para compararla:
    "10.15" -> (10, 15), "7" -> (7,). Devuelve None si no es numérica.
    """
    if carga_validacion.esta_vacio(texto):
        return None
    partes = texto.strip().split(".")
    if not all(parte.isdecimal() for parte in partes):
        return None
    return tuple(int(parte) for parte in partes)


def igualar_longitud(a, b):
    """
    Rellena con ceros la tupla más corta para poder comparar versiones de
    distinta longitud: (7,) y (7, 0) pasan a ser iguales.
    """
    largo = max(len(a), len(b))
    return a + (0,) * (largo - len(a)), b + (0,) * (largo - len(b))


def es_so_obsoleto(equipo):
    """
    Devuelve True si el sistema operativo y la versión del equipo cumplen
    alguna regla de config.SO_OBSOLETOS.
    """
    sistema = (equipo.get("sistema_operativo") or "").strip().casefold()
    version = version_a_tupla(equipo.get("version_so"))
    # Sin versión numérica no podemos comparar: no se marca como obsoleto.
    if version is None:
        return False

    for sistema_regla, comparacion, version_regla in config.SO_OBSOLETOS:
        if sistema != sistema_regla.casefold():
            continue
        a, b = igualar_longitud(version, version_a_tupla(version_regla))
        if COMPARACIONES[comparacion](a, b):
            return True
    return False


def obtener_equipos_so_obsoleto(equipos):
    """Devuelve la lista de equipos con sistema operativo obsoleto."""
    return [equipo for equipo in equipos if es_so_obsoleto(equipo)]


def obtener_garantias_proximas(equipos, fecha_referencia):
    """
    Devuelve los equipos cuya fin_garantia está entre fecha_referencia y
    fecha_referencia + config.DIAS_AVISO_GARANTIA, ambas incluidas.
    """
    limite = fecha_referencia + timedelta(days=config.DIAS_AVISO_GARANTIA)
    proximas = []
    for equipo in equipos:
        fin = carga_validacion.convertir_fecha(equipo["fin_garantia"])
        # <= en los dos lados: las dos fechas del intervalo cuentan.
        if fin is not None and fecha_referencia <= fin <= limite:
            proximas.append(equipo)
    return proximas


def calcular_antiguedad(fecha_compra, fecha_referencia):
    """Devuelve la antigüedad en años: días transcurridos / DIAS_POR_ANIO."""
    # Restar dos date da un timedelta; .days son los días enteros.
    return (fecha_referencia - fecha_compra).days / config.DIAS_POR_ANIO


def antiguedad_media_por_departamento(tabla, fecha_referencia):
    """
    Devuelve {departamento: antigüedad media en años}, redondeada a
    config.DECIMALES.
    """
    # Calculamos la antigüedad de cada equipo con la misma función de
    # siempre, y pandas agrupa por departamento y hace la media.
    antiguedades = tabla["fecha_compra"].apply(
        lambda texto: calcular_antiguedad(carga_validacion.convertir_fecha(texto), fecha_referencia)
    )
    medias = antiguedades.groupby(tabla["departamento"]).mean().sort_index()
    return {dep: round(float(media), config.DECIMALES) for dep, media in medias.items()}


def coste_por_departamento(tabla):
    """Devuelve {departamento: suma de precio_eur}, redondeada a 2 decimales."""
    sumas = tabla.groupby("departamento")["precio_eur"].sum().sort_index()
    return {dep: round(float(suma), config.DECIMALES) for dep, suma in sumas.items()}


def calcular_auditoria(equipos, fecha_referencia):
    """
    Calcula los cinco indicadores de la auditoría y los devuelve juntos en un
    diccionario, para mostrarlos, escribirlos y dibujarlos.
    """
    tabla = crear_dataframe(equipos)
    return {
        "fecha_referencia": fecha_referencia,
        "total": len(equipos),
        "por_tipo": contar_por_campo(tabla, "tipo"),
        "por_departamento": contar_por_campo(tabla, "departamento"),
        "por_estado": contar_por_campo(tabla, "estado"),
        "so_obsoleto": obtener_equipos_so_obsoleto(equipos),
        "garantias_proximas": obtener_garantias_proximas(equipos, fecha_referencia),
        "antiguedad_media": antiguedad_media_por_departamento(tabla, fecha_referencia),
        "coste": coste_por_departamento(tabla),
    }


def formatear_auditoria(auditoria):
    """
    Construye el texto completo de la auditoría, organizado por secciones.
    Se usa tanto para la consola como para informe_auditoria.txt, así los
    dos muestran siempre exactamente lo mismo.
    """
    lineas = []
    titulo = "INFORME DE AUDITORÍA DEL INVENTARIO"
    lineas += [titulo, "=" * len(titulo)]
    lineas.append(f"Fecha de referencia: {auditoria['fecha_referencia']}")
    lineas.append(f"Equipos válidos analizados: {auditoria['total']}")

    def seccion(nombre):
        """Añade una línea en blanco, el título de la sección y su subrayado."""
        lineas.extend(["", nombre, "-" * len(nombre)])

    for nombre, clave in (
        ("1. Equipos por tipo", "por_tipo"),
        ("2. Equipos por departamento", "por_departamento"),
        ("3. Equipos por estado", "por_estado"),
    ):
        seccion(nombre)
        datos = auditoria[clave]
        ancho = max((len(k) for k in datos), default=0)
        for valor, cantidad in datos.items():
            lineas.append(f"  {valor:<{ancho}}  {cantidad:>4}")

    seccion(f"4. Equipos con sistema operativo obsoleto ({len(auditoria['so_obsoleto'])})")
    for e in auditoria["so_obsoleto"]:
        lineas.append(
            f"  {e['id_equipo']}  {e['hostname']}  {e['sistema_operativo']} {e['version_so']}  ({e['estado']})"
        )

    seccion(
        f"5. Garantías que caducan en los próximos {config.DIAS_AVISO_GARANTIA} días "
        f"({len(auditoria['garantias_proximas'])})"
    )
    for e in auditoria["garantias_proximas"]:
        lineas.append(f"  {e['id_equipo']}  {e['hostname']}  {e['departamento']}  {e['fin_garantia']}  ({e['estado']})")

    seccion("6. Antigüedad media y coste total por departamento")
    departamentos = auditoria["antiguedad_media"]
    ancho = max((len(d) for d in departamentos), default=0)
    lineas.append(f"  {'Departamento':<{ancho}}  {'Años':>6}  {'Coste (€)':>12}")
    for dep, media in departamentos.items():
        lineas.append(f"  {dep:<{ancho}}  {media:>6.2f}  {auditoria['coste'][dep]:>12.2f}")

    return "\n".join(lineas)


def mostrar_auditoria(auditoria):
    """Muestra por consola los resultados de la auditoría."""
    print()
    print(formatear_auditoria(auditoria))


# ---------------------------------------------------------------------------
# Informes
# ---------------------------------------------------------------------------
def escribir_informe_auditoria(auditoria):
    """
    Escribe config.AUDIT_REPORT_FILE, organizado por secciones.
    Devuelve None si se ha escrito bien, o un mensaje de error si no.
    """
    ruta = config.AUDIT_REPORT_FILE
    try:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta, "w", encoding=config.ENCODING_ESCRITURA) as fichero:
            fichero.write(formatear_auditoria(auditoria) + "\n")
    except OSError as error:
        return f"No se pudo escribir {ruta.name}: {error}"
    return None


def generar_informes(auditoria):
    """
    Genera informe_auditoria.txt, equipos_so_obsoleto.csv y
    garantias_proximas.csv.

    Devuelve una lista de tuplas (ruta, error); error es None si ese
    fichero se generó bien.
    """
    resultados = [(config.AUDIT_REPORT_FILE, escribir_informe_auditoria(auditoria))]
    for ruta, clave in (
        (config.OBSOLETE_OS_FILE, "so_obsoleto"),
        (config.WARRANTY_FILE, "garantias_proximas"),
    ):
        error = carga_validacion.escribir_csv(ruta, auditoria[clave], config.COLUMNAS_CONTRATO)
        resultados.append((ruta, error))
    return resultados


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------
def generar_grafico_barras(datos, titulo, etiqueta_x, etiqueta_y, ruta, decimales=0):
    """
    Dibuja un gráfico de barras con matplotlib a partir de {etiqueta: valor},
    con título, ejes y el valor encima de cada barra, y lo guarda como PNG.

    Devuelve None si se ha guardado bien, o un mensaje de error si no.
    """
    figura, ejes = plt.subplots(figsize=(10, 6))
    try:
        etiquetas = list(datos.keys())
        valores = list(datos.values())
        barras = ejes.bar(etiquetas, valores, color="#2456a6")
        # Escribe el valor encima de cada barra (lectura clara del dato).
        ejes.bar_label(barras, fmt=f"%.{decimales}f", padding=3)
        ejes.set_title(titulo)
        ejes.set_xlabel(etiqueta_x)
        ejes.set_ylabel(etiqueta_y)
        # Margen arriba para que la etiqueta de la barra más alta no se corte.
        if valores:
            ejes.set_ylim(0, max(valores) * 1.15)
        else:
            ejes.text(0.5, 0.5, "Sin datos", ha="center", va="center", transform=ejes.transAxes)
        # Inclina los nombres largos (departamentos) para que no se pisen.
        plt.setp(ejes.get_xticklabels(), rotation=30, ha="right")
        figura.tight_layout()
        ruta.parent.mkdir(parents=True, exist_ok=True)
        figura.savefig(ruta, dpi=120)
    except OSError as error:
        return f"No se pudo guardar {ruta.name}: {error}"
    finally:
        # Cerrar siempre la figura para no acumular memoria entre ejecuciones.
        plt.close(figura)
    return None


def generar_graficos(auditoria):
    """
    Genera los tres gráficos obligatorios: equipos por departamento,
    equipos por estado y antigüedad media por departamento.

    Devuelve una lista de tuplas (ruta, error), como generar_informes.
    """
    graficos = (
        (auditoria["por_departamento"], "Equipos por departamento", "Departamento",
         "Número de equipos", config.CHART_DEPARTMENTS_FILE, 0),
        (auditoria["por_estado"], "Equipos por estado", "Estado",
         "Número de equipos", config.CHART_STATES_FILE, 0),
        (auditoria["antiguedad_media"], "Antigüedad media por departamento", "Departamento",
         "Antigüedad media (años)", config.CHART_AGE_FILE, config.DECIMALES),
    )
    resultados = []
    for datos, titulo, eje_x, eje_y, ruta, decimales in graficos:
        error = generar_grafico_barras(datos, titulo, eje_x, eje_y, ruta, decimales)
        resultados.append((ruta, error))
    return resultados
