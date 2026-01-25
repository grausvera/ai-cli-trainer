import os
import time
import yaml
import random
import shutil
from pathlib import Path

from rich.progress import (
    BarColumn,
    FileSizeColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from core.constants import IMAGE_EXTENSIONS, LABEL_EXTENSIONS
from ui import BashUI


class Dataset:
    def __init__(self, ui: BashUI) -> None:
        self._ui: BashUI = ui

    def copy(self, source_path: Path, dest_folder: Path, is_folder: bool) -> bool:
        try:
            total: int = self._getTotalSize(source_path)

            action_title: str = (
                "📂 Copiando carpeta" if is_folder else "📄 Copiando archivo"
            )

            with Progress(
                SpinnerColumn(style="bar.pulse"),
                TextColumn("[bold white]{task.description}"),
                BarColumn(bar_width=None, style="white", finished_style="white"),
                TextColumn("{task.percentage:>3.0f}%"),
                TextColumn("•"),
                FileSizeColumn(),
                TextColumn("•"),
                TransferSpeedColumn(),
                TextColumn("•"),
                TimeRemainingColumn(),
                console=self._ui.console,
                transient=False,
            ) as progress:
                task: TaskID = progress.add_task(action_title, total=total)

                if is_folder:
                    for root, _, files in os.walk(source_path):
                        rel_path = Path(root).relative_to(source_path)
                        dest_path = dest_folder / rel_path
                        dest_path.mkdir(parents=True, exist_ok=True)

                        for file in files:
                            src_file = Path(root) / file
                            dest_file = dest_path / file

                            shutil.copy2(src_file, dest_file)
                            progress.update(task, advance=src_file.stat().st_size)
                else:
                    with (
                        open(source_path, "rb") as fsrc,
                        open(dest_folder, "wb") as fdst,
                    ):
                        chunk_size = 1024 * 1024
                        while True:
                            buf = fsrc.read(chunk_size)
                            if not buf:
                                break
                            fdst.write(buf)
                            progress.update(task, advance=len(buf))
            return True
        except Exception:
            raise

    def unzipZIP(self, zip_path: Path, dest_folder: Path) -> bool:
        try:
            import zipfile

            if not zipfile.is_zipfile(zip_path):
                return False

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                members: list[zipfile.ZipInfo] = zip_ref.infolist()
                total: int = sum(member.file_size for member in members)

                with Progress(
                    SpinnerColumn(style="bar.pulse"),
                    TextColumn("[bold white]{task.description}"),
                    BarColumn(bar_width=None, style="white", finished_style="white"),
                    TextColumn("{task.percentage:>3.0f}%"),
                    TextColumn("•"),
                    FileSizeColumn(),
                    TextColumn("•"),
                    TransferSpeedColumn(),
                    TextColumn("•"),
                    TimeRemainingColumn(),
                    console=self._ui.console,
                    transient=False,
                ) as progress:
                    task: TaskID = progress.add_task("🗃️  Descomprimiendo", total=total)

                    for member in members:
                        zip_ref.extract(member, path=dest_folder)
                        progress.update(task, advance=member.file_size)

            os.remove(zip_path)
            return True

        except Exception:
            raise

    def unzipRAR(self, rar_path: Path, dest_folder: Path) -> bool:
        try:
            import rarfile

            if not rarfile.is_rarfile(rar_path):
                return False

            with rarfile.RarFile(rar_path) as rar_ref:
                members: list[rarfile.RarInfo] = rar_ref.infolist()
                total: int = sum(member.file_size for member in members)

                with Progress(
                    SpinnerColumn(style="bar.pulse"),
                    TextColumn("[bold white]{task.description}"),
                    BarColumn(bar_width=None, style="white", finished_style="white"),
                    TextColumn("{task.percentage:>3.0f}%"),
                    TextColumn("•"),
                    FileSizeColumn(),
                    TextColumn("•"),
                    TransferSpeedColumn(),
                    TextColumn("•"),
                    TimeRemainingColumn(),
                    console=self._ui.console,
                    transient=False,
                ) as progress:
                    task: TaskID = progress.add_task(
                        "🗃️  Descomprimiendo RAR", total=total
                    )

                    for member in members:
                        rar_ref.extract(member, path=dest_folder)
                        progress.update(task, advance=member.file_size)

            os.remove(rar_path)
            return True

        except Exception:
            raise

    def unzipTAR(self, tar_path: Path, dest_folder: Path) -> bool:
        try:
            import tarfile

            if not tarfile.is_tarfile(tar_path):
                return False

            with tarfile.open(tar_path, "r:*") as tar_ref:
                members: list[tarfile.TarInfo] = tar_ref.getmembers()
                total: int = sum(member.size for member in members)

                with Progress(
                    SpinnerColumn(style="bar.pulse"),
                    TextColumn("[bold white]{task.description}"),
                    BarColumn(bar_width=None, style="white", finished_style="white"),
                    TextColumn("{task.percentage:>3.0f}%"),
                    TextColumn("•"),
                    FileSizeColumn(),
                    TextColumn("•"),
                    TransferSpeedColumn(),
                    TextColumn("•"),
                    TimeRemainingColumn(),
                    console=self._ui.console,
                    transient=False,
                ) as progress:
                    task: TaskID = progress.add_task(
                        "🗃️  Descomprimiendo TAR", total=total
                    )

                    for member in members:
                        tar_ref.extract(member, path=dest_folder)
                        progress.update(task, advance=member.size)

            os.remove(tar_path)
            return True

        except Exception:
            raise

    def scan(self, dataset_path: Path) -> dict[str, int]:
        try:
            stats: dict[str, int] = {"images": 0, "labels": 0}

            all_files: list[Path] = [f for f in dataset_path.rglob("*") if f.is_file()]

            with Progress(
                SpinnerColumn(style="bar.pulse"),
                TextColumn("[bold white]{task.description}"),
                BarColumn(bar_width=None, style="white", finished_style="white"),
                TextColumn("{task.percentage:>3.0f}%"),
                TextColumn("•"),
                MofNCompleteColumn(),
                TextColumn("•"),
                TimeElapsedColumn(),
                console=self._ui.console,
                transient=False,
            ) as progress:
                task: TaskID = progress.add_task(
                    "🔍 Escaneando contenido",
                    total=len(all_files),
                )

                for file in all_files:
                    progress.update(task, advance=1)
                    time.sleep(0.0001)

                    if file.suffix.lower() in IMAGE_EXTENSIONS:
                        stats["images"] += 1
                    elif file.suffix.lower() in LABEL_EXTENSIONS:
                        stats["labels"] += 1

            return stats

        except Exception:
            raise

    def normalize(
        self,
        dataset_path: Path,
        images_dir: Path,
        labels_dir: Path,
    ) -> tuple[bool, list[tuple[Path, Path]]]:
        try:
            all_files: list[Path] = [f for f in dataset_path.rglob("*") if f.is_file()]

            to_move: list[tuple[Path, Path]] = []
            for file in all_files:
                if file.parent == images_dir or file.parent == labels_dir:
                    continue

                if file.suffix.lower() in IMAGE_EXTENSIONS:
                    dest = images_dir / file.name
                elif file.suffix.lower() in LABEL_EXTENSIONS:
                    dest = labels_dir / file.name
                else:
                    continue

                if dest.exists():
                    raise Exception(f"El archivo {dest.name} ya existe (duplicado).")

                to_move.append((file, dest))

            with Progress(
                SpinnerColumn(style="bar.pulse"),
                TextColumn("[bold white]{task.description}"),
                BarColumn(bar_width=None, style="white", finished_style="white"),
                TextColumn("{task.percentage:>3.0f}%"),
                TextColumn("•"),
                MofNCompleteColumn(),
                console=self._ui.console,
                transient=False,
            ) as progress:
                task: TaskID = progress.add_task(
                    "🧮 Normalizando dataset",
                    total=len(to_move),
                )

                for src, dst in to_move:
                    shutil.move(str(src), str(dst))
                    progress.update(task, advance=1)
                    time.sleep(0.0001)

            if not to_move:
                self._cleanFiles(dataset_path, images_dir, labels_dir)
                self._cleanFolders(dataset_path, images_dir, labels_dir)
                return True, []

            self._cleanFiles(dataset_path, images_dir, labels_dir)
            self._cleanFolders(dataset_path, images_dir, labels_dir)
            return True, to_move

        except Exception:
            raise

    def integrity(
        self,
        dataset_path: Path,
        images_dir: Path,
        labels_dir: Path,
    ) -> tuple[list[str], list[str]]:
        try:
            image_files: dict[str, Path] = {
                f.stem: f
                for f in images_dir.glob("*")
                if f.suffix.lower() in IMAGE_EXTENSIONS
            }
            label_files: dict[str, Path] = {
                f.stem: f
                for f in labels_dir.glob("*")
                if f.suffix.lower() in LABEL_EXTENSIONS
            }

            all_stems: list[str] = list(image_files.keys() | label_files.keys())
            valid_pairs: list[str] = []
            orphans: list[str] = []

            with Progress(
                SpinnerColumn(style="bar.pulse"),
                TextColumn("[bold white]{task.description}"),
                BarColumn(bar_width=None, style="white", finished_style="white"),
                TextColumn("{task.percentage:>3.0f}%"),
                TextColumn("•"),
                MofNCompleteColumn(),
                console=self._ui.console,
                transient=False,
            ) as progress:
                task: TaskID = progress.add_task(
                    "⛓️‍💥 Verificando integridad",
                    total=len(all_stems),
                )

                for stem in all_stems:
                    has_image = stem in image_files
                    has_label = stem in label_files

                    if has_image and has_label:
                        valid_pairs.append(stem)
                    else:
                        orphans.append(stem)

                    progress.update(task, advance=1)
                    time.sleep(0.0001)

            if len(orphans) > 0:
                orphans_images_dir = dataset_path / "orphans" / "images"
                orphans_labels_dir = dataset_path / "orphans" / "labels"
                orphans_images_dir.mkdir(parents=True, exist_ok=True)
                orphans_labels_dir.mkdir(parents=True, exist_ok=True)
                for orphan in orphans:
                    shutil.move(
                        str(images_dir / f"{orphan}.*"),
                        str(orphans_images_dir / f"{orphan}.*"),
                    )
                    shutil.move(
                        str(labels_dir / f"{orphan}.*"),
                        str(orphans_labels_dir / f"{orphan}.*"),
                    )

            return valid_pairs, orphans
        except Exception:
            raise

    def split(
        self,
        stems: list[str],
        dataset_path: Path,
        images_dir: Path,
        labels_dir: Path,
    ) -> tuple[list[str], list[str]]:
        try:
            dirs = {
                "images_train": dataset_path / "train" / "images",
                "labels_train": dataset_path / "train" / "labels",
                "images_val": dataset_path / "val" / "images",
                "labels_val": dataset_path / "val" / "labels",
            }

            for d in dirs.values():
                d.mkdir(parents=True, exist_ok=True)

            random.shuffle(stems)
            split_idx = int(len(stems) * 0.8)
            train_stems = stems[:split_idx]
            val_stems = stems[split_idx:]

            with Progress(
                SpinnerColumn(style="bar.pulse"),
                TextColumn("[bold white]{task.description}"),
                BarColumn(bar_width=None, style="white", finished_style="white"),
                TextColumn("{task.percentage:>3.0f}%"),
                TextColumn("•"),
                MofNCompleteColumn(),
                console=self._ui.console,
                transient=False,
            ) as progress:
                task: TaskID = progress.add_task(
                    "🔍 Moviendo pares de datos",
                    total=len(stems),
                )

                self._moveBatch(
                    train_stems,
                    images_dir,
                    labels_dir,
                    dirs["images_train"],
                    dirs["labels_train"],
                )
                self._moveBatch(
                    val_stems,
                    images_dir,
                    labels_dir,
                    dirs["images_val"],
                    dirs["labels_val"],
                )
                shutil.rmtree(str(images_dir))
                shutil.rmtree(str(labels_dir))
                progress.update(task, completed=len(stems))
                time.sleep(0.0001)

            return train_stems, val_stems

        except Exception:
            raise

    def generateYAML(self, dataset_path: Path, classes: list[str]) -> tuple[bool, Path]:
        try:
            yaml_data = {
                "path": str(dataset_path),
                "train": "train/images",
                "val": "val/images",
                "nc": len(classes),
                "names": {i: name for i, name in enumerate(classes)},
            }

            yaml_path = dataset_path / "data.yaml"
            with open(yaml_path, "w") as f:
                yaml.dump(yaml_data, f, sort_keys=False)

            return True, yaml_path

        except Exception:
            raise

    def _getTotalSize(self, path: Path) -> int:
        if path.is_file():
            return path.stat().st_size

        total = 0
        for p in path.rglob("*"):
            if p.is_file():
                total += p.stat().st_size
        return total

    def _cleanFiles(
        self,
        dataset_path: Path,
        images_dir: Path,
        labels_dir: Path,
    ) -> None:
        for p in dataset_path.rglob("*"):
            if (
                p.is_file()
                and p.parent not in [images_dir, labels_dir]
                and (
                    p.suffix.lower() not in IMAGE_EXTENSIONS
                    and p.suffix.lower() not in LABEL_EXTENSIONS
                )
            ):
                p.unlink()

    def _cleanFolders(
        self,
        dataset_path: Path,
        images_dir: Path,
        labels_dir: Path,
    ) -> None:
        for p in dataset_path.rglob("*"):
            if p.is_dir() and p not in [images_dir, labels_dir]:
                shutil.rmtree(str(p))

    def _moveBatch(
        self,
        stems: list[str],
        source_images: Path,
        source_labels: Path,
        dest_images: Path,
        dest_labels: Path,
    ) -> None:
        for stem in stems:
            images = list(source_images.glob(f"{stem}.*"))
            labels = list(source_labels.glob(f"{stem}.*"))

            if len(images) != 1 or len(labels) != 1:
                file_type = "imagen" if len(images) == 1 else "etiqueta"
                raise Exception(f"No se encontró la {file_type} para el stem: {stem}")

            shutil.move(str(images[0]), str(dest_images / images[0].name))
            shutil.move(str(labels[0]), str(dest_labels / labels[0].name))
