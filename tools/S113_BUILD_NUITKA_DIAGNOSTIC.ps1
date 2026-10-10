# S113 ONLY — diagnostic Nuitka standalone proof, NEVER a release build.
# Original Nuitka version and complete TLM source/Info provider are UNKNOWN.
$ErrorActionPreference = "Stop"
if (-not $IsWindows -and $PSVersionTable.PSEdition -eq "Core") {
    throw "S113_REQUIRES_WINDOWS"
}
python -m nuitka --standalone --mingw64 --assume-yes-for-downloads --enable-plugin=tk-inter --output-dir=artifacts/s113 --output-filename=S113_NUITKA_DIAGNOSTIC_NOT_PRODUCT.exe src/TLMTool.py
if ($LASTEXITCODE -ne 0) { throw "S113_NUITKA_COMPILE_FAILED" }
python tools/S113_VERIFY_NUITKA_DIAGNOSTIC.py artifacts/s113/TLMTool.dist artifacts/s113/verification.json
if ($LASTEXITCODE -ne 0) { throw "S113_NUITKA_DIAGNOSTIC_VERIFICATION_FAILED" }
