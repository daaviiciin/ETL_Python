"""
Auditoría, informes y gráficos del inventario.

Responsabilidad: calcular los indicadores a partir del inventario válido,
escribir los ficheros de informe y generar los gráficos PNG. Todos los
cálculos reciben la fecha de referencia como parámetro.
"""

import config


# ---------------------------------------------------------------------------
# Auditoría
# ---------------------------------------------------------------------------
def contar_por_campo(equipos, campo):
    """Devuelve un diccionario {valor: número de equipos} para un campo."""
    conteo = {}
    for equipo in equipos:
        valor = equipo[campo]
        conteo[valor] = conteo.get(valor, 0) + 1
    return conteo


def version_a_tupla(texto):
    """
    Convierte una versión en tupla de enteros para compararla:
    "10.15" -> (10, 15), "7" -> (7,). Devuelve None si no es numérica.
    """
    if not isinstance(texto, str):
        return None
    partes = texto.strip().split(".")
    if any(not parte or any(c not in "0123456789" for c in parte) for parte in partes):
        return None
    try:
        return tuple(int(parte) for parte in partes)
    except ValueError:
        return None


def es_so_obsoleto(equipo):
    """
    Devuelve True si el sistema operativo y la versión del equipo cumplen
    alguna regla de config.SO_OBSOLETOS.
    """
    version = version_a_tupla(equipo.get("version_so"))
    sistema = equipo.get("sistema_operativo")
    if version is None or not isinstance(sistema, str):
        return False
    for nombre, comparacion, texto_limite in config.SO_OBSOLETOS:
        if sistema.strip().casefold() != nombre.casefold():
            continue
        limite = version_a_tupla(texto_limite)
        if limite is None:
            continue
        # Los componentes finales ausentes equivalen a cero: 7 == 7.0.
        longitud = max(len(version), len(limite))
        actual = version + (0,) * (longitud - len(version))
        umbral = limite + (0,) * (longitud - len(limite))
        if (
            (comparacion == "==" and actual == umbral)
            or (comparacion == "<" and actual < umbral)
            or (comparacion == "<=" and actual <= umbral)
        ):
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
    from datetime import datetime, timedelta

    limite = fecha_referencia + timedelta(days=config.DIAS_AVISO_GARANTIA)
    return [
        equipo for equipo in equipos
        if fecha_referencia <= datetime.strptime(
            equipo["fin_garantia"], config.FORMATO_FECHA
        ).date() <= limite
    ]


def calcular_antiguedad(fecha_compra, fecha_referencia):
    """Devuelve la antigüedad en años: días transcurridos / DIAS_POR_ANIO."""
    from datetime import datetime

    compra = datetime.strptime(fecha_compra, config.FORMATO_FECHA).date()
    return (fecha_referencia - compra).days / config.DIAS_POR_ANIO


def antiguedad_media_por_departamento(equipos, fecha_referencia):
    """
    Devuelve {departamento: antigüedad media en años}, redondeada a
    config.DECIMALES.
    """
    totales = {}
    conteos = contar_por_campo(equipos, "departamento")
    for equipo in equipos:
        departamento = equipo["departamento"]
        totales[departamento] = totales.get(departamento, 0) + calcular_antiguedad(
            equipo["fecha_compra"], fecha_referencia
        )
    return {
        departamento: round(total / conteos[departamento], config.DECIMALES)
        for departamento, total in totales.items()
    }


def coste_por_departamento(equipos):
    """Devuelve {departamento: suma de precio_eur}, redondeada a 2 decimales."""
    from decimal import Decimal

    totales = {}
    for equipo in equipos:
        departamento = equipo["departamento"]
        totales[departamento] = totales.get(departamento, Decimal("0")) + Decimal(
            equipo["precio_eur"]
        )
    return {
        departamento: float(round(total, config.DECIMALES))
        for departamento, total in totales.items()
    }


