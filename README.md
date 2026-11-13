# IT Asset Manager

## 1. Descripción del proyecto

IT Asset Manager es una aplicación de consola desarrollada en Python para gestionar y analizar un inventario de equipos informáticos mediante archivos CSV. Permite cargar y validar registros, gestionar equipos, guardar el inventario actualizado y consultar una auditoría con informes TXT/CSV y gráficos PNG.

## 2. Tecnologías y dependencias

- Python 3.12, definido en `environment.yml`.
- Git y GitHub para el control de versiones y la colaboración.
- Biblioteca estándar de Python: `csv`, `pathlib`, `datetime`, `re`, `math` y `decimal`.
- Dependencias declaradas: pandas 3.1 y matplotlib 3.11 en Conda; `pandas>=3.1,<3.2` y `matplotlib>=3.11,<3.12` en pip. Matplotlib genera los gráficos con el renderizador no interactivo Agg; pandas no se utiliza en el código actual.

Se puede utilizar cualquier editor o IDE, como PyCharm o Visual Studio Code.

## 3. Estructura real del proyecto

```text
ETL_Python/
├── .gitignore
├── README.md
├── environment.yml
├── requirements.txt
├── main.py
├── acciones.py
├── config.py
├── carga_validacion.py
├── gestion.py
├── informes.py
├── test_informes.py
├── test_main.py
├── datos/
│   ├── inventario.csv
│   └── inventario_prueba.csv
└── salida/
    └── .gitkeep
```

Los directorios locales `.venv/`, `__pycache__/` y los archivos del editor no forman parte del código entregable. No hay una carpeta `docs/` ni una memoria PDF en la estructura revisada.

| Módulo | Responsabilidad |
|---|---|
| `main.py` | Menú principal, submenú de gestión y estado del inventario en memoria. |
| `acciones.py` | Entrada de datos por consola y llamadas a los módulos de lógica. |
| `config.py` | Rutas, contrato CSV, valores permitidos y umbrales. |
| `carga_validacion.py` | Lectura, validación, resumen de carga y escritura genérica de CSV. |
| `gestion.py` | Altas, bajas lógicas, búsquedas, modificaciones, listados y guardado. |
| `informes.py` | Cálculos de análisis implementados y funciones de informes pendientes. |

## 4. Instalación

### Obtener el proyecto

Se necesita Git para clonar el repositorio:

```bash
git clone https://github.com/daaviiciin/ETL_Python.git
cd ETL_Python
```

Las funcionalidades disponibles dependen de la rama utilizada. Esta documentación describe los archivos de la copia de trabajo revisada, no garantiza que todas las ramas tengan el mismo desarrollo.

### Opción A: Conda

Con Conda instalado, ejecutar desde la carpeta del proyecto:

```bash
conda env create -f environment.yml
conda activate it-asset-manager
```

El archivo define el entorno `it-asset-manager`, el canal `defaults`, Python 3.12, pandas 3.1 y matplotlib 3.11. `environment.yml` se validó en Windows con `conda env create --dry-run -f environment.yml`, comprobando la resolución del entorno sin instalarlo.

Para salir del entorno:

```bash
conda deactivate
```

### Opción B: pip y entorno virtual

Con Python 3.12 instalado:

```bash
python -m venv .venv
```

Activar en PowerShell de Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

En CMD de Windows:

```bat
.venv\Scripts\activate.bat
```

En Linux o macOS:

```bash
source .venv/bin/activate
```

Instalar las dependencias declaradas:

```bash
python -m pip install -r requirements.txt
```

Cada persona debe crear su propio entorno; `.venv/` está excluido de Git. Esta alternativa instala dependencias en el entorno virtual y no requiere crear también el entorno Conda.

## 5. Ejecución y uso

Con el entorno elegido activado, ejecutar desde la carpeta principal:

```bash
python main.py
```

El menú ofrece:

