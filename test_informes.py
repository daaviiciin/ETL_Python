"""Pruebas de cálculo y presentación de auditoría, con datos en memoria."""

import copy
import csv
import io
import tempfile
import unittest
from contextlib import ExitStack, redirect_stdout
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.image import imread

import config
import informes


class AuditoriaTests(unittest.TestCase):
    def setUp(self):
        self.fecha = date(2026, 1, 1)
        base = dict.fromkeys(config.COLUMNAS_CONTRATO, "")
        base.update(
            id_equipo="EQ-1", hostname="PC-1", departamento="IT",
            estado="activo", sistema_operativo="Windows", version_so="7",
            fecha_compra="2025-01-01", fin_garantia="2026-01-01",
            precio_eur="0.10",
        )
        self.equipos = [base, dict(
            base, id_equipo="EQ-2", hostname="PC-2", estado="baja",
            sistema_operativo="macOS", version_so="12", precio_eur="0.20",
            fin_garantia=(self.fecha + timedelta(days=config.DIAS_AVISO_GARANTIA)).isoformat(),
        )]

    def test_indicadores_y_datos_originales(self):
        original = copy.deepcopy(self.equipos)
        resultado = informes.calcular_auditoria(self.equipos, self.fecha)
        self.assertEqual(resultado, {
            "equipos_por_departamento": {"IT": 2},
            "equipos_por_estado": {"activo": 1, "baja": 1},
            "equipos_so_obsoleto": [self.equipos[0]],
            "garantias_proximas": self.equipos,
            "antiguedad_media_por_departamento": {"IT": 1.0},
            "coste_por_departamento": {"IT": 0.3},
        })
        self.assertEqual(self.equipos, original)

    def test_fecha_recibida_y_limites(self):
        resultado = informes.calcular_auditoria(
            self.equipos, self.fecha + timedelta(days=1)
        )
        self.assertEqual(resultado["garantias_proximas"], [self.equipos[1]])
        self.assertEqual(resultado["antiguedad_media_por_departamento"], {"IT": 1.0})

    def test_presentacion_no_recalcula_ni_modifica(self):
        auditoria = informes.calcular_auditoria(self.equipos, self.fecha)
        original = copy.deepcopy(auditoria)
        salida = io.StringIO()
        with patch.object(informes, "calcular_auditoria", side_effect=AssertionError), redirect_stdout(salida):
            informes.mostrar_auditoria(auditoria)
        for texto in ("IT: 2 equipos", "activo: 1 equipos", "baja: 1 equipos",
                      "IT: 1.00 años", "IT: 0.30 EUR", "EQ-1", "PC-2", "2026-01-01"):
            self.assertIn(texto, salida.getvalue())
        self.assertEqual(auditoria, original)

    def test_inventario_vacio(self):
        auditoria = informes.calcular_auditoria([], self.fecha)
        self.assertEqual(auditoria["equipos_so_obsoleto"], [])
        self.assertEqual(auditoria["garantias_proximas"], [])
        for clave in ("equipos_por_departamento", "equipos_por_estado",
                      "antiguedad_media_por_departamento", "coste_por_departamento"):
            self.assertEqual(auditoria[clave], {})
        salida = io.StringIO()
        with redirect_stdout(salida):
            informes.mostrar_auditoria(auditoria)
        self.assertEqual(salida.getvalue().count("Sin datos."), 4)
        self.assertEqual(salida.getvalue().count("Sin equipos."), 2)

    def rutas_temporales(self, pila, raiz):
        rutas = [raiz / "salida" / nombre for nombre in (
            "informe_auditoria.txt", "equipos_so_obsoleto.csv", "garantias_proximas.csv"
        )]
        for constante, ruta in zip(
            ("AUDIT_REPORT_FILE", "OBSOLETE_OS_FILE", "WARRANTY_FILE"), rutas
        ):
            pila.enter_context(patch.object(config, constante, ruta))
        return rutas

    def test_exportacion_y_lectura(self):
        self.equipos[0]["usuario_asignado"] = "Ana, Muñoz\nSoporte"
        self.equipos[0]["linea_csv"] = 2
        auditoria = informes.calcular_auditoria(self.equipos, self.fecha)
        original = copy.deepcopy(auditoria)
        with tempfile.TemporaryDirectory() as directorio, ExitStack() as pila:
            rutas = self.rutas_temporales(pila, Path(directorio))
            pila.enter_context(redirect_stdout(io.StringIO()))
            pila.enter_context(patch.object(informes, "calcular_auditoria", side_effect=AssertionError))
            self.assertTrue(informes.generar_informes(auditoria, self.fecha))
            texto = rutas[0].read_text(encoding=config.ENCODING_ESCRITURA)
            for fragmento in ("2026-01-01", "Antigüedad media", "0.30 EUR", "EQ-1"):
                self.assertIn(fragmento, texto)
            for ruta, clave in zip(rutas[1:], ("equipos_so_obsoleto", "garantias_proximas")):
                with ruta.open(encoding=config.ENCODING_LECTURA, newline="") as fichero:
                    lector = csv.DictReader(fichero, delimiter=config.SEPARADOR)
                    self.assertEqual(tuple(lector.fieldnames), config.COLUMNAS_CONTRATO)
                    self.assertEqual(list(lector), [
                        {campo: equipo[campo] for campo in config.COLUMNAS_CONTRATO}
                        for equipo in auditoria[clave]
                    ])
            self.assertEqual(set(rutas[0].parent.iterdir()), set(rutas))
        self.assertEqual(auditoria, original)

    def test_exportacion_vacia(self):
        auditoria = informes.calcular_auditoria([], self.fecha)
        with tempfile.TemporaryDirectory() as directorio, ExitStack() as pila:
            rutas = self.rutas_temporales(pila, Path(directorio))
            pila.enter_context(redirect_stdout(io.StringIO()))
            self.assertTrue(informes.generar_informes(auditoria, self.fecha))
            self.assertIn("Sin datos.", rutas[0].read_text(encoding="utf-8"))
            for ruta in rutas[1:]:
                with ruta.open(encoding="utf-8", newline="") as fichero:
                    self.assertEqual(list(csv.reader(fichero)), [list(config.COLUMNAS_CONTRATO)])

    def test_error_reemplazo_conserva_informes_y_datos(self):
        auditoria = informes.calcular_auditoria(self.equipos, self.fecha)
        original = copy.deepcopy(auditoria)
        with tempfile.TemporaryDirectory() as directorio, ExitStack() as pila:
            rutas = self.rutas_temporales(pila, Path(directorio))
            rutas[0].parent.mkdir()
            for ruta in rutas:
                ruta.write_text("anterior", encoding="utf-8")
            salida = pila.enter_context(redirect_stdout(io.StringIO()))
            with patch.object(Path, "replace", side_effect=PermissionError("bloqueado")):
                self.assertFalse(informes.generar_informes(auditoria, self.fecha))
            for ruta in rutas:
                self.assertEqual(ruta.read_text(encoding="utf-8"), "anterior")
            self.assertEqual(set(rutas[0].parent.iterdir()), set(rutas))
            self.assertNotIn("Informe guardado", salida.getvalue())
        self.assertEqual(auditoria, original)

    def test_graficos_png_e_indicadores(self):
        auditoria = informes.calcular_auditoria(self.equipos, self.fecha)
        original = copy.deepcopy(auditoria)
        with tempfile.TemporaryDirectory() as directorio, ExitStack() as pila:
            rutas = [Path(directorio) / "graficos" / nombre for nombre in (
                "departamentos.png", "estados.png", "antiguedad.png"
            )]
            for constante, ruta in zip(("CHART_DEPARTMENTS_FILE", "CHART_STATES_FILE", "CHART_AGE_FILE"), rutas):
                pila.enter_context(patch.object(config, constante, ruta))
            pila.enter_context(redirect_stdout(io.StringIO()))
            with patch.object(informes, "generar_grafico_barras", wraps=informes.generar_grafico_barras) as generar:
                self.assertTrue(informes.generar_graficos(auditoria))
            for llamada, clave in zip(generar.call_args_list, (
                "equipos_por_departamento", "equipos_por_estado", "antiguedad_media_por_departamento"
            )):
                self.assertIs(llamada.args[0], auditoria[clave])
            for ruta in rutas:
                self.assertEqual(ruta.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
                imagen = imread(ruta)
                self.assertGreater(imagen.shape[0], 500)
                self.assertGreater(imagen.shape[1], 800)
            self.assertEqual(set(rutas[0].parent.iterdir()), set(rutas))
        self.assertEqual(auditoria, original)

    def test_grafico_etiquetas_largas_y_vacio(self):
        guardar = Figure.savefig
        observados = []

        def inspeccionar(figura, *args, **kwargs):
            eje = figura.axes[0]
            observados.append((
                [texto.get_text() for texto in eje.get_xticklabels()],
                [texto.get_text() for texto in eje.texts],
                eje.get_title(), eje.get_xlabel(), eje.get_ylabel(),
            ))
            return guardar(figura, *args, **kwargs)

        datos = {"Departamento de investigación y operaciones internacionales": 1.25,
                 "NombreSinEspacios" * 8: 2.5}
        original = copy.deepcopy(datos)
        with tempfile.TemporaryDirectory() as directorio, redirect_stdout(io.StringIO()):
            ruta = Path(directorio) / "grafico.png"
            with patch.object(Figure, "savefig", inspeccionar):
                self.assertTrue(informes.generar_grafico_barras(datos, "Título", "Grupo", "Años", ruta))
                self.assertTrue(informes.generar_grafico_barras({}, "Vacío", "Grupo", "Años", ruta))
            self.assertTrue(all("\n" in etiqueta for etiqueta in observados[0][0]))
            self.assertIn("1.25", observados[0][1])
            self.assertEqual(observados[0][2:], ("Título", "Grupo", "Años"))
            self.assertIn("Sin datos para mostrar", observados[1][1])
            self.assertGreater(imread(ruta).size, 0)
        self.assertEqual(datos, original)

    def test_grafico_errores_conservan_archivo_anterior(self):
        datos = {"IT": 2}
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "grafico.png"
            ruta.write_bytes(b"anterior")
            for objetivo in ("savefig", "replace"):
                salida = io.StringIO()
                parche = patch.object(Figure, "savefig", side_effect=OSError("disco lleno")) if objetivo == "savefig" else patch.object(Path, "replace", side_effect=PermissionError("bloqueado"))
                with parche, redirect_stdout(salida):
                    self.assertFalse(informes.generar_grafico_barras(datos, "Título", "X", "Y", ruta))
                self.assertEqual(ruta.read_bytes(), b"anterior")
                self.assertEqual(list(Path(directorio).iterdir()), [ruta])
                self.assertNotIn("Gráfico guardado", salida.getvalue())
        self.assertEqual(datos, {"IT": 2})

    def test_generar_graficos_continua_tras_fallo(self):
        auditoria = informes.calcular_auditoria([], self.fecha)
        with patch.object(informes, "generar_grafico_barras", side_effect=[False, True, True]) as generar:
            self.assertFalse(informes.generar_graficos(auditoria))
        self.assertEqual(generar.call_count, 3)

    def test_error_csv_continua_y_conserva_destino(self):
        import carga_validacion

        auditoria = informes.calcular_auditoria(self.equipos, self.fecha)
        escribir = carga_validacion.escribir_csv
        llamadas = 0

        def fallar_primero(ruta, filas, columnas):
            nonlocal llamadas
            llamadas += 1
            if llamadas == 1:
                Path(ruta).write_text("parcial", encoding="utf-8")
                return "disco lleno"
            return escribir(ruta, filas, columnas)

        with tempfile.TemporaryDirectory() as directorio, ExitStack() as pila:
            rutas = self.rutas_temporales(pila, Path(directorio))
            rutas[0].parent.mkdir()
            rutas[1].write_text("anterior", encoding="utf-8")
            pila.enter_context(redirect_stdout(io.StringIO()))
            with patch.object(carga_validacion, "escribir_csv", side_effect=fallar_primero):
                self.assertFalse(informes.generar_informes(auditoria, self.fecha))
            self.assertEqual(llamadas, 2)
            self.assertEqual(rutas[1].read_text(encoding="utf-8"), "anterior")
            self.assertTrue(rutas[0].is_file() and rutas[2].is_file())
            self.assertEqual(set(rutas[0].parent.iterdir()), set(rutas))


if __name__ == "__main__":
    unittest.main()