def calcular_auditoria(equipos, fecha_referencia):
    """
    Calcula los cinco indicadores de la auditoría y los devuelve juntos en un
    diccionario, para mostrarlos, escribirlos y dibujarlos.
    """
    # El indicador de distribución incluye departamento y estado.
    return {
        "equipos_por_departamento": contar_por_campo(equipos, "departamento"),
        "equipos_por_estado": contar_por_campo(equipos, "estado"),
        "equipos_so_obsoleto": obtener_equipos_so_obsoleto(equipos),
        "garantias_proximas": obtener_garantias_proximas(equipos, fecha_referencia),
        "antiguedad_media_por_departamento": antiguedad_media_por_departamento(
            equipos, fecha_referencia
        ),
        "coste_por_departamento": coste_por_departamento(equipos),
    }


def mostrar_auditoria(auditoria):
    """Muestra por consola los resultados de la auditoría."""
    print("\n=== AUDITORÍA DEL INVENTARIO ===")
    for clave, titulo, unidad in (
        ("equipos_por_departamento", "Equipos por departamento", "equipos"),
        ("equipos_por_estado", "Equipos por estado", "equipos"),
        ("antiguedad_media_por_departamento", "Antigüedad media por departamento", "años"),
        ("coste_por_departamento", "Coste por departamento", "EUR"),
    ):
        print(f"\n{titulo}:")
        datos = auditoria[clave]
        if not datos:
            print("  Sin datos.")
        for etiqueta, valor in datos.items():
            texto = str(valor) if unidad == "equipos" else f"{valor:.{config.DECIMALES}f}"
            print(f"  {etiqueta}: {texto} {unidad}")

    for clave, titulo in (
        ("equipos_so_obsoleto", "Equipos con sistema operativo obsoleto"),
        ("garantias_proximas", f"Garantías próximas (hasta {config.DIAS_AVISO_GARANTIA} días, límites incluidos)"),
    ):
        equipos = auditoria[clave]
        print(f"\n{titulo}: {len(equipos)}")
        if not equipos:
            print("  Sin equipos.")
        for equipo in equipos:
            detalle = (
                f"{equipo['sistema_operativo']} {equipo['version_so']}"
                if clave == "equipos_so_obsoleto"
                else f"fin de garantía: {equipo['fin_garantia']}"
            )
            print(f"  {equipo['id_equipo']} | {equipo['hostname']} | {equipo['departamento']} | {detalle}")


# ---------------------------------------------------------------------------
# Informes
# ---------------------------------------------------------------------------
def escribir_informe_auditoria(auditoria, fecha_referencia):
    """Escribe config.AUDIT_REPORT_FILE, organizado por secciones."""
    import io
    import tempfile
    from contextlib import redirect_stdout
    from pathlib import Path

    contenido = io.StringIO()
    with redirect_stdout(contenido):
        print(f"Fecha de referencia: {fecha_referencia.strftime(config.FORMATO_FECHA)}")
        mostrar_auditoria(auditoria)
    ruta = Path(config.AUDIT_REPORT_FILE)
    temporal = None
    try:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding=config.ENCODING_ESCRITURA,
            dir=ruta.parent, delete=False,
        ) as fichero:
            temporal = Path(fichero.name)
            fichero.write(contenido.getvalue())
        temporal.replace(ruta)
    except (OSError, UnicodeError) as error:
        print(f"Error al escribir {ruta.name}: {error}")
        return False
    finally:
        if temporal is not None and temporal.exists():
            try:
                temporal.unlink()
            except OSError:
                pass
    print(f"Informe guardado en {ruta}.")
    return True


