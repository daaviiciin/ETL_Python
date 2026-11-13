"""
Acciones del menú de IT Asset Manager.

Responsabilidad: hacer de intermediario entre el menú (main.py) y los módulos
de lógica. Cada opción del menú corresponde a una función de este módulo, que
pide por teclado los datos que hagan falta y llama a carga_validacion,
gestion o informes. Aquí no se valida ni se calcula nada.
"""

from datetime import date
from pathlib import Path

import carga_validacion
import config
import gestion
import informes


def obtener_fecha_referencia():
    """
    Devuelve la fecha de referencia para los cálculos.

    Usa config.FECHA_REFERENCIA_FIJA si tiene valor (para repetir los
    cálculos con una fecha concreta) y date.today() en caso contrario.
    """
    # Si en config.py se ha fijado una fecha (por ejemplo date(2026, 11, 2)),
    # usamos esa para que los cálculos den siempre el mismo resultado.
    if config.FECHA_REFERENCIA_FIJA is not None:
        return config.FECHA_REFERENCIA_FIJA
    # Si vale None, funcionamiento normal: la fecha de hoy.
    return date.today()


# ---------------------------------------------------------------------------
# Menú principal
# ---------------------------------------------------------------------------
def accion_cargar():
    """
    Pide la ruta del CSV (Enter = config.INVENTORY_FILE), lo carga y lo
    valida. Devuelve la lista de equipos válidos, o None si falla.
    """
    # Mostramos la ruta por defecto relativa al proyecto para que sea corta.
    por_defecto = config.INVENTORY_FILE.relative_to(config.BASE_DIR)
    # strip('"') quita las comillas que añade Windows al "Copiar como ruta".
    texto = input(f"Ruta del CSV (Enter = {por_defecto}): ").strip().strip('"')

    if texto == "":
        ruta = config.INVENTORY_FILE
    else:
        ruta = Path(texto)
        # Una ruta relativa como "datos/otro.csv" se interpreta desde la
        # carpeta del proyecto, aunque el programa se lance desde otro sitio.
        if not ruta.is_absolute():
            ruta = config.BASE_DIR / ruta

    return carga_validacion.cargar_y_validar(ruta)


def accion_auditoria(inventario, fecha_referencia):
    """Calcula la auditoría, la muestra y genera informes y gráficos."""
    # Se calcula una sola vez y el mismo resultado se usa para la consola,
    # los ficheros y los gráficos: así siempre coinciden entre sí.
    auditoria = informes.calcular_auditoria(inventario, fecha_referencia)
    informes.mostrar_auditoria(auditoria)
    informes.generar_informes(auditoria, fecha_referencia)
    informes.generar_graficos(auditoria)


def accion_guardar(inventario):
    """
    Guarda el inventario en salida/inventario_actualizado.csv.
    El CSV original nunca se toca.
    """
    return gestion.guardar_inventario(inventario)


def accion_analisis(inventario, fecha_referencia, opcion):
    """Ejecuta la operación elegida sobre una única auditoría en memoria."""
    auditoria = informes.calcular_auditoria(inventario, fecha_referencia)
    if opcion == "1":
        informes.mostrar_auditoria(auditoria)
        return True

    exito = True
    operaciones = []
    if opcion in ("2", "4"):
        operaciones.append(("informes", informes.generar_informes, (auditoria, fecha_referencia)))
    if opcion in ("3", "4"):
        operaciones.append(("gráficos", informes.generar_graficos, (auditoria,)))
    for nombre, funcion, argumentos in operaciones:
        try:
            if not funcion(*argumentos):
                print(f"No se han generado todos los {nombre}. Puedes reintentar.")
                exito = False
        except Exception as error:
            print(f"Error al generar {nombre}: {error}. Puedes reintentar.")
            exito = False
    return exito


# ---------------------------------------------------------------------------
# Submenú de gestión
# inventario es la MISMA lista que tiene main(): si una función le hace
# append o cambia un equipo, main() ve el cambio sin usar variables globales.
# ---------------------------------------------------------------------------
def accion_alta(inventario):
    """Pide los datos de un equipo nuevo e intenta darlo de alta."""
    # Pedimos los datos y gestion decide si son válidos.
    equipo = gestion.pedir_datos_equipo()
    exito, mensaje = gestion.dar_alta_equipo(inventario, equipo)
    print(mensaje)


def accion_baja(inventario):
    """Pide un id_equipo y le aplica la baja lógica."""
    # Baja lógica: solo necesitamos el identificador.
    id_equipo = input("id_equipo a dar de baja: ").strip()
    exito, mensaje = gestion.dar_baja_equipo(inventario, id_equipo)
    print(mensaje)


def accion_buscar(inventario):
    """Pide un campo y un valor, y muestra los equipos que coinciden."""
    # Mostramos los campos permitidos desde config.
    campo = input(f"Campo {config.CAMPOS_BUSQUEDA}: ").strip()
    valor = input("Valor a buscar: ").strip()
    gestion.mostrar_equipos(gestion.buscar_equipos(inventario, campo, valor))


def accion_modificar(inventario):
    """Pide un id_equipo, un campo modificable y su nuevo valor."""
    # Solo estado, departamento o usuario asignado.
    id_equipo = input("id_equipo a modificar: ").strip()
    campo = input(f"Campo {config.CAMPOS_MODIFICABLES}: ").strip()
    nuevo_valor = input("Nuevo valor: ").strip()
    exito, mensaje = gestion.modificar_equipo(inventario, id_equipo, campo, nuevo_valor)
    print(mensaje)


def accion_listar(inventario):
    """Muestra el inventario completo."""
    # Sin filtro, filtrar_equipos devuelve el inventario completo.
    gestion.mostrar_equipos(gestion.filtrar_equipos(inventario))
