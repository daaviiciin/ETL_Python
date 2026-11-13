"""Navegación y errores del menú 3 sin leer ni escribir datos reales."""

import copy
import io
import unittest
from contextlib import ExitStack, redirect_stdout
from datetime import date
from unittest.mock import call, patch

import acciones
import main


class MenuAnalisisTests(unittest.TestCase):
    def setUp(self):
        self.fecha = date(2026, 1, 1)
        self.inventario = [{"id_equipo": "EQ-1", "estado": "activo"}]
        self.original = copy.deepcopy(self.inventario)
        self.auditoria = {"resultado": "simulado"}
        self.pila = ExitStack()
        self.addCleanup(self.pila.close)
        self.salida = self.pila.enter_context(redirect_stdout(io.StringIO()))
        self.calcular = self.pila.enter_context(patch(
            "acciones.informes.calcular_auditoria", return_value=self.auditoria
        ))
        self.mostrar = self.pila.enter_context(patch("acciones.informes.mostrar_auditoria"))
        self.informes = self.pila.enter_context(patch(
            "acciones.informes.generar_informes", return_value=True
        ))
        self.graficos = self.pila.enter_context(patch(
            "acciones.informes.generar_graficos", return_value=True
        ))
        self.cargar = self.pila.enter_context(patch(
            "acciones.accion_cargar", return_value=self.inventario
        ))
        self.guardar = self.pila.enter_context(patch("acciones.accion_guardar", return_value=True))
        self.pila.enter_context(patch("acciones.obtener_fecha_referencia", return_value=self.fecha))

    def tearDown(self):
        self.assertEqual(self.inventario, self.original)

    def navegar(self, opciones, inventario=None):
        with patch("builtins.input", side_effect=opciones):
            main.menu_analisis(self.inventario if inventario is None else inventario, self.fecha)

    def test_cada_opcion_y_contrato_de_acciones(self):
        for opcion, llamadas in (("1", (1, 0, 0)), ("2", (0, 1, 0)),
                                 ("3", (0, 0, 1)), ("4", (0, 1, 1))):
            with self.subTest(opcion=opcion):
                for mock in (self.calcular, self.mostrar, self.informes, self.graficos):
                    mock.reset_mock()
                self.navegar([opcion, "0"])
                self.calcular.assert_called_once_with(self.inventario, self.fecha)
                self.assertEqual((self.mostrar.call_count, self.informes.call_count,
                                  self.graficos.call_count), llamadas)
                if self.mostrar.called:
                    self.mostrar.assert_called_once_with(self.auditoria)
                if self.informes.called:
                    self.informes.assert_called_once_with(self.auditoria, self.fecha)
                if self.graficos.called:
                    self.graficos.assert_called_once_with(self.auditoria)

    def test_opcion_invalida_y_espacios(self):
        self.navegar(["incorrecta", "9", " 1 ", "0"])
        self.assertEqual(self.salida.getvalue().count("Opción no válida"), 2)
        self.mostrar.assert_called_once_with(self.auditoria)

    def test_volver_no_calcula_ni_exporta(self):
        self.navegar(["0"])
        self.calcular.assert_not_called()
        self.informes.assert_not_called()
        self.graficos.assert_not_called()

    def test_sin_inventario_no_pide_opciones(self):
        with patch("builtins.input") as entrada:
            main.menu_analisis(None, self.fecha)
        entrada.assert_not_called()
        self.calcular.assert_not_called()
        self.assertIn("Primero carga", self.salida.getvalue())

    def test_lista_vacia_cargada_permite_analisis(self):
        vacio = []
        self.navegar(["1", "0"], vacio)
        self.calcular.assert_called_once_with(vacio, self.fecha)

    def test_error_calculo_y_presentacion_permiten_reintentar(self):
        self.calcular.side_effect = [ValueError("fecha incorrecta"), self.auditoria, self.auditoria]
        self.mostrar.side_effect = [RuntimeError("fallo consola"), None]
        self.navegar(["1", "1", "1", "0"])
        self.assertEqual(self.calcular.call_count, 3)
        self.assertEqual(self.mostrar.call_count, 2)
        self.assertEqual(self.salida.getvalue().count("Puedes reintentar"), 2)

    def test_fallo_exportaciones_y_reintento(self):
        self.informes.side_effect = [False, PermissionError("bloqueado"), True]
        self.graficos.side_effect = [RuntimeError("fallo gráfico"), False, True]
        self.navegar(["4", "4", "4", "0"])
        self.assertEqual(self.informes.call_count, 3)
        self.assertEqual(self.graficos.call_count, 3)
        self.assertEqual(self.salida.getvalue().count("Puedes reintentar"), 4)
        for llamada in self.calcular.call_args_list:
            self.assertIs(llamada.args[0], self.inventario)

    def test_resultado_booleano_accion(self):
        self.assertTrue(acciones.accion_analisis(self.inventario, self.fecha, "4"))
        self.informes.return_value = False
        self.assertFalse(acciones.accion_analisis(self.inventario, self.fecha, "4"))

    def test_interrupciones_vuelven_al_menu_principal(self):
        for error in (EOFError, KeyboardInterrupt):
            with self.subTest(error=error), patch("builtins.input", side_effect=error):
                main.menu_analisis(self.inventario, self.fecha)
        self.calcular.assert_not_called()
        self.assertEqual(self.salida.getvalue().count("Volviendo al menú principal"), 2)

    def test_main_bloquea_opcion_3_sin_carga(self):
        with patch("builtins.input", side_effect=["3", "0"]):
            main.main()
        self.calcular.assert_not_called()
        self.assertIn("Primero carga", self.salida.getvalue())

    def test_main_carga_navega_vuelve_y_conserva_inventario(self):
        with patch("builtins.input", side_effect=["1", "3", "1", "0", "3", "4", "0", "4"]):
            main.main()
        self.cargar.assert_called_once_with()
        self.assertEqual(self.calcular.call_args_list, [
            call(self.inventario, self.fecha), call(self.inventario, self.fecha)
        ])
        for llamada in self.calcular.call_args_list:
            self.assertIs(llamada.args[0], self.inventario)
        self.guardar.assert_called_once_with(self.inventario)
        self.assertIn("Hasta luego.", self.salida.getvalue())


if __name__ == "__main__":
    unittest.main()
