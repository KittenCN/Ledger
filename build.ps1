$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$buildDir = Join-Path $root "build"
$venvDir = Join-Path $root ".venv-build"
$venvPython = Join-Path $venvDir "Scripts\\python.exe"
$targetLibDir = Join-Path $buildDir "Ledger\\lib"
$libraryZip = Join-Path $targetLibDir "library.zip"
$libraryDll = Join-Path $targetLibDir "library.dll"
$libraryDat = Join-Path $targetLibDir "library.dat"

Set-Location $root

if (Test-Path $buildDir) {
    Remove-Item -LiteralPath $buildDir -Recurse -Force
}

if (-not (Test-Path $venvPython)) {
    python -m venv $venvDir
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create build virtual environment."
    }
}

& $venvPython -m pip install --upgrade pip --no-cache-dir
if ($LASTEXITCODE -ne 0) {
    throw "Failed to upgrade pip in build virtual environment."
}

& $venvPython -m pip install --no-cache-dir -r requirements-build.txt
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install build dependencies."
}

& $venvPython setup.py build
if ($LASTEXITCODE -ne 0) {
    throw "Build failed."
}

if (Test-Path $libraryDll) {
    Remove-Item -LiteralPath $libraryDll -Force
}

if (Test-Path $libraryZip) {
    Rename-Item -LiteralPath $libraryZip -NewName "library.dll"
}
else {
    throw "Expected archive not found: $libraryZip"
}

if (Test-Path $libraryDat) {
    Set-Content -LiteralPath $libraryDat -Value "library.dll" -NoNewline -Encoding ascii
}
else {
    throw "Expected library metadata not found: $libraryDat"
}

if (-not (Test-Path $libraryDll)) {
    throw "Renamed archive not found: $libraryDll"
}

if (Test-Path $libraryZip) {
    throw "Unexpected leftover archive found: $libraryZip"
}

Write-Host ""
Write-Host "Build completed:" -ForegroundColor Green
Write-Host "  $buildDir\\Ledger\\Ledger.exe"
Write-Host "Embedded archive renamed to lib\\library.dll and still handled as a zip payload."