1. **Cargar y validar inventario:** Enter selecciona `datos/inventario.csv`. También se puede indicar `datos/inventario_prueba.csv` u otra ruta. Las rutas relativas introducidas se interpretan desde la carpeta del proyecto. Una carga fallida conserva el inventario anterior.
2. **Gestión del inventario:** altas, bajas lógicas, búsquedas, modificaciones y listado completo; `0` vuelve al menú principal.
3. **Auditoría, informes y gráficos:** abre el submenú de análisis del inventario cargado.
4. **Guardar y salir:** escribe `salida/inventario_actualizado.csv` y sale solo si el guardado tiene éxito. Si falla, mantiene el inventario y el menú para reintentar.
0. **Salir sin guardar:** termina sin exportar los cambios del inventario. La carga puede haber generado ya `errores.csv`.

Las opciones de gestión, auditoría y guardado requieren cargar primero un inventario. Una carga con todos los registros rechazados deja una lista vacía que el programa considera cargada.

El submenú de la opción 3 ofrece:

| Opción | Operación |
|---|---|
| 1 | Mostrar la auditoría en consola, sin generar archivos. |
| 2 | Generar el informe TXT y los dos CSV de auditoría. |
| 3 | Generar los tres gráficos PNG. |
| 4 | Generar informes y gráficos. |
| 0 | Volver al menú principal. |

Cada operación calcula una única auditoría con el inventario actual en memoria y la fecha de referencia del programa. No vuelve a cargar el CSV. Las opciones inválidas se vuelven a solicitar; los errores de cálculo o generación muestran un aviso y permiten reintentar. En la generación conjunta se intenta generar gráficos aunque fallen los informes. Una interrupción por teclado o fin de entrada en este submenú vuelve al menú principal.

## 6. Configuración y contrato CSV

Las rutas se construyen a partir de la ubicación de `config.py`, sin depender de la carpeta desde la que se lance Python:

- `BASE_DIR`: carpeta principal del proyecto.
- `DATA_DIR`: carpeta `datos/`.
- `OUTPUT_DIR`: carpeta `salida/`.
- `INVENTORY_FILE` y `TEST_FILE`: archivos de entrada predeterminados.
- `UPDATED_FILE`: destino del inventario actualizado.
- Otras constantes definen las salidas de errores, informes y gráficos.

La cabecera debe contener estas 13 columnas, mostradas en su orden de exportación:

```text
id_equipo,hostname,tipo,marca_modelo,sistema_operativo,version_so,direccion_ip,departamento,usuario_asignado,fecha_compra,fin_garantia,estado,precio_eur
```

La lectura utiliza coma y UTF-8 con o sin BOM; las salidas usan UTF-8. Las fechas y los precios permanecen como texto dentro de los diccionarios del inventario.

Validaciones implementadas:

- Archivo existente, con cabecera, registros y todas las columnas obligatorias.
- ID, hostname, sistema operativo y departamento no vacíos.
- Tipo: `portatil`, `sobremesa`, `servidor` o `movil`.
- IP opcional; si se informa, debe tener cuatro grupos entre 0 y 255 y ser única entre los registros aceptados.
- ID único entre los registros aceptados. La validación de duplicados compara el texto exacto.
- Fechas existentes con formato `AAAA-MM-DD`; fin de garantía estrictamente posterior a la compra.
- Estado: `activo`, `almacen`, `reparacion` o `baja`.
- Precio finito mayor que cero, con punto decimal opcional; no admite coma decimal ni notación científica.

`marca_modelo`, `version_so` y `usuario_asignado` deben existir como columnas, pero pueden estar vacíos. Se informa únicamente del primer error de cada registro. Una fila rechazada no bloquea otra posterior con el mismo ID o IP. Las columnas adicionales no se exportan en las salidas del contrato.

`FECHA_REFERENCIA_FIJA = None` selecciona la fecha del sistema una vez al arrancar; si se configura una fecha fija, se utiliza esa. Los cálculos de análisis reciben la fecha como parámetro. Los umbrales actuales son 90 días para garantías, 365,25 días por año y dos decimales.

## 7. Funcionalidades implementadas y pendientes

### Implementadas y accesibles desde el menú

- Carga y validación CSV, separación de válidos y rechazados y resumen por regla.
- Alta de equipos reutilizando la validación de carga, sin añadir registros inválidos.
- Baja lógica: cambia el estado a `baja` sin eliminar el equipo.
- Búsquedas exactas sin distinguir mayúsculas por ID, hostname, departamento o tipo.
- Modificación exclusiva de estado, departamento y usuario asignado; valida el estado y rechaza departamentos vacíos.
- Listado en tabla y manejo de listas vacías.
- Guardado con las 13 columnas en orden, protección de `INVENTORY_FILE` y aviso de errores sin anunciar éxito falso.

