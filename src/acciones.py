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


def elegir_de_lista(texto, opciones):
    """
    Muestra las opciones numeradas y pide elegir una por su número.
    Devuelve la opción elegida, o None si se pulsa Enter sin escribir nada.
    """
    print(texto)
    for numero, opcion in enumerate(opciones, start=1):
        print(f"  {numero}. {opcion}")
    while True:
        respuesta = input("Número (Enter = cancelar): ").strip()
        if respuesta == "":
            return None
        # isdecimal() evita que int() falle con letras o símbolos.
        if respuesta.isdecimal() and 1 <= int(respuesta) <= len(opciones):
            return opciones[int(respuesta) - 1]
        print("Número no válido. Prueba otra vez.")


def mostrar_resultados_ficheros(resultados):
    """
    Muestra, para cada (ruta, error), si el fichero se generó o por qué no.
    Devuelve True si se generaron todos.
    """
    todo_bien = True
    for ruta, error in resultados:
        if error is None:
            print(f"  Generado: {carga_validacion.ruta_para_mostrar(ruta)}")
        else:
            print(f"  Aviso: {error}")
            todo_bien = False
    return todo_bien


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
    print()
    print("Ficheros de salida:")
    mostrar_resultados_ficheros(informes.generar_informes(auditoria))
    mostrar_resultados_ficheros(informes.generar_graficos(auditoria))


def accion_guardar(inventario):
    """
    Guarda el inventario en salida/inventario_actualizado.csv.
    El CSV original nunca se toca. Devuelve True si se guardó bien.
    """
    error = gestion.guardar_inventario(inventario)
    if error is not None:
        print(f"Aviso: {error}")
        return False
    print(f"Inventario guardado en {carga_validacion.ruta_para_mostrar(config.UPDATED_FILE)}")
    return True


# ---------------------------------------------------------------------------
# Submenú de gestión
# inventario es la MISMA lista que tiene main(): si una función le hace
# append o cambia un equipo, main() ve el cambio sin usar variables globales.
# ---------------------------------------------------------------------------
def accion_alta(inventario):
    """
    Pide uno a uno los campos de un equipo nuevo. Cada dato se valida en
    cuanto se escribe y, si no es válido, se vuelve a pedir. Escribiendo
    config.PALABRA_CANCELAR se abandona el alta sin añadir nada.
    """
    print(f"Alta de equipo (escribe '{config.PALABRA_CANCELAR}' para salir).")
    equipo = {}
    # Se piden en el orden del contrato: así fecha_compra ya existe cuando
    # se valida fin_garantia, que la necesita para compararlas.
    for campo in config.COLUMNAS_CONTRATO:
        while True:
            # Aquí NO usamos strip(): " activo" debe rechazarse igual que en
            # la carga del CSV, no corregirse en silencio.
            valor = input(f"  {campo}: ")
            if valor.strip().casefold() == config.PALABRA_CANCELAR:
                print("Alta cancelada.")
                return
            equipo[campo] = valor
            motivo = gestion.validar_dato_alta(campo, equipo, inventario)
            if motivo is None:
                break
            print(f"  No válido: {motivo}")

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
    campo = elegir_de_lista("¿Por qué campo quieres buscar?", config.CAMPOS_BUSQUEDA)
    if campo is None:
        return
    valor = input("Valor a buscar: ").strip()
    gestion.mostrar_equipos(gestion.buscar_equipos(inventario, campo, valor))


def accion_modificar(inventario):
    """Pide un id_equipo, un campo modificable y su nuevo valor."""
    id_equipo = input("id_equipo a modificar: ").strip()
    if gestion.buscar_por_id(inventario, id_equipo) is None:
        print(f"No existe ningún equipo con id {id_equipo}.")
        return
    # Solo estado, departamento o usuario asignado.
    campo = elegir_de_lista("¿Qué campo quieres modificar?", config.CAMPOS_MODIFICABLES)
    if campo is None:
        return
    if campo == "estado":
        # Para el estado ofrecemos la lista: así no se puede escribir mal.
        nuevo_valor = elegir_de_lista("Nuevo estado:", config.ESTADOS_VALIDOS)
        if nuevo_valor is None:
            return
    else:
        nuevo_valor = input("Nuevo valor: ")
    exito, mensaje = gestion.modificar_equipo(inventario, id_equipo, campo, nuevo_valor)
    print(mensaje)


def accion_listar(inventario):
    """Muestra el inventario completo o filtrado por tipo, departamento o estado."""
    campo = elegir_de_lista("¿Filtrar por algún campo? (Enter = listado completo)", config.CAMPOS_FILTRO)
    if campo is None:
        gestion.mostrar_equipos(gestion.filtrar_equipos(inventario))
        return
    valor = input(f"Valor de {campo}: ").strip()
    gestion.mostrar_equipos(gestion.filtrar_equipos(inventario, campo, valor))
