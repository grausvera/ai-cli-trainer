import time
import shutil
from pathlib import Path

from core.constants import (
    MODELS_BASE_DIR,
    MODELS_TRAINED_DIR,
    SECTION_THREE_TITLE,
    YOLO_MODEL_URL,
    YOLO_MODEL_VERSIONS,
)
from core import Dataset, Downloader, Validator
from ui import BashUI


class SectionThree:
    def __init__(
        self,
        ui: BashUI,
        validator: Validator,
        dataset: Dataset,
        downloader: Downloader,
    ) -> None:
        self._ui: BashUI = ui
        self._validator: Validator = validator
        self._dataset: Dataset = dataset
        self._downloader: Downloader = downloader

        self._base_models_path: Path | None = None
        self._trained_models_path: Path | None = None

    def run(self, context: dict[str, object]) -> None:
        model_name = f"model_{time.strftime('%Y%m%d%H%M%S')}"
        self._ui.section(
            SECTION_THREE_TITLE,
            subtitle=f"Modelo Resultante: {model_name}",
        )

        try:
            self._base_models_path = MODELS_BASE_DIR
            self._base_models_path.mkdir(exist_ok=True)

            source = self._ui.ask(
                "Fuente del Modelo Base",
                choices=["yolo", "local", "drive"],
                default="yolo",
            )

            if source == "yolo":
                base_model_path = self._selectYOLOModel()
            elif source == "local":
                base_model_path = self._selectLocalModel()
            elif source == "drive":
                base_model_path = self._selectDriveModel()

            context["base_model_path"] = base_model_path

            self._ui.console.print()
            epochs = self._ui.askInt("Épocas", default=100)
            batch = self._ui.askInt("Tamaño de Batch", default=16)
            imgsz = self._ui.askInt("Tamaño de Imagen", default=640)
            device = self._askForDevice()

            context["epochs"] = epochs
            context["batch"] = batch
            context["imgsz"] = imgsz
            context["device"] = device

            self._ui.console.print()
            self._ui.stepSuccess("Configuración guardada.")

            self._ui.console.print()
            confirm = self._ui.askConfirm("Iniciar Entrenamiento", default=True)
            if confirm:
                self._trained_models_path = MODELS_TRAINED_DIR
                self._trained_models_path.mkdir(exist_ok=True)

                self._runTraining(context, model_name)
            else:
                raise Exception("Entrenamiento cancelado por el usuario.")

        except Exception:
            raise

    def _selectYOLOModel(self) -> Path:
        try:
            version = self._ui.ask(
                "Versión",
                choices=["n", "s", "m", "l", "x"],
                default="n",
            )

            yolo_model = YOLO_MODEL_VERSIONS[version]
            path = self._base_models_path / yolo_model
            url = YOLO_MODEL_URL + yolo_model

            self._ui.console.print()
            if path.exists():
                self._ui.stepSuccess(
                    f"El modelo '{path.name}' ya se encuentra en la carpeta '{self._base_models_path.parent.name}/{self._base_models_path.name}'."
                )

                return Path(path)
            else:
                self._ui.stepInfo("Conectando con Ultralytics.")
                if not self._downloader.runYOLO(url, path):
                    raise Exception(
                        f"No se pudo descargar el modelo base '{yolo_model}'."
                    )

                self._ui.stepSuccess(
                    "Modelo base listo en: "
                    + f"{self._base_models_path.parent.name}/{self._base_models_path.name}/{yolo_model}"
                )

                return Path(path)

        except Exception:
            raise

    def _selectLocalModel(self) -> Path:
        try:
            path = self._ui.askPath("Ruta del modelo '.pt' local")

            if path.exists() and path.suffix == ".pt":
                shutil.copy2(path, self._base_models_path)
                self._ui.stepSuccess(
                    "Modelo base listo en: "
                    + f"{self._base_models_path.parent.name}/{self._base_models_path.name}/{path.name}"
                )

                return Path(self._base_models_path / path.name)
            else:
                self._ui.stepWarning(
                    "Advertencia: El archivo no existe o no es un modelo '.pt'."
                )
                return self.selectLocalModel()
        except Exception:
            raise

    def _selectDriveModel(self) -> Path:
        url = self._ui.ask("Enlace de Google Drive del modelo '.pt'")

        if not self._validator.validateGDURL(url):
            self._ui.stepWarning(
                "Advertencia: La URL no pertenece a Google Drive.\n"
                + "  Formato esperado: 'https://drive.google.com/...'"
            )
            return self.selectDriveModel()

        try:
            path = self._downloader.runGD(url, self._base_models_path)

            if path and path.exists() and path.suffix == ".pt":
                self._ui.stepSuccess(
                    "Modelo descargado de Google Drive: "
                    + f"{self._base_models_path.parent.name}/{self._base_models_path.name}/{path.name}"
                )

                return Path(path)

            else:
                if path and path.exists():
                    if path.is_dir():
                        shutil.rmtree(str(path))
                    else:
                        path.unlink()
                else:
                    raise Exception("No se pudo descargar el modelo '.pt'.")

        except Exception:
            raise

    def _askForDevice(self) -> str:
        device = self._ui.ask(
            "Dispositivo ",
            choices=[
                "cpu",
                "cuda",
                "mps",
                "auto",
            ],
            default="auto",
        )

        if device == "auto":
            return None
        elif device == "mps":
            import torch

            if not torch.backends.mps.is_available():
                self._ui.stepWarning(
                    "Advertencia: No se detectaron GPUs Apple (MPS) disponibles.\n"
                    "  Por favor, ingrese un dispositivo válido para su sistema."
                )
                return self._askForDevice()

            return device
        elif device == "cuda":
            import torch

            if not torch.cuda.is_available():
                self._ui.stepWarning(
                    "Advertencia: No se detectaron GPUs NVIDIA (CUDA) disponibles.\n"
                    "  Se seleccionará 'auto' para el dispositivo de entrenamiento."
                )
                return None

            num_devices = torch.cuda.device_count()
            if num_devices == 1:
                return torch.cuda.get_device_name(0)
            else:
                gpu_names = [torch.cuda.get_device_name(i) for i in range(num_devices)]

                return self._askForGPUs(num_devices, gpu_names)
        else:
            return device

    def _askForGPUs(self, num_devices: int, gpu_names: list[str]) -> list[int]:
        # TODO: Testear el ingreso de IDs de GPU
        gpu_ids = self._ui.ask(f"IDs de la GPU ({', '.join(gpu_names)})")
        chunks = [int(i.strip()) for i in gpu_ids.split(",") if i.strip().isdigit()]

        if len(chunks) == 0:
            self._ui.stepWarning(
                "Advertencia: No se ingresaron IDs de GPU válidos.\n"
                "  Por favor ingrese IDs de GPU válidos separados por coma."
            )
            return self._askForGPUs(num_devices, gpu_names)

        for chunk in chunks:
            if chunk not in range(num_devices):
                self._ui.stepWarning(
                    f"Advertencia: El ID de la GPU '{chunk}' no es válido.\n"
                    "  Por favor ingrese IDs de GPU válidos separados por coma."
                )
                chunks = []
                return self._askForGPUs(num_devices, gpu_names)

        return chunks

    def _runTraining(self, context: dict[str, object], model_name: str) -> None:
        try:
            from core.trainer import Trainer

            self._ui.section("🚀 INICIANDO ENGINE DE ENTRENAMIENTO... ")

            trainer = Trainer(str(context.get("base_model_path", "N/A")))
            success, best_model_path = trainer.run(
                data_yaml=context.get("yaml_path", "N/A"),
                epochs=context.get("epochs", 0),
                imgsz=context.get("imgsz", 0),
                batch=context.get("batch", 0),
                project_dir=self._trained_models_path,
                run_name=model_name,
                device=context.get("device", None),
            )

            if success and best_model_path:
                context["best_model_path"] = best_model_path
                context["trained_model_path"] = self._trained_models_path / model_name
                self._ui.stepSuccess("Entrenamiento completado correctamente.")
            else:
                raise Exception("No se pudo entrenar el modelo.")

        except Exception:
            raise
