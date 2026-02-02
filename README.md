# 🤖 AI Model Trainer CLI

**Pipeline automatizado de entrenamiento para modelos YOLO**

AI CLI Trainer es una herramienta de línea de comandos (CLI) diseñada para simplificar y automatizar el proceso de entrenamiento de modelos de visión por computadora utilizando la arquitectura YOLO (Ultralytics). Guía al usuario paso a paso desde la ingesta de datos hasta el entrenamiento final, gestionando validaciones, descargas y configuraciones de forma automática.

## 🚀 Características Principales

- **📦 Ingesta de Datos Flexible:**
  - Soporte para datasets locales (carpetas, archivos `.zip`, `.rar`, `.tar`).
  - Descarga directa de datasets y modelos desde **Google Drive**.
- **🧠 Procesamiento Inteligente:**
  - ✅ Validación automática de integridad (pares imagen-etiqueta).
  - 🧹 Detección y manejo de imágenes huérfanas.
  - 📂 Normalización de estructura de directorios.
  - ✂️ División automática (Split) de datos en entrenamiento (Train) y validación (Val).
  - ⚙️ Generación automática de archivos de configuración `data.yaml`.
- **🎛️ Entrenamiento Personalizable:**
  - Selección de modelos base YOLO (n, s, m, l, x) con descarga automática.
  - Carga de modelos pre-entrenados locales o desde la nube.
  - Configuración interactiva de hiperparámetros (épocas, batch size, tamaño de imagen).
- **⚡ Soporte de Hardware:** Detección y selección automática de GPU (NVIDIA CUDA), Apple Silicon (MPS) o CPU.
- **🎨 Interfaz Visual:** UI moderna en terminal con barras de progreso, tablas y paneles informativos.

## 📋 Requisitos

- 🐍 Python 3.10 o superior.
- 🌐 Conexión a internet (para descargar modelos/datasets).

## 🛠️ Instalación

1.  **Clonar el repositorio:**

    ```bash
    git clone https://github.com/grausvera/ai-cli-trainer.git
    cd ai-cli-trainer
    ```

2.  **Crear un entorno virtual:**

    ```bash
    python -m venv .venv
    ```

3.  **Activar el entorno virtual:**

    Elige el comando correspondiente a tu sistema operativo y terminal:

    **Windows (CMD)**

    ```cmd
    .venv\Scripts\activate
    ```

    **Windows (PowerShell)**
    _Si es la primera vez, habilita la ejecución de scripts:_

    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```

    _Luego activa el entorno:_

    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```

    **Windows (Git Bash)**

    ```bash
    source .venv/Scripts/activate
    ```

    **Linux / macOS**

    ```bash
    source .venv/bin/activate
    ```

    > 💡 **Nota:** Para desactivar el entorno en cualquier momento, simplemente escribe `deactivate`.

4.  **📦 Instalar dependencias:**

    Selecciona el archivo adecuado según tu hardware:

    **Estándar (CPU / Apple Silicon)**

    ```bash
    pip install -r requirements/base.txt
    ```

    **NVIDIA GPU (CUDA 11.8)**

    ```bash
    pip install -r requirements/gpu-cu118.txt
    ```

    **NVIDIA GPU (CUDA 12.1)**

    ```bash
    pip install -r requirements/gpu-cu121.txt
    ```

    _Dependencias principales: `ultralytics`, `rich`, `gdown`, `requests`._

## ▶️ Uso

Para iniciar el asistente de entrenamiento, ejecuta el archivo principal:

```bash
python main.py
```

Sigue las instrucciones en pantalla para navegar por las 3 secciones del pipeline.

### 📖 Guía de Entradas Comunes

Durante la ejecución, el programa te solicitará información específica. Aquí tienes cómo ingresarla correctamente:

#### 1. Definición de Clases (Etiquetas)

Cuando el sistema te pida los nombres de las clases, ingrésalos separados por comas.

- **Formato:** `clase1, clase2, clase3`
- **Ejemplo:** `persona, coche, semaforo`

> 💡 **Tip:** El sistema normalizará automáticamente los nombres (convertirá espacios a guiones bajos y eliminará caracteres especiales).
>
> **Renombrado Avanzado:** Si deseas cambiar el nombre de una clase existente, usa el formato `viejo=nuevo`.
>
> - Ejemplo: `person=persona, car=auto`

#### 2. Selección de GPUs (NVIDIA CUDA)

Si seleccionas `cuda` como dispositivo y tienes múltiples tarjetas gráficas, deberás especificar cuáles usar mediante sus IDs (índices).

- **Una sola GPU:** Ingresa el número `0`.
- **Múltiples GPUs:** Ingresa los índices separados por comas.
  - Ejemplo: `0, 1` (Usará la primera y segunda GPU).

## 📂 Estructura del Proyecto

```text
ai-cli-trainer/
├── core/            # Lógica principal del negocio
│   ├── dataset.py      # Manejo y procesamiento de datos
│   ├── downloader.py   # Gestor de descargas (Drive/YOLO)
│   ├── trainer.py      # Wrapper de entrenamiento YOLO
│   └── validator.py    # Validaciones de archivos y fuentes
├── ui/              # Interfaz de usuario (CLI)
│   ├── bash.py         # Componentes visuales (Rich)
│   └── seccions/       # Pasos del asistente
├── datasets/        # Almacenamiento temporal de datasets procesados
├── models/          # Gestión de modelos
│   ├── base/           # Modelos base descargados (yolo11n.pt, etc.)
│   └── trained/        # Resultados de entrenamientos
├── main.py          # Punto de entrada de la aplicación
└── requirements/    # Dependencias modulares (base, gpu, etc.)
```

## 🖥️ Soporte de Hardware

La herramienta detecta automáticamente el hardware disponible:

- **NVIDIA GPU:** Soporte completo vía CUDA.
- **Apple Silicon:** Soporte para chips M1/M2/M3 vía MPS (Metal Performance Shaders).
- **CPU:** Modo de respaldo si no se detectan aceleradores.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
