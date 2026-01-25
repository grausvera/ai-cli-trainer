import re
from pathlib import Path

from core.constants import SECTION_TWO_TITLE
from core import Dataset, Validator
from ui import BashUI


class SectionTwo:
    def __init__(
        self,
        ui: BashUI,
        validator: Validator,
        dataset: Dataset,
    ) -> None:
        self._ui: BashUI = ui
        self._validator: Validator = validator
        self._dataset: Dataset = dataset

    def run(self, context: dict[str, object]) -> None:
        self._dataset_path: Path = context["dataset_path"]
        self._images_dir: Path = self._dataset_path / "images"
        self._labels_dir: Path = self._dataset_path / "labels"

        rel_path = f"{self._dataset_path.parent.name}/{self._dataset_path.name}"
        self._ui.section(SECTION_TWO_TITLE, subtitle=f"Destino: {rel_path}")

        try:
            self._images_dir.mkdir(exist_ok=True)
            self._labels_dir.mkdir(exist_ok=True)

            normalized, to_move = self._dataset.normalize(
                self._dataset_path,
                self._images_dir,
                self._labels_dir,
            )
            if not normalized:
                raise Exception("No se pudo normalizar el dataset.")
            elif normalized and len(to_move) > 0:
                self._ui.stepSuccess(
                    "Estructura del dataset normalizada correctamente.\n"
                    f"  {len(to_move)} archivos movidos."
                )
            else:
                self._ui.stepSuccess("La estructura del dataset ya está normalizada")

            self._ui.console.print()
            pairs, orphans = self._dataset.integrity(
                self._dataset_path,
                self._images_dir,
                self._labels_dir,
            )
            if len(pairs) == 0:
                raise Exception("No hay pares válidos para procesar.")
            else:
                context["amount_pairs"] = len(pairs)
                self._ui.stepSuccess(
                    f"Integridad verificada: {len(pairs)} pares válidos.\n"
                    f"  Todas las imágenes tienen su etiqueta correspondiente."
                )
                if len(orphans) > 0:
                    context["amount_orphans"] = len(orphans)
                    self._ui.stepWarning(
                        f"Se encontraron {len(orphans)} imágenes huérfanas.\n"
                        f"  Se han movido a la carpeta '{self._dataset_path.name}/orphans'."
                    )

            self._ui.console.print()
            train_stems, val_stems = self._dataset.split(
                pairs,
                self._dataset_path,
                self._images_dir,
                self._labels_dir,
            )
            if len(train_stems) == 0 or len(val_stems) == 0 or len(orphans) > 0:
                raise Exception("No se pudo dividir el dataset.")
            else:
                context["amount_train"] = len(train_stems)
                context["amount_val"] = len(val_stems)
                self._ui.stepSuccess(
                    f"Split completado: {len(train_stems)} pares para entrenamiento y {len(val_stems)} pares para validación."
                )

            self._ui.console.print()
            classes = self._askForClasses()
            context["classes"] = classes

            self._ui.console.print()
            success, yaml_path = self._dataset.generateYAML(self._dataset_path, classes)
            if not success or not yaml_path:
                raise Exception("No se pudo generar el archivo data.yaml.")
            else:
                context["yaml_path"] = yaml_path
                self._ui.stepSuccess(
                    "YAML generado correctamente.\n"
                    + f"  Ruta:                  {rel_path}\n"
                    + "  Ruta de entrenamiento: train/images\n"
                    + "  Ruta de validación:    val/images\n"
                    + f"  Clases (nc):           {len(classes)}\n"
                    + f"  Nombres:               {', '.join(classes)}"
                )

        except Exception:
            raise

    def _askForClasses(self, classes: list[str] = []) -> list[str]:
        class_names = self._ui.ask("Nombres de clases (separados por coma)")

        chunks = [
            self._parseClassName(class_name)
            for class_name in class_names.split(",")
            if class_name.strip()
        ]

        for chunk in chunks:
            if chunk in classes:
                self._ui.stepWarning(
                    f"Advertencia: El nombre de clase '{chunk}' ya existe.\n"
                    "  Por favor ingrese un nombre de clase diferente."
                )
                continue
            elif "=" in chunk:
                parts = chunk.split("=")
                old_name, new_name = parts

                if old_name in classes:
                    classes[classes.index(old_name)] = new_name
                else:
                    self._ui.stepWarning(
                        f"Advertencia: La clase '{old_name}' no existe.\n"
                        "  Por favor ingrese una clase existente para modificar."
                    )
                    continue
            else:
                classes.append(chunk)

        if len(classes) > 0:
            self._ui.stepSuccess(
                f"Se han definido {len(classes)} clases para el dataset.\n"
                f"  {', '.join(classes)}"
            )

            self._ui.console.print()
            confirm = self._ui.askConfirm(
                "Modificar o agregar más clases",
                default=True,
            )
            if confirm:
                return self._askForClasses(classes)
            else:
                return classes
        else:
            self._ui.stepWarning(
                "No se ingresaron nombres de clases válidos.\n"
                "  Por favor ingrese nombres de clases válidos separados por coma."
                "  Ejemplo: 'clase,clase1,clase_2'"
            )
            return self._askForClasses(classes)

    def _parseClassName(self, raw_name: str) -> str:
        if raw_name.count("=") != 1:
            return self._sanitizeClassName(raw_name)

        parts = raw_name.split("=", 1)
        old = self._sanitizeClassName(parts[0])
        new = self._sanitizeClassName(parts[1])

        if not old or not new:
            return self._sanitizeClassName(raw_name)

        return f"{old}={new}"

    def _sanitizeClassName(self, raw_name: str) -> str:
        text = raw_name.strip().lower()
        text = re.sub(r"\s+", "_", text)
        text = re.sub(r"[^\w]", "", text)
        text = re.sub(r"_+", "_", text)
        text = text.strip("_")

        return text
