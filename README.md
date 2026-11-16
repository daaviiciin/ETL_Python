# IT Asset Manager

Programa de consola en Python que carga el inventario informático de la empresa desde un fichero CSV, comprueba la calidad de cada registro y separa los válidos de los rechazados. Permite gestionar el inventario desde un menú (altas, bajas, búsquedas, modificaciones y listados). También genera un informe de auditoría, listados en CSV y gráficos PNG para la dirección de IT.

**Integrantes del grupo**

- David Rojas
- Estefanía Correa
- David Moreno

---

## 1. Requisitos

| Requisito | Versión |
|---|---|
| Python | **3.11 o superior** (probado con 3.13). Lo exige pandas 3 |
| matplotlib | 3.11.2 (en `requirements.txt`) |
| pandas | 3.1.1 (en `requirements.txt`) |
| numpy | 2.5.4 (la instalan pandas y matplotlib; fijada en `requirements.txt`) |

`requirements.txt` fija la versión exacta de **todas** las dependencias, también las que pandas y matplotlib instalan por su cuenta, para que cualquier instalación reproduzca exactamente el entorno con el que se ha probado el programa.

El resto de módulos (`csv`, `datetime`, `pathlib`, `re`…) son de la biblioteca estándar y no hay que instalarlos.

---

## 2. Instalación y arranque

### Opción A: script automático (recomendada)

El script comprueba la versión de Python, crea el entorno virtual `.venv`, instala `requirements.txt` y arranca el programa.

| Sistema | Qué hacer |
|---|---|
| **Windows** | Doble clic en `instalar.bat`, o desde una terminal en la carpeta del proyecto: `instalar.bat` |
| **Linux / macOS** | Desde una terminal en la carpeta del proyecto: `bash instalar.sh` |

Se puede ejecutar tantas veces como se quiera. Si el entorno ya existe, no se vuelve a crear: solo se comprueban las dependencias y arranca el programa.

### Opción B: paso a paso

```bash
# 1. Entrar en la carpeta del proyecto (la que sale al descomprimir el zip)
cd ETL_Python

# 2. Crear el entorno virtual
python -m venv .venv

# 3. Activarlo
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux / macOS

# 4. Instalar las dependencias
pip install -r requirements.txt

# 5. Ejecutar
python main.py
```

### Opción C: entorno Conda

Conda **no es necesario**: las opciones A y B solo necesitan Python. Para quien ya use Anaconda, Miniconda o Miniforge, `environment.yml` define el entorno `it-asset-manager` con Python 3.13 y las mismas versiones de pandas, matplotlib y numpy que `requirements.txt` (canal `conda-forge`):

```bash
conda env create -f environment.yml
conda activate it-asset-manager
python main.py
```

El programa se ejecuta con `python main.py` desde la carpeta del proyecto. Las rutas de `datos/` y `salida/` se calculan a partir de dónde está `config.py`, así que funciona en cualquier ordenador, e incluso lanzado desde otra carpeta, sin cambiar nada.

---

## 3. Uso del programa

Al arrancar se muestra la fecha de referencia que se usará en los cálculos y si hay un inventario cargado.

```
=== IT ASSET MANAGER ===
Fecha de referencia: 2026-11-09
Inventario: sin cargar
1. Cargar y validar inventario
2. Gestión del inventario
3. Auditoría, informes y gráficos
4. Guardar y salir
0. Salir sin guardar
```

### Menú principal

| Opción | Qué hace |
|---|---|
| **1. Cargar y validar inventario** | Pide la ruta del CSV. Si se pulsa **Enter**, carga `datos/inventario.csv`. Se puede escribir cualquier otra ruta, relativa al proyecto (`datos/inventario_prueba.csv`) o absoluta, y también pegarla con comillas. Valida cada fila, guarda los rechazados en `salida/errores.csv` y muestra el resumen: filas leídas, válidas, rechazadas y errores por cada una de las 13 reglas. Si el fichero no existe, está vacío o le falta una columna, muestra un mensaje y el programa sigue funcionando. |
| **2. Gestión del inventario** | Abre el submenú de gestión (tabla siguiente). Necesita un inventario cargado. |
| **3. Auditoría, informes y gráficos** | Calcula los indicadores sobre el inventario actual, los muestra por consola y genera los informes y los tres gráficos en `salida/`. |
| **4. Guardar y salir** | Guarda el inventario, con todos los cambios, en `salida/inventario_actualizado.csv` y cierra el programa. El CSV original **nunca** se modifica. |
| **0. Salir sin guardar** | Cierra el programa sin guardar los cambios de la sesión. |

### Submenú de gestión

