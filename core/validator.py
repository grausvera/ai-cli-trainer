import zipfile
import rarfile
import tarfile
from pathlib import Path

from core.constants import IMAGE_EXTENSIONS, LABEL_EXTENSIONS, UNZIP_EXTENSIONS


class Validator:
    @staticmethod
    def source(path: Path) -> tuple[bool, str]:
        if not path.exists():
            return False, "path_not_found"

        if path.is_dir():
            return True, "folder"
        elif path.is_file():
            if Validator.unzip(path):
                return True, "unzip"
            elif Validator.image(path):
                return True, "image"
            elif Validator.label(path):
                return True, "label"
            else:
                return False, "file_unsupported"
        else:
            return False, "path_invalid"

    @staticmethod
    def validateGDURL(url: str) -> bool:
        if not url or not isinstance(url, str) or "drive.google.com" not in url:
            return False
        return True

    @staticmethod
    def model(path: Path) -> bool:
        if not path.exists():
            return False
        elif path.is_file() and path.suffix.lower() == ".pt":
            return True
        else:
            return False

    @staticmethod
    def image(path: Path) -> bool:
        if not path.exists():
            return False
        elif path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            return True
        else:
            return False

    @staticmethod
    def label(path: Path) -> bool:
        if not path.exists():
            return False
        elif path.is_file() and path.suffix.lower() in LABEL_EXTENSIONS:
            return True
        else:
            return False

    @staticmethod
    def unzip(path: Path) -> bool:
        if not path.exists():
            return False
        elif path.is_file() and path.suffix.lower() in UNZIP_EXTENSIONS:
            return True
        else:
            return False

    @staticmethod
    def unzipType(path: Path) -> str:
        if not path.exists():
            return "path_not_found"
        elif path.is_file() and path.suffix.lower() in UNZIP_EXTENSIONS:
            if zipfile.is_zipfile(path):
                return "zip"
            elif rarfile.is_rarfile(path):
                return "rar"
            elif tarfile.is_tarfile(path):
                return "tar"
            else:
                return "unzip_invalid"
        else:
            return "path_invalid"
