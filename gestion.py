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
    equipo = dict.fromkeys(config.COLUMNAS_CONTRATO, "")
    try:
        for campo in config.COLUMNAS_CONTRATO:
            equipo[campo] = input(f"{campo}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nAlta cancelada.")
        # Un ID vacío garantiza que la acción existente rechace el alta.
        equipo["id_equipo"] = ""
    return equipo


def dar_alta_equipo(inventario, equipo):
    """
    Añade un equipo al inventario si cumple las reglas del contrato de datos
    (incluidos id e IP no repetidos respecto al inventario actual).

    Devuelve una tupla (exito, mensaje).
    """
    import carga_validacion

    if not isinstance(equipo, dict):
        return False, "El equipo debe ser un diccionario con los 13 campos del contrato."
    faltantes = carga_validacion.obtener_columnas_faltantes(equipo)
    if faltantes:
        return False, "Faltan campos obligatorios: " + ", ".join(faltantes)
    if any(
        valor is not None and not isinstance(valor, str)
        for campo, valor in equipo.items() if campo in config.COLUMNAS_CONTRATO
    ):
        return False, "Los campos del equipo deben contener texto o None."

    # Conservamos únicamente el contrato en una copia independiente.
    nuevo_equipo = {campo: equipo[campo] for campo in config.COLUMNAS_CONTRATO}
    ids_validos = {actual["id_equipo"] for actual in inventario}
    ips_validas = {
        actual["direccion_ip"] for actual in inventario
        if not carga_validacion.esta_vacio(actual["direccion_ip"])
    }
    codigo = carga_validacion.validar_fila(nuevo_equipo, ids_validos, ips_validas)
    if codigo is not None:
        return False, f"No se ha dado de alta el equipo: {config.MOTIVOS_ERROR[codigo]}"

    inventario.append(nuevo_equipo)
    return True, f"Equipo {nuevo_equipo['id_equipo']} dado de alta correctamente."


def buscar_por_id(inventario, id_equipo):
    """Devuelve el diccionario del equipo con ese id_equipo, o None."""
    for equipo in inventario:
        if equipo["id_equipo"].casefold() == id_equipo.casefold():
            return equipo
    return None


def dar_baja_equipo(inventario, id_equipo):
    """
    Baja lógica: cambia el estado del equipo a "baja" sin borrarlo.

    Devuelve una tupla (exito, mensaje).
    """
    equipo = buscar_por_id(inventario, id_equipo)
    if equipo is None:
        return False, f"No se encuentra el equipo con ID {id_equipo}."
    if equipo["estado"] == config.ESTADO_BAJA:
        return False, f"El equipo {equipo['id_equipo']} ya está de baja."
    equipo["estado"] = config.ESTADO_BAJA
    return True, f"Equipo {equipo['id_equipo']} dado de baja correctamente."


def buscar_equipos(inventario, campo, valor):
    """
    Busca equipos cuyo campo (uno de config.CAMPOS_BUSQUEDA) coincide con
    el valor, sin distinguir mayúsculas.

    Devuelve la lista de equipos encontrados.
    """
    if campo not in config.CAMPOS_BUSQUEDA:
        print(f"Campo de búsqueda no válido. Campos permitidos: {config.CAMPOS_BUSQUEDA}")
        return []
    return [
        equipo for equipo in inventario
        if equipo[campo].casefold() == valor.casefold()
    ]


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
    if campo is None and valor is None:
        return list(inventario)
    if campo is None or valor is None:
        print("Indica tanto el campo como el valor del filtro.")
        return []
    return buscar_equipos(inventario, campo, valor)


def mostrar_equipos(equipos):
    """Muestra por consola una tabla legible con los equipos recibidos."""
    if not equipos:
        print("No hay equipos para mostrar.")
        return

    columnas = config.COLUMNAS_CONTRATO
    # Preparamos solo la representación: los registros originales no cambian.
    filas = [
        [" ".join(str(equipo.get(campo) or "").split()) for campo in columnas]
        for equipo in equipos
    ]
    anchos = [
        max(len(campo), max(len(fila[indice]) for fila in filas))
        for indice, campo in enumerate(columnas)
    ]
    print(" | ".join(campo.ljust(ancho) for campo, ancho in zip(columnas, anchos)))
    print("-+-".join("-" * ancho for ancho in anchos))
    for fila in filas:
        print(" | ".join(valor.ljust(ancho) for valor, ancho in zip(fila, anchos)))
    print(f"Total de equipos: {len(equipos)}")


def guardar_inventario(inventario):
    """
    Guarda el inventario en config.UPDATED_FILE.

    El fichero original nunca se sobrescribe.
    """
    raise NotImplementedError