| Opción | Qué hace |
|---|---|
| **1. Alta de equipo** | Pide los 13 campos uno a uno. Cada dato se valida en cuanto se escribe, con las mismas reglas que la carga del CSV. Si no es válido (por ejemplo, una IP ya usada), se explica el motivo y se vuelve a pedir. Escribiendo `cancelar` se abandona el alta. |
| **2. Baja de equipo** | Baja **lógica**: pide el `id_equipo` y cambia su estado a `baja`, sin borrar el registro. |
| **3. Buscar equipos** | Se elige el campo (`id_equipo`, `hostname`, `departamento` o `tipo`) y el valor. No distingue mayúsculas. En `hostname` y `departamento` basta con una parte del texto. |
| **4. Modificar equipo** | Cambia el `estado` (elegido de una lista), el `departamento` o el `usuario_asignado` de un equipo. El nuevo valor se valida antes de aplicarlo. |
| **5. Listar inventario** | Muestra todo el inventario, o solo los equipos de un tipo, departamento o estado. |
| **0. Volver** | Vuelve al menú principal. |

### Ficheros que genera el programa

Todos se guardan en `salida/`. La carpeta se crea si no existe y los ficheros se sobrescriben en cada ejecución.

| Fichero | Contenido | Se genera con |
|---|---|---|
| `errores.csv` | Filas rechazadas con sus 13 columnas originales más `linea_csv`, `codigo_error` y `motivo` | Opción 1 |
| `inventario_actualizado.csv` | Inventario válido con las altas, bajas y modificaciones de la sesión | Opción 4 |
| `informe_auditoria.txt` | Informe por secciones: reparto por tipo, departamento y estado; SO obsoletos; garantías próximas; antigüedad media y coste por departamento | Opción 3 |
| `equipos_so_obsoleto.csv` | Equipos con sistema operativo obsoleto | Opción 3 |
| `garantias_proximas.csv` | Equipos cuya garantía caduca en los próximos 90 días | Opción 3 |
| `grafico_departamentos.png` | Barras: número de equipos por departamento | Opción 3 |
| `grafico_estados.png` | Barras: número de equipos por estado | Opción 3 |
| `grafico_antiguedad.png` | Barras: antigüedad media (años) por departamento | Opción 3 |

### Cómo comprobar los resultados con una fecha fija

Por defecto, los cálculos usan la fecha de hoy (`date.today()`). Para repetirlos con una fecha concreta, edita `config.py`:

```python
FECHA_REFERENCIA_FIJA = date(2026, 11, 2)   # en vez de None
```

Después ejecuta el programa y carga `datos/inventario_prueba.csv` (opción 1) y lanza la auditoría (opción 3). Para volver al funcionamiento normal, déjala otra vez en `None`.

---

## 4. Estructura del proyecto

```text
ETL_Python/
├── main.py                     Programa principal: solo los menús
├── acciones.py                 Una función por opción del menú: pide los datos y llama a la lógica
├── carga_validacion.py         Lectura del CSV, reglas de validación, errores.csv y resumen de carga
├── gestion.py                  Altas, bajas, búsquedas, modificaciones, listados y guardado
├── informes.py                 Auditoría (con pandas), informes TXT/CSV y gráficos (matplotlib)
├── config.py                   Todas las constantes: rutas, contrato de datos, umbrales, SO obsoletos
├── requirements.txt            Dependencias de terceros con su versión (pip)
├── environment.yml             Las mismas dependencias para Conda
├── instalar.bat                Instalación y arranque en Windows
├── instalar.sh                 Instalación y arranque en Linux / macOS
├── README.md
├── datos/
│   ├── inventario.csv
│   └── inventario_prueba.csv
├── salida/                     Se genera al ejecutar (se entrega vacía)
└── docs/
    └── memoria.pdf             Memoria técnica
```

### Responsabilidad de cada módulo

Las dependencias van en un solo sentido, sin imports circulares:

```
main.py → acciones.py → gestion.py / informes.py → carga_validacion.py → config.py
```

| Módulo | Responsabilidad | Qué no hace |
|---|---|---|
| `main.py` | Muestra los menús y lee la opción elegida | No pide datos ni calcula nada |
| `acciones.py` | Pide por teclado los datos de cada opción y llama al módulo que corresponda | No valida ni calcula |
| `carga_validacion.py` | Lee el CSV con el módulo `csv`, aplica las reglas (`validar_campo` / `validar_fila`) y escribe CSV | No usa `input()` |
| `gestion.py` | Opera sobre el inventario (lista de diccionarios). Reutiliza las reglas de `carga_validacion` | No usa `input()` |
| `informes.py` | Calcula los indicadores, escribe los informes y dibuja los gráficos | No lee el CSV ni usa `input()` |
| `config.py` | Guarda todas las constantes. No ejecuta nada al importarse | — |

**Decisiones de diseño**