### Cálculos implementados en `informes.py`

Las funciones auxiliares se integran en `calcular_auditoria()` y se presentan mediante `mostrar_auditoria()` desde el menú 3:

- Conteo de equipos por campo y conversión de versiones numéricas a tuplas.
- Selección de sistemas obsoletos según `SO_OBSOLETOS`: Windows 7 y 8.1, macOS anterior a 12 y Ubuntu/Ubuntu Server hasta 18.04 inclusive. Son reglas configuradas del proyecto.
- Las versiones no numéricas no se clasifican como obsoletas.
- Selección de garantías entre la fecha de referencia y 90 días después, incluidos ambos extremos.
- Antigüedad en años, media por departamento y coste por departamento, con redondeo de los resultados agregados. El coste utiliza `Decimal` para sumar los precios.

### Informes y gráficos implementados

El informe TXT incluye la fecha de referencia, distribuciones por departamento y estado, antigüedad media, costes y los equipos con SO obsoleto o garantía próxima. Los dos CSV exportan estos últimos grupos con las 13 columnas del contrato, en orden y sin metadatos internos.

Los PNG muestran equipos por departamento, equipos por estado y antigüedad media por departamento. Incluyen títulos, ejes, valores y etiquetas largas divididas en líneas. Si el inventario está vacío, los informes indican la ausencia de datos, los CSV conservan la cabecera y los gráficos muestran un mensaje.

Los informes TXT/CSV y gráficos PNG se escriben primero en archivos temporales y sustituyen cada destino solo al completar su escritura. Un fallo conserva el archivo anterior de ese destino y los datos en memoria. La operación conjunta puede producir resultados parciales: las salidas que se completan correctamente se conservan aunque falle otra.

### Estado pendiente

Las funciones previstas de auditoría, informes y gráficos ya están implementadas; no quedan bloques `NotImplementedError` en `informes.py`. Las reglas de obsolescencia siguen siendo las reglas configuradas del proyecto y requieren mantenimiento cuando cambien los criterios adoptados.

## 8. Archivos de salida

| Archivo en `salida/` | Estado |
|---|---|
| `errores.csv` | Se regenera tras una lectura correcta, incluso sin rechazados. Incluye las 13 columnas más `linea_csv`, `codigo_error` y `motivo`. |
| `inventario_actualizado.csv` | Se genera al guardar el inventario. |
| `informe_auditoria.txt` | Auditoría por secciones y fecha de referencia; submenú 2 o 4. |
| `equipos_so_obsoleto.csv` | Equipos con SO obsoleto; submenú 2 o 4. |
| `garantias_proximas.csv` | Equipos con garantía próxima; submenú 2 o 4. |
| `grafico_departamentos.png` | Equipos por departamento; submenú 3 o 4. |
| `grafico_estados.png` | Equipos por estado; submenú 3 o 4. |
| `grafico_antiguedad.png` | Antigüedad media por departamento; submenú 3 o 4. |

Las salidas CSV implementadas crean el directorio de destino si falta y sobrescriben el archivo de salida anterior. Una lectura fallida no actualiza `errores.csv`. El contenido generado de `salida/` está excluido de Git; `.gitkeep` conserva la carpeta en el repositorio.

## 9. Pruebas automatizadas

Con el entorno Conda o `.venv` activado y las dependencias instaladas, ejecutar desde la carpeta principal:

```bash
python -m unittest discover -v
```

En PowerShell también se puede utilizar directamente el Python del entorno local:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -v
```

- `test_informes.py`: indicadores, fechas, límites, redondeos, exportación y lectura de TXT/CSV, PNG, datos vacíos y errores de escritura. Utiliza directorios temporales y backend Agg, sin abrir ventanas ni modificar los archivos de datos.
- `test_main.py`: navegación del menú 3, sus cuatro operaciones, volver, opciones inválidas, inventario no cargado o vacío, errores y reintentos. Utiliza mocks para entradas, carga, cálculo y exportaciones; no lee ni escribe datos reales.

Comprobación de espacios y formato del diff:

```bash
git diff --check
```
