"""
Gestión del inventario.

Responsabilidad: altas, bajas lógicas, búsquedas, modificaciones, listados y
guardado del inventario actualizado. El inventario es una lista de
diccionarios que se recibe como parámetro; nunca es una variable global.
Este módulo no pide datos por teclado: eso lo hace acciones.py.
"""

import carga_validacion
import config


# ---------------------------------------------------------------------------
# Altas
# ---------------------------------------------------------------------------
def obtener_ids_e_ips(inventario):
    """
    Devuelve una tupla (ids, ips) con dos conjuntos: los id_equipo y las
    direcciones IP que ya usa el inventario, para detectar duplicados.
    """
    ids = set()
    ips = set()
    for equipo in inventario:
        ids.add(equipo["id_equipo"])
        # La IP es opcional: solo guardamos las que vienen rellenas.
        if not carga_validacion.esta_vacio(equipo["direccion_ip"]):
            ips.add(equipo["direccion_ip"])
    return ids, ips


def validar_dato_alta(campo, equipo, inventario):
    """
    Valida un único campo de un equipo que se está dando de alta.

    equipo es el diccionario con los campos introducidos hasta ahora.
    Usa exactamente las mismas reglas que la carga del CSV.
    Devuelve None si es válido, o el motivo del error (texto legible).
    """
    ids, ips = obtener_ids_e_ips(inventario)
    codigo = carga_validacion.validar_campo(campo, equipo, ids, ips)
    if codigo is None:
        return None
    return config.MOTIVOS_ERROR[codigo]


def dar_alta_equipo(inventario, equipo):
    """
    Añade un equipo al inventario si cumple las reglas del contrato de datos
    (incluidos id e IP no repetidos respecto al inventario actual).

    Devuelve una tupla (exito, mensaje).
    """
    # Aunque acciones.py ya valida campo a campo, volvemos a validar la
    # fila completa: así esta función es segura aunque se llame desde otro
    # sitio con datos sin revisar.
    ids, ips = obtener_ids_e_ips(inventario)
    codigo = carga_validacion.validar_fila(equipo, ids, ips)
    if codigo is not None:
        return False, f"Alta rechazada: {config.MOTIVOS_ERROR[codigo]}"
    inventario.append(equipo)
    return True, f"Equipo {equipo['id_equipo']} dado de alta."


# ---------------------------------------------------------------------------
# Bajas, búsquedas y modificaciones
# ---------------------------------------------------------------------------
def buscar_por_id(inventario, id_equipo):
    """Devuelve el diccionario del equipo con ese id_equipo, o None."""
    for equipo in inventario:
        if equipo["id_equipo"] == id_equipo:
            return equipo
    return None


def dar_baja_equipo(inventario, id_equipo):
    """
    Baja lógica: cambia el estado del equipo a "baja" sin borrarlo.

    Devuelve una tupla (exito, mensaje).
    """
    equipo = buscar_por_id(inventario, id_equipo)
    if equipo is None:
        return False, f"No existe ningún equipo con id {id_equipo}."
    if equipo["estado"] == config.ESTADO_BAJA:
        return False, f"El equipo {id_equipo} ya estaba de baja."
    # No se elimina de la lista: solo cambia su estado. Así sigue contando
    # en la auditoría y queda constancia de que existió.
    equipo["estado"] = config.ESTADO_BAJA
    return True, f"Equipo {id_equipo} dado de baja."


def buscar_equipos(inventario, campo, valor):
    """
    Busca equipos cuyo campo (uno de config.CAMPOS_BUSQUEDA) coincide con
    el valor, sin distinguir mayúsculas.

    En hostname y departamento basta con que el valor aparezca dentro del
    texto; en id_equipo y tipo la coincidencia debe ser exacta.
    Devuelve la lista de equipos encontrados.
    """
    # casefold() es como lower() pero más completo con letras especiales.
    buscado = valor.strip().casefold()
    encontrados = []
    for equipo in inventario:
        texto = (equipo.get(campo) or "").casefold()
        if campo in config.CAMPOS_BUSQUEDA_PARCIAL:
            coincide = buscado in texto
        else:
            coincide = buscado == texto
        if coincide:
            encontrados.append(equipo)
    return encontrados


def modificar_equipo(inventario, id_equipo, campo, nuevo_valor):
    """
    Cambia el estado, el departamento o el usuario asignado de un equipo,
    validando el nuevo valor con las reglas del contrato.

    Devuelve una tupla (exito, mensaje).
    """
    if campo not in config.CAMPOS_MODIFICABLES:
        return False, f"El campo {campo} no se puede modificar."
    equipo = buscar_por_id(inventario, id_equipo)
    if equipo is None:
        return False, f"No existe ningún equipo con id {id_equipo}."

    # Validamos el nuevo valor con la misma regla que se usa en la carga.
    # Los conjuntos de duplicados van vacíos: estos campos no los usan.
    codigo = carga_validacion.validar_campo(campo, {campo: nuevo_valor}, set(), set())
    if codigo is not None:
        return False, f"Modificación rechazada: {config.MOTIVOS_ERROR[codigo]}"

    anterior = equipo[campo]
    equipo[campo] = nuevo_valor
    return True, f"{id_equipo}: {campo} cambiado de '{anterior}' a '{nuevo_valor}'."


# ---------------------------------------------------------------------------
# Listados y guardado
# ---------------------------------------------------------------------------
def filtrar_equipos(inventario, campo=None, valor=None):
    """
    Devuelve el inventario completo si no se indica filtro, o solo los
    equipos cuyo campo coincide con el valor (sin distinguir mayúsculas).
    """
    if campo is None:
        # list() devuelve una copia: quien la reciba no altera el orden
        # ni el contenido de la lista original al recorrerla.
        return list(inventario)
    buscado = valor.strip().casefold()
    return [e for e in inventario if (e.get(campo) or "").casefold() == buscado]


def mostrar_equipos(equipos):
    """Muestra por consola una tabla legible con los equipos recibidos."""
    if not equipos:
        print("No hay equipos que mostrar.")
        return

    columnas = config.COLUMNAS_LISTADO
    # Ancho de cada columna = el texto más largo entre la cabecera y los
    # valores de esa columna. Así la tabla queda alineada con cualquier dato.
    anchos = {}
    for columna in columnas:
        valores = [len(e.get(columna) or "") for e in equipos]
        anchos[columna] = max([len(columna)] + valores)

    cabecera = "  ".join(c.ljust(anchos[c]) for c in columnas)
    print(cabecera)
    print("-" * len(cabecera))
    for equipo in equipos:
        print("  ".join((equipo.get(c) or "").ljust(anchos[c]) for c in columnas))
    # Singular o plural según el número, para no escribir "1 equipos".
    palabra = "equipo" if len(equipos) == 1 else "equipos"
    print(f"Total: {len(equipos)} {palabra}")


def guardar_inventario(inventario):
    """
    Guarda el inventario en config.UPDATED_FILE.

    El fichero original nunca se sobrescribe.
    Devuelve None si se ha guardado bien, o un mensaje de error si no.
    """
    # Solo las 13 columnas del contrato: la clave interna linea_csv y
    # cualquier columna extra del CSV original no se escriben.
    return carga_validacion.escribir_csv(config.UPDATED_FILE, inventario, config.COLUMNAS_CONTRATO)