- **Sin variables globales:** el inventario y la fecha de referencia son variables locales de `main()` que se pasan como parámetro.
- **Una sola fuente de reglas:** la carga, el alta y la modificación usan la misma función `validar_campo`.
- **Datos en estructuras básicas:** listas de diccionarios y conjuntos (`set`) para detectar duplicados. pandas solo se usa en la auditoría, para los repartos (`value_counts`) y para las medias y sumas por departamento (`groupby`).
- **Ningún valor escrito a mano:** umbrales, rutas, formatos y la lista de SO obsoletos están en `config.py`.

---

## 5. Reglas de validación

Cada fila se comprueba en el orden de las columnas del contrato. Si incumple varias reglas, se informa solo de la **primera**. Las filas rechazadas no se corrigen ni se eliminan en silencio: se guardan en `errores.csv` con su motivo.

| Columna | Regla | Código de error |
|---|---|---|
| `id_equipo` | No vacío y no repetido | `ID_VACIO`, `ID_DUPLICADO` |
| `hostname` | No vacío | `HOSTNAME_VACIO` |
| `tipo` | `portatil`, `sobremesa`, `servidor` o `movil` | `TIPO_INVALIDO` |
| `sistema_operativo` | No vacío | `SO_VACIO` |
| `direccion_ip` | Opcional; si existe, 4 números de 0 a 255 y no repetida | `IP_INVALIDA`, `IP_DUPLICADA` |
| `departamento` | No vacío | `DEPARTAMENTO_VACIO` |
| `fecha_compra` | `AAAA-MM-DD` con ceros y fecha real | `FECHA_COMPRA_INVALIDA` |
| `fin_garantia` | `AAAA-MM-DD` y posterior a `fecha_compra` | `FIN_GARANTIA_INVALIDA`, `GARANTIA_ANTERIOR_COMPRA` |
| `estado` | `activo`, `almacen`, `reparacion` o `baja` | `ESTADO_INVALIDO` |
| `precio_eur` | Número con punto decimal mayor que 0 | `PRECIO_INVALIDO` |

`marca_modelo`, `version_so` y `usuario_asignado` son opcionales y admiten cualquier texto.

---

## 6. Supuestos adoptados

1. **Duplicados:** un `id_equipo` o una IP solo cuentan como repetidos si ya los usa un equipo **válido** anterior. Una fila rechazada no bloquea a las siguientes. Se conserva siempre la primera aparición.
2. **Garantía del mismo día:** si `fin_garantia` coincide con `fecha_compra`, la fila se rechaza, porque no es *posterior*.
3. **Precios enteros:** se aceptan (`1500`). "Con punto decimal" se interpreta como que el separador decimal es el punto. Se rechazan `1500,50`, `0`, negativos, texto, `nan`, `inf` y notación científica (`1e5`).
4. **Espacios:** un campo que solo tiene espacios cuenta como vacío. Un valor con espacios alrededor (`" activo"`) **no** se corrige: se rechaza, porque no es exactamente un valor permitido.
5. **Fechas:** se exigen los ceros (`2022-3-5` se rechaza) y que la fecha exista (`2023-02-30` se rechaza).
6. **Fichero solo con cabecera:** se trata como vacío y no se carga.
7. **Columnas extra:** si el CSV trae columnas que no están en el contrato, se avisa por consola y se ignoran. Si falta alguna columna del contrato, el fichero no se carga.
8. **Codificación:** UTF-8, con o sin BOM (el de los ficheros guardados con Excel).
9. **Número de línea** en `errores.csv`: es la línea real del fichero, con la cabecera como línea 1. Las líneas en blanco no desplazan la numeración.
10. **SO obsoleto:** Windows 7, Windows 8.1, macOS anterior a 12 y Ubuntu 18.04 o anterior. **Ubuntu Server 18.04 o anterior también se considera obsoleto**, porque es la misma versión de Ubuntu. Windows 10, Windows Server, iOS y Android se consideran vigentes. Las versiones se comparan por partes numéricas (`10.15` es posterior a `10.2`), y si la versión no es numérica el equipo no se marca como obsoleto.
11. **Auditoría:** se calcula sobre el inventario actual, con las altas, bajas y modificaciones de la sesión, e incluye los equipos de cualquier estado, también los de baja. La antigüedad es (días hasta la fecha de referencia) / 365,25, con la media por departamento redondeada a 2 decimales. Una garantía es próxima si vence entre la fecha de referencia y 90 días después, ambas incluidas.

---

## 7. Limitaciones conocidas

- Los cambios de la sesión solo se guardan con la opción **4**. Salir con **0** los descarta.
- Solo se pueden modificar `estado`, `departamento` y `usuario_asignado`. Un equipo no se puede borrar físicamente, solo darse de baja.
- Si un fichero de `salida/` está abierto en otro programa (por ejemplo, Excel), no se puede sobrescribir. El programa avisa y sigue funcionando. En el caso de "Guardar y salir", no se cierra hasta que se pueda guardar.
- La fecha de referencia fija se cambia editando `config.py`, no desde el menú.
- Los informes muestran los números con punto decimal (`1102.91`).
