"""
Programa principal de IT Asset Manager.

Responsabilidad: mostrar los menús, pedir opciones al usuario y llamar a las
funciones de los demás módulos. Aquí no hay lógica de validación ni cálculos.
Se ejecuta con:  python main.py
"""

from datetime import date

# Importamos los módulos del proyecto. main está arriba del todo en la
# "escalera" de dependencias: puede importar a todos, pero nadie importa main.
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


def pedir_opcion(opciones_validas):
    """
    Pide una opción por teclado hasta que el usuario escriba una de las
    opciones_validas. Devuelve la opción elegida como texto.
    """
    # .strip() quita espacios y saltos de línea: " 1 " se trata como "1".
    opcion = input("Elige una opción: ").strip()
    # Mientras lo escrito no sea una opción permitida, volvemos a preguntar.
    # Así una letra o un número fuera de rango nunca rompe el programa.
    while opcion not in opciones_validas:
        print("Opción no válida. Prueba otra vez.")
        opcion = input("Elige una opción: ").strip()
    return opcion


def mostrar_menu_principal(fecha_referencia, inventario_cargado):
    """Muestra el menú principal con la fecha de referencia en uso."""
    print()
    print("=== IT ASSET MANAGER ===")
    # Mostramos la fecha para saber siempre con qué fecha se calcula
    # (útil al comprobar los resultados con una fecha fija).
    print(f"Fecha de referencia: {fecha_referencia}")
    if inventario_cargado:
        print("Inventario: cargado")
    else:
        print("Inventario: sin cargar")
    print("1. Cargar y validar inventario")
    print("2. Gestión del inventario")
    print("3. Auditoría, informes y gráficos")
    print("4. Guardar y salir")
    print("0. Salir sin guardar")


def mostrar_menu_gestion():
    """Muestra el submenú de gestión del inventario."""
    print()
    print("--- GESTIÓN DEL INVENTARIO ---")
    print("1. Alta de equipo")
    print("2. Baja de equipo")
    print("3. Buscar equipos")
    print("4. Modificar equipo")
    print("5. Listar inventario")
    print("0. Volver")


def opcion_cargar():
    """
    Pide la ruta del CSV (Enter = config.INVENTORY_FILE), lo carga y lo
    valida. Devuelve la lista de equipos válidos, o None si falla.
    """
    raise NotImplementedError


def menu_gestion(inventario):
    """
    Bucle del submenú de gestión. Modifica la lista inventario recibida
    (altas, bajas, modificaciones) hasta que el usuario elige volver.
    """
    # inventario es la MISMA lista que tiene main(): si una función le hace
    # append o cambia un equipo, main() ve el cambio sin usar variables globales.
    opcion = None
    # El submenú se repite hasta que el usuario elige "0" (volver).
    while opcion != "0":
        mostrar_menu_gestion()
        opcion = pedir_opcion(("1", "2", "3", "4", "5", "0"))
        # try/except: si la función elegida aún no está implementada,
        # lanza NotImplementedError y aquí la capturamos para no romper.
        try:
            if opcion == "1":
                # Alta: pedimos los datos y gestion decide si son válidos.
                equipo = gestion.pedir_datos_equipo()
                exito, mensaje = gestion.dar_alta_equipo(inventario, equipo)
                print(mensaje)
            elif opcion == "2":
                # Baja lógica: solo necesitamos el identificador.
                id_equipo = input("id_equipo a dar de baja: ").strip()
                exito, mensaje = gestion.dar_baja_equipo(inventario, id_equipo)
                print(mensaje)
            elif opcion == "3":
                # Búsqueda: mostramos los campos permitidos desde config.
                campo = input(f"Campo {config.CAMPOS_BUSQUEDA}: ").strip()
                valor = input("Valor a buscar: ").strip()
                gestion.mostrar_equipos(gestion.buscar_equipos(inventario, campo, valor))
            elif opcion == "4":
                # Modificación: solo estado, departamento o usuario asignado.
                id_equipo = input("id_equipo a modificar: ").strip()
                campo = input(f"Campo {config.CAMPOS_MODIFICABLES}: ").strip()
                nuevo_valor = input("Nuevo valor: ").strip()
                exito, mensaje = gestion.modificar_equipo(inventario, id_equipo, campo, nuevo_valor)
                print(mensaje)
            elif opcion == "5":
                # Listado: sin filtro devuelve el inventario completo.
                gestion.mostrar_equipos(gestion.filtrar_equipos(inventario))
        except NotImplementedError:
            print("Esta opción aún no está implementada.")


def opcion_auditoria(inventario, fecha_referencia):
    """Calcula la auditoría, la muestra y genera informes y gráficos."""
    # Se calcula una sola vez y el mismo resultado se usa para la consola,
    # los ficheros y los gráficos: así siempre coinciden entre sí.
    auditoria = informes.calcular_auditoria(inventario, fecha_referencia)
    informes.mostrar_auditoria(auditoria)
    informes.generar_informes(auditoria, fecha_referencia)
    informes.generar_graficos(auditoria)


def main():
    """
    Punto de entrada. El inventario y la fecha de referencia son variables
    locales de esta función y se pasan como parámetros: no hay globales.
    """
    # La fecha se calcula UNA vez al arrancar y se pasa a quien la necesite.
    fecha_referencia = obtener_fecha_referencia()
    # None significa "todavía no se ha cargado ningún CSV".
    inventario = None
    opcion = None

    # El bucle termina con "4" (guardar y salir) o "0" (salir sin guardar).
    while opcion not in ("4", "0"):
        mostrar_menu_principal(fecha_referencia, inventario is not None)
        opcion = pedir_opcion(("1", "2", "3", "4", "0"))
        try:
            if opcion == "1":
                # Cargar (o volver a cargar) un CSV sustituye el inventario.
                inventario = opcion_cargar()
            elif opcion in ("2", "3", "4") and inventario is None:
                # Sin inventario no se puede gestionar, auditar ni guardar.
                print("Primero carga un inventario (opción 1).")
                if opcion == "4":
                    # Anulamos la opción para que el while no termine:
                    # no tiene sentido "guardar y salir" sin nada que guardar.
                    opcion = None
            elif opcion == "2":
                menu_gestion(inventario)
            elif opcion == "3":
                opcion_auditoria(inventario, fecha_referencia)
            elif opcion == "4":
                # Se guarda en salida/inventario_actualizado.csv;
                # el CSV original nunca se toca.
                gestion.guardar_inventario(inventario)
        except NotImplementedError:
            print("Esta opción aún no está implementada.")

    print("Hasta luego.")


# Solo arranca el menú si ejecutamos "python main.py" directamente.
# Si otro fichero hiciera "import main", el menú no se lanzaría solo.
if __name__ == "__main__":
    main()
