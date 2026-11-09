
# IT Asset Manager

## 1. Descripción del proyecto

IT Asset Manager es una aplicación desarrollada en Python para la gestión y el análisis de un inventario de equipos informáticos.

El proyecto permite trabajar con información de los equipos mediante archivos CSV y está diseñado para facilitar su gestión, validación y análisis.

## 2. Tecnologías utilizadas

- Python 3.
- Git para el control de versiones.
- GitHub para el almacenamiento del proyecto y el trabajo colaborativo.
- pathlib para la gestión de rutas y directorios.
- matplotlib para la generación de gráficos.

El proyecto no depende de un entorno de desarrollo específico. Cada integrante puede utilizar el editor o IDE que prefiera, como PyCharm o Visual Studio Code.

## 3. Estructura del proyecto

La estructura prevista del proyecto es la siguiente:

```text
IT_ASSET_MANAGER/
│
├── main.py
├── config.py
├── carga_validacion.py
├── gestion.py
├── informes.py
├── requirements.txt
├── README.md
│
├── datos/
│   ├── inventario.csv
│   └── inventario_prueba.csv
│
├── salida/
│
└── docs/
    └── memoria.pdf
```

## 4. Configuración del proyecto

El proyecto utiliza rutas relativas para localizar sus carpetas y archivos.

En el módulo `config.py` se centralizan las rutas y configuraciones generales.

Actualmente se han definido las siguientes constantes:

- `BASE_DIR`: carpeta principal del proyecto.
- `DATA_DIR`: carpeta donde se almacenan los archivos CSV.
- `OUTPUT_DIR`: carpeta donde se guardarán los resultados generados.
- `INVENTORY_FILE`: ruta del inventario principal.
- `TEST_FILE`: ruta del inventario de pruebas.
- `UPDATED_FILE`: ruta donde se guardará el inventario actualizado.

Esta configuración permite ejecutar el proyecto desde diferentes ubicaciones y ordenadores sin modificar manualmente las rutas.

## 5. Entorno virtual y dependencias

El proyecto utiliza un entorno virtual de Python (`.venv`) para mantener aisladas las dependencias.

Cada integrante del grupo y cualquier persona que descargue el proyecto deberá crear su propio entorno virtual.

La carpeta `.venv` no se incluirá en el repositorio de GitHub, ya que cada usuario tendrá su propia configuración local.

Las dependencias necesarias se especificarán en el archivo `requirements.txt`.

## 6. Instalación y configuración

### Requisitos previos

- Tener instalado Python 3.
- Tener Git instalado si se desea clonar el repositorio.

### Clonar el repositorio

```bash
git clone URL_DEL_REPOSITORIO
```

Entrar en la carpeta del proyecto:

```bash
cd IT_ASSET_MANAGER
```

### Crear el entorno virtual

En Windows:

```bash
python -m venv .venv
```

### Activar el entorno virtual

En Windows:

```bash
.venv\Scripts\activate
```

### Instalar las dependencias

```bash
pip install -r requirements.txt
```

## 7. Ejecución del programa

Una vez configurado el entorno virtual e instaladas las dependencias, el programa se ejecutará desde la carpeta principal mediante:

```bash
python main.py
```

Las instrucciones definitivas de funcionamiento se completarán cuando esté desarrollado el menú principal.

## 8. Estado actual del desarrollo

Actualmente se ha iniciado la configuración del proyecto y se ha creado el módulo `config.py`, donde se están centralizando las rutas y configuraciones generales.

También se ha iniciado la documentación mediante este archivo README.

El resto de módulos y funcionalidades se desarrollarán progresivamente.
