import time
import shutil
from pathlib import Path

from core.constants import (
    DATASETS_DIR,
    IMAGE_EXTENSIONS,
    SECTION_ONE_TITLE,
    UNZIP_EXTENSIONS,
)
from core import Dataset, Downloader, Validator
from ui import BashUI


class SectionOne:
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

        self._dataset_path: Path | None = None

    def run(self, context: dict[str, object]) -> None:
        self._ui.section(
            SECTION_ONE_TITLE,
            subtitle="Seleccione dónde se encuentran sus datos crudos:",
        )

        source = self._ui.ask("Fuente", choices=["local", "drive"], default="local")
        clean_source = source.lower().strip()

        if clean_source == "local":
            source, dataset_path = self._selectLocalSource()
        elif clean_source == "drive":
            source, dataset_path = self._selectDriveSource()

        context["dataset_source"] = source
        context["dataset_path"] = Path(dataset_path).expanduser().resolve()

    def _selectLocalSource(self) -> tuple[str, Path]:
        path = self._ui.askPath("Ruta de origen (carpeta o archivo comprimido)")
        is_valid, type_detected = self._validator.source(path)

        if not is_valid:
            if type_detected == "path_not_found":
                self._ui.stepWarning(
                    f"Advertencia: La ruta '{path}' no existe.\n"
                    + "  Verifique que la carpeta o archivo esté en su PC."
                )
                return self._selectLocalSource()
            else:
                self._ui.stepWarning(
                    f"Advertencia: El archivo '{path.name}' no es compatible.\n"
                    + "  Verifique que sea un archivo comprimido ("
                    + ", ".join(UNZIP_EXTENSIONS)
                    + ") o una imagen ("
                    + ", ".join(IMAGE_EXTENSIONS)
                    + ")."
                )
                return self._selectLocalSource()

        self._ui.console.print()
        self._ui.stepInfo("Procesando archivos locales")

        try:
            self._dataset_path = DATASETS_DIR / f"{time.strftime('%Y%m%d%H%M%S')}"
            self._dataset_path.mkdir(parents=True, exist_ok=True)

            if is_valid and type_detected == "folder":
                self._ui.stepSuccess("Directorio detectado.")

                if not self._dataset.copy(path, self._dataset_path, True):
                    raise Exception("No se pudo copiar el directorio.")

            elif is_valid and type_detected == "unzip":
                self._ui.stepSuccess("Archivo comprimido detectado.")
                copy_path = self._dataset_path / path.name

                if not self._dataset.copy(path, copy_path, False):
                    raise Exception("No se pudo copiar el archivo.")

                unzip_type = self._validator.unzipType(copy_path)
                if unzip_type == "zip":
                    if not self._dataset.unzipZIP(copy_path, self._dataset_path):
                        raise Exception("No se pudo descomprimir el archivo ZIP.")
                elif unzip_type == "rar":
                    if not self._dataset.unzipRAR(copy_path, self._dataset_path):
                        raise Exception("No se pudo descomprimir el archivo RAR.")
                elif unzip_type == "tar":
                    if not self._dataset.unzipTAR(copy_path, self._dataset_path):
                        raise Exception("No se pudo descomprimir el archivo TAR.")

            elif is_valid and type_detected == "image":
                self._ui.stepSuccess("Imagen detectada.")
                copy_path = self._dataset_path / path.name

                if not self._dataset.copy(path, copy_path, False):
                    raise Exception("No se pudo copiar la imagen.")

            if not self._scanAndValidate(self._dataset_path):
                self._cleanOnFail()
                return self._selectLocalSource()
            else:
                return path, self._dataset_path

        except Exception:
            self._cleanOnFail()
            raise

    def _selectDriveSource(self) -> tuple[str, Path]:
        url = self._ui.ask("Enlace de Google Drive")

        if not self._validator.validateGDURL(url):
            self._ui.stepWarning(
                "Advertencia: La URL no pertenece a Google Drive.\n"
                + "  Formato esperado: 'https://drive.google.com/...'"
            )
            return self._selectDriveSource()

        self._ui.console.print()
        self._ui.stepInfo("Conectando con Google Drive")

        try:
            self._dataset_path = DATASETS_DIR / f"{time.strftime('%Y%m%d%H%M%S')}"
            self._dataset_path.mkdir(parents=True, exist_ok=True)

            path = self._downloader.runGD(url, self._dataset_path)

            if path is None:
                raise Exception("No se pudo descargar el contenido de Google Drive.")

            is_valid, type_detected = self._validator.source(path)

            if is_valid and type_detected == "folder":
                self._ui.stepSuccess("Directorio detectado.")

            elif is_valid and type_detected == "unzip":
                self._ui.stepSuccess("Archivo comprimido detectado.")

                unzip_type = self._validator.unzipType(path)
                if unzip_type == "zip":
                    if not self._dataset.unzipZIP(path, self._dataset_path):
                        raise Exception("No se pudo descomprimir el archivo ZIP.")
                elif unzip_type == "rar":
                    if not self._dataset.unzipRAR(path, self._dataset_path):
                        raise Exception("No se pudo descomprimir el archivo RAR.")
                elif unzip_type == "tar":
                    if not self._dataset.unzipTAR(path, self._dataset_path):
                        raise Exception("No se pudo descomprimir el archivo TAR.")

            elif is_valid and type_detected == "image":
                self._ui.stepSuccess("Imagen detectada.")

            else:
                self._ui.stepWarning(
                    f"Advertencia: El archivo descargado '{path.name}' no es compatible.\n"
                    + "  Verifique que sea un archivo comprimido ("
                    + ", ".join(UNZIP_EXTENSIONS)
                    + ") o una imagen ("
                    + ", ".join(IMAGE_EXTENSIONS)
                    + ")."
                )
                self._cleanOnFail()
                return self._selectDriveSource()

            if not self._scanAndValidate(self._dataset_path):
                self._cleanOnFail()
                return self._selectDriveSource()
            else:
                return url, self._dataset_path

        except Exception:
            self._cleanOnFail()
            raise

    def _scanAndValidate(self, target_path: Path) -> bool:
        self._ui.console.print()
        self._ui.stepInfo("Procesando contenido")

        stats = self._dataset.scan(target_path)

        if stats["images"] > 0:
            self._ui.stepSuccess(
                f"Dataset válido detectado. {stats['images']} imágenes"
                + (" " if stats["labels"] == 0 else f"y {stats['labels']} etiquetas ")
                + "encontradas."
            )
            return True
        else:
            self._ui.stepWarning(
                "Advertencia: No se encontraron imágenes"
                + (" o etiquetas" if stats["labels"] <= 0 else "")
                + " en el dataset.\n"
                + "  Por favor, verifique que el dataset contenga imágenes"
                + (" o etiquetas." if stats["labels"] <= 0 else ".")
            )
            return False

    def _cleanOnFail(self) -> None:
        if self._dataset_path and self._dataset_path.exists():
            shutil.rmtree(str(self._dataset_path))
            self._dataset_path = None
