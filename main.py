"""
TRAINER (AI-CLI-TRAINER)
------------------------------
Herramienta CLI para entrenamiento automatizado de modelos YOLO.

@author: grausvera
@license: MIT
@version: 1.0.0
"""

import sys
import shutil
from pathlib import Path

from core.constants import APP_NAME, APP_SUBTITLE
from core import Dataset, Downloader, Validator
from ui import BashUI
from ui.seccions import SectionOne, SectionTwo, SectionThree


def safeClean(context: dict[str, object]) -> None:
    if context:
        dataset_path: Path = context.get("dataset_path", None)
        if dataset_path and isinstance(dataset_path, Path) and dataset_path.exists():
            shutil.rmtree(str(dataset_path), ignore_errors=True)

        trained_model_path: Path = context.get("trained_model_path", None)
        if (
            trained_model_path
            and isinstance(trained_model_path, Path)
            and trained_model_path.exists()
        ):
            shutil.rmtree(str(trained_model_path), ignore_errors=True)

        context.clear()


def main():
    ui = BashUI()
    validator = Validator()
    dataset = Dataset(ui)
    downloader = Downloader(ui)

    context: dict[str, object] = {}

    try:
        ui.header(APP_NAME, APP_SUBTITLE)

        SectionOne(ui, validator, dataset, downloader).run(context)
        SectionTwo(ui, validator, dataset).run(context)
        SectionThree(ui, validator, dataset, downloader).run(context)

        ui.footer(context)

    except KeyboardInterrupt:
        ui.console.print()
        ui.stepError("Operación cancelada por el usuario.")
        safeClean(context)
        sys.exit(0)
    except Exception as e:
        ui.console.print()
        ui.stepError(f"Error inesperado: {e}")
        safeClean(context)
        sys.exit(1)


if __name__ == "__main__":
    main()
