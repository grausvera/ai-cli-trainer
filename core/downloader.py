import gdown
import shutil
import requests
from pathlib import Path

from rich.progress import (
    BarColumn,
    FileSizeColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from ui import BashUI


class Downloader:
    def __init__(self, ui: BashUI) -> None:
        self._ui: BashUI = ui

    def runGD(self, url: str, dest_folder: Path) -> Path | None:
        dest_folder.mkdir(parents=True, exist_ok=True)
        action_title = "carpeta" if self._isGDFolder(url) else "archivo"

        try:
            with Progress(
                SpinnerColumn(style="bar.pulse"),
                TextColumn("[bold white]{task.description}"),
                TextColumn("•"),
                TimeElapsedColumn(),
                console=self._ui.console,
                transient=False,
            ) as progress:
                progress.add_task(
                    f"📥 Descargando {action_title}... (Esto puede tardar unos minutos)",
                    total=None,
                )

                if self._isGDFolder(url):
                    files = gdown.download_folder(
                        url,
                        output=str(dest_folder),
                        quiet=True,
                        use_cookies=False,
                    )

                    return dest_folder if files else None

                else:
                    output_file = gdown.download(url, quiet=True, fuzzy=True)

                    if output_file:
                        source = Path(output_file)
                        final_path = dest_folder / source.name
                        shutil.move(str(source), str(final_path))
                        return final_path

                    return None

        except Exception:
            raise

    def runYOLO(self, url: str, dest_path: Path) -> bool:
        try:
            response = requests.get(url, stream=True)
            total = int(response.headers.get("content-length", 0))

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
                task = progress.add_task("📥 Descargando modelo", total=total)

                with open(dest_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))

            return True

        except Exception:
            raise

    def _isGDFolder(self, url: str) -> bool:
        return "/folders/" in url or "drive.google.com/drive/folders/" in url

    def _isGDFile(self, url: str) -> bool:
        return "file/d/" in url or "drive.google.com/file/d/" in url
