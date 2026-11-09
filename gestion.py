"""
Gestión del inventario.

Responsabilidad: altas, bajas lógicas, búsquedas, modificaciones, listados y
guardado del inventario actualizado. El inventario es una lista de
diccionarios que se recibe como parámetro; nunca es una variable global.
"""

import config


def pedir_datos_equipo():
    """
    Pide por consola los 13 campos de un equipo nuevo.

    Devuelve un diccionario con las columnas de config.COLUMNAS_CONTRATO.
    """
    raise NotImplementedError


def dar_alta_equipo(inventario, equipo):
    """
    Añade un equipo al inventario si cumple las reglas del contrato de datos
    (incluidos id e IP no repetidos respecto al inventario actual).

    Devuelve una tupla (exito, mensaje).
    """
    raise NotImplementedError


def buscar_por_id(inventario, id_equipo):
    """Devuelve el diccionario del equipo con ese id_equipo, o None."""
    raise NotImplementedError


def dar_baja_equipo(inventario, id_equipo):
    """
    Baja lógica: cambia el estado del equipo a "baja" sin borrarlo.

    Devuelve una tupla (exito, mensaje).
    """
    raise NotImplementedError


def buscar_equipos(inventario, campo, valor):
    """
    Busca equipos cuyo campo (uno de config.CAMPOS_BUSQUEDA) coincide con
    el valor, sin distinguir mayúsculas.

    Devuelve la lista de equipos encontrados.
    """
    raise NotImplementedError


def modificar_equipo(inventario, id_equipo, campo, nuevo_valor):
    """
    Cambia el estado, el departamento o el usuario asignado de un equipo,
    validando el nuevo valor con las reglas del contrato.

    Devuelve una tupla (exito, mensaje).
    """
    raise NotImplementedError


def filtrar_equipos(inventario, campo=None, valor=None):
    """
    Devuelve el inventario completo si no se indica filtro, o solo los
    equipos cuyo campo coincide con el valor.
    """
    raise NotImplementedError


def mostrar_equipos(equipos):
    """Muestra por consola una tabla legible con los equipos recibidos."""
    raise NotImplementedError


def guardar_inventario(inventario):
    """
    Guarda el inventario en config.UPDATED_FILE.

    El fichero original nunca se sobrescribe.
    """
    raise NotImplementedError
