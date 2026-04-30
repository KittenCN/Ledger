# Build Ledger

This repository can be rebuilt on Windows with `cx_Freeze`.

## Prerequisites

- Python 3.13 or another supported Python 3 version installed
- WebView2 runtime available on Windows

## Recommended build flow

Use the helper script. It creates an isolated `.venv-build` environment so the build does not modify your main Python environment.

```powershell
.\build.ps1
```

## Manual build

Create a dedicated virtual environment:

```powershell
python -m venv .venv-build
```

Install build dependencies:

```powershell
.\.venv-build\Scripts\python.exe -m pip install --upgrade pip
.\.venv-build\Scripts\python.exe -m pip install -r requirements-build.txt
```

Run the build:

```powershell
.\.venv-build\Scripts\python.exe setup.py build_exe
```

## Build output

The packaged application is written to:

```text
build/Ledger/
```

The executable will be:

```text
build/Ledger/Ledger.exe
```

## Notes

- The `resource/` directory is embedded into the packaged application during build and is not shipped as plain source files in `build/Ledger/`.
- At runtime the embedded resources are extracted to a temporary directory so `pywebview` can load the HTML entry page.
- After build, the cx_Freeze archive is renamed from `lib/library.zip` to `lib/library.dll`. It is still a zip-format payload internally.
- Activation files are not bundled. Place `activation.config`, `activation.txt`, or `license.key` next to the packaged executable or inside its `resource/` directory.
- The checked-in `Ledger/` directory is an older frozen output and should be treated as a reference artifact, not as the build source.
- `requirements-build.txt` pins the tested packaging versions used by this repository.