def generar_informes(auditoria, fecha_referencia):
    """
    Genera informe_auditoria.txt, equipos_so_obsoleto.csv y
    garantias_proximas.csv.
    """
    import csv
    import tempfile
    from pathlib import Path
    import carga_validacion

    # La auditoría recibida ya fue calculada por calcular_auditoria().
    # Reutilizarla evita resultados distintos entre consola y exportaciones.
    exito = escribir_informe_auditoria(auditoria, fecha_referencia)
    for destino, clave in (
        (config.OBSOLETE_OS_FILE, "equipos_so_obsoleto"),
        (config.WARRANTY_FILE, "garantias_proximas"),
    ):
        ruta = Path(destino)
        temporal = None
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=ruta.parent, delete=False) as fichero:
                temporal = Path(fichero.name)
            error = carga_validacion.escribir_csv(
                temporal, auditoria[clave], config.COLUMNAS_CONTRATO
            )
            if error is not None:
                print(f"Error al generar {ruta.name}: {error}")
                exito = False
                continue
            temporal.replace(ruta)
        except (OSError, UnicodeError, csv.Error) as error:
            print(f"Error al generar {ruta.name}: {error}")
            exito = False
            continue
        finally:
            if temporal is not None and temporal.exists():
                try:
                    temporal.unlink()
                except OSError:
                    pass
        print(f"Informe guardado en {ruta}.")
    return exito


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------
def generar_grafico_barras(datos, titulo, etiqueta_x, etiqueta_y, ruta):
    """
    Dibuja un gráfico de barras con matplotlib a partir de {etiqueta: valor},
    con título, ejes y el valor encima de cada barra, y lo guarda como PNG.
    """
    import tempfile
    import textwrap
    from pathlib import Path
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    destino = Path(ruta)
    temporal = None
    figura = Figure(figsize=(max(8, len(datos) * 1.2), 6), layout="constrained")
    FigureCanvasAgg(figura)
    try:
        eje = figura.subplots()
        eje.set_title(titulo, wrap=True)
        eje.set_xlabel(etiqueta_x)
        eje.set_ylabel(etiqueta_y)
        if datos:
            etiquetas = [textwrap.fill(str(etiqueta), width=18) for etiqueta in datos]
            valores = list(datos.values())
            barras = eje.bar(range(len(valores)), valores, color="#3576AB")
            eje.set_xticks(range(len(etiquetas)), etiquetas)
            eje.tick_params(axis="x", labelsize=9)
            textos = [
                str(valor) if isinstance(valor, int) else f"{valor:.{config.DECIMALES}f}"
                for valor in valores
            ]
            eje.bar_label(barras, labels=textos, padding=4)
            eje.margins(y=0.2)
            eje.axhline(0, color="grey", linewidth=0.6)
        else:
            eje.text(0.5, 0.5, "Sin datos para mostrar", ha="center", va="center",
                     transform=eje.transAxes)
            eje.set_xticks([])
            eje.set_yticks([])
        destino.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=destino.parent, delete=False) as fichero:
            temporal = Path(fichero.name)
        figura.savefig(temporal, format="png", dpi=150, bbox_inches="tight")
        temporal.replace(destino)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Error al generar {destino.name}: {error}")
        return False
    finally:
        figura.clear()
        if temporal is not None and temporal.exists():
            try:
                temporal.unlink()
            except OSError:
                pass
    print(f"Gráfico guardado en {destino}.")
    return True


def generar_graficos(auditoria):
    """
    Genera los tres gráficos obligatorios: equipos por departamento,
    equipos por estado y antigüedad media por departamento.
    """
    exito = True
    for clave, titulo, etiqueta_x, etiqueta_y, ruta in (
        ("equipos_por_departamento", "Equipos por departamento", "Departamento",
         "Número de equipos", config.CHART_DEPARTMENTS_FILE),
        ("equipos_por_estado", "Equipos por estado", "Estado",
         "Número de equipos", config.CHART_STATES_FILE),
        ("antiguedad_media_por_departamento", "Antigüedad media por departamento",
         "Departamento", "Antigüedad media (años)", config.CHART_AGE_FILE),
    ):
        if not generar_grafico_barras(auditoria[clave], titulo, etiqueta_x, etiqueta_y, ruta):
            exito = False
    return exito
