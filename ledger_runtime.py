import base64
import hashlib
import importlib
import io
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path


APP_NAME = "Ledger"
ROOT_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent


def _load_embedded_resources():
    return importlib.import_module("ledger_embedded_resources")


def _extract_embedded_resources(target_dir: Path):
    embedded_resources = _load_embedded_resources()
    archive_bytes = base64.b64decode(embedded_resources.RESOURCE_ARCHIVE_B64)
    archive_hash = hashlib.sha256(archive_bytes).hexdigest()
    if archive_hash != embedded_resources.RESOURCE_ARCHIVE_SHA256:
        raise RuntimeError("Embedded resource archive integrity check failed.")

    target_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive_file:
        archive_file.extractall(target_dir)


def get_runtime_resource_dir():
    if not getattr(sys, "frozen", False):
        return ROOT_DIR / "resource"

    embedded_resources = _load_embedded_resources()
    cache_root = Path(tempfile.gettempdir()) / f"{APP_NAME}Runtime"
    target_dir = cache_root / embedded_resources.RESOURCE_ARCHIVE_SHA256
    app_html = target_dir / "App.html"

    if app_html.is_file():
        return target_dir

    if target_dir.exists():
        shutil.rmtree(target_dir, ignore_errors=True)

    _extract_embedded_resources(target_dir)
    return target_dir
