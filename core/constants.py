from pathlib import Path

# Configuración Visual
CONSOLE_WIDTH = 80
APP_NAME = "AI CLI TRAINER"
APP_SUBTITLE = "Pipeline Automatizado de Entrenamiento"
SECTION_ONE_TITLE = "1. ORIGEN DEL DATASET"
SECTION_TWO_TITLE = " 2. PROCESAMIENTO DE DATOS"
SECTION_THREE_TITLE = "3. HIPERPARÁMETROS DE ENTRENAMIENTO "

# Rutas Base
BASE_DIR = Path.cwd()
DATASETS_DIR = BASE_DIR / "datasets"
MODELS_DIR = BASE_DIR / "models"
MODELS_BASE_DIR = MODELS_DIR / "base"
MODELS_TRAINED_DIR = MODELS_DIR / "trained"

# Asegurar que existan las carpetas base al importar
DATASETS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_BASE_DIR.mkdir(parents=True, exist_ok=True)
MODELS_TRAINED_DIR.mkdir(parents=True, exist_ok=True)

# Extensiones de archivos
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
LABEL_EXTENSIONS = {".txt"}
UNZIP_EXTENSIONS = {".zip"}

YOLO_MODEL_VERSIONS = {
    "n": "yolo11n.pt",
    "s": "yolo11s.pt",
    "m": "yolo11m.pt",
    "l": "yolo11l.pt",
    "x": "yolo11x.pt",
}
YOLO_MODEL_URL = "https://github.com/ultralytics/assets/releases/download/v8.3.0/"
