import base64
import hashlib
import io
import zipfile
from pathlib import Path


FIXED_TIMESTAMP = (2024, 1, 1, 0, 0, 0)


def build_resource_module(resource_dir: Path, output_file: Path):
    resource_dir = Path(resource_dir)
    output_file = Path(output_file)
    files = sorted(path for path in resource_dir.rglob("*") if path.is_file())

    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(archive_buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive_file:
        for file_path in files:
            archive_name = file_path.relative_to(resource_dir).as_posix()
            archive_info = zipfile.ZipInfo(archive_name, FIXED_TIMESTAMP)
            archive_info.compress_type = zipfile.ZIP_DEFLATED
            archive_file.writestr(archive_info, file_path.read_bytes())

    archive_bytes = archive_buffer.getvalue()
    archive_hash = hashlib.sha256(archive_bytes).hexdigest()
    archive_b64 = base64.b64encode(archive_bytes).decode("ascii")

    output_file.write_text(
        "\n".join(
            [
                '"""Generated file. Do not edit by hand."""',
                "",
                f'RESOURCE_ARCHIVE_SHA256 = "{archive_hash}"',
                f'RESOURCE_ARCHIVE_B64 = "{archive_b64}"',
                "",
            ]
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    build_resource_module(project_root / "resource", project_root / "ledger_embedded_resources.py")
