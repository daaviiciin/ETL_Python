"""
Programa principal de IT Asset Manager.

Responsabilidad: SOLO los menús. Muestra las opciones, lee la elección del
usuario y llama a la función correspondiente de acciones.py.
Se ejecuta con:  python main.py
"""

# main está arriba del todo en la "escalera" de dependencias: solo habla con
# acciones.py, que a su vez llama a los módulos de lógica.
import acciones


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


def menu_gestion(inventario):
    """
    Bucle del submenú de gestión. Llama a la acción elegida hasta que el
    usuario elige volver.
    """
    opcion = None
    # El submenú se repite hasta que el usuario elige "0" (volver).
    while opcion != "0":
        mostrar_menu_gestion()
        opcion = pedir_opcion(("1", "2", "3", "4", "5", "0"))
        # try/except: si la función elegida aún no está implementada,
        # lanza NotImplementedError y aquí la capturamos para no romper.
        try:
            if opcion == "1":
                acciones.accion_alta(inventario)
            elif opcion == "2":
                acciones.accion_baja(inventario)
            elif opcion == "3":
                acciones.accion_buscar(inventario)
            elif opcion == "4":
                acciones.accion_modificar(inventario)
            elif opcion == "5":
                acciones.accion_listar(inventario)
        except NotImplementedError:
            print("Esta opción aún no está implementada.")


def main():
    """
    Punto de entrada. El inventario y la fecha de referencia son variables
    locales de esta función y se pasan como parámetros: no hay globales.
    """
    # La fecha se calcula UNA vez al arrancar y se pasa a quien la necesite.
    fecha_referencia = acciones.obtener_fecha_referencia()
    # None significa "todavía no se ha cargado ningún CSV".
    inventario = None
    opcion = None

    # Solo termina con "4" si el guardado tiene éxito, o con "0".
    while opcion not in ("4", "0"):
        mostrar_menu_principal(fecha_referencia, inventario is not None)
        opcion = pedir_opcion(("1", "2", "3", "4", "0"))
        try:
            if opcion == "1":
                # Si la carga falla (devuelve None) conservamos el inventario
                # que hubiera antes, en vez de perderlo.
                nuevo_inventario = acciones.accion_cargar()
                if nuevo_inventario is not None:
                    inventario = nuevo_inventario
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
                acciones.accion_auditoria(inventario, fecha_referencia)
            elif opcion == "4":
                if not acciones.accion_guardar(inventario):
                    print("No se ha guardado el inventario. Puedes reintentar; los datos siguen en memoria.")
                    opcion = None
        except NotImplementedError:
            print("Esta opción aún no está implementada.")

    print("Hasta luego.")


# Solo arranca el menú si ejecutamos "python main.py" directamente.
# Si otro fichero hiciera "import main", el menú no se lanzaría solo.
if __name__ == "__main__":
    main()
