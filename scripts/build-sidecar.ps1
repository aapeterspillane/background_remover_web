# Build script for the Python backend sidecar (Windows)

$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectDir

Write-Host "Building backend sidecar..."

# Detect target triple
$Arch = [System.Environment]::GetEnvironmentVariable("PROCESSOR_ARCHITECTURE")
if ($Arch -eq "AMD64") {
    $TargetTriple = "x86_64-pc-windows-msvc"
} elseif ($Arch -eq "ARM64") {
    $TargetTriple = "aarch64-pc-windows-msvc"
} else {
    $TargetTriple = "i686-pc-windows-msvc"
}

Write-Host "Target triple: $TargetTriple"

# Ensure PyInstaller is installed
pip install pyinstaller --quiet

# Build with PyInstaller
pyinstaller backend.spec --noconfirm --clean

# Create binaries directory if it doesn't exist
New-Item -ItemType Directory -Force -Path "src-tauri\binaries" | Out-Null

# Copy the built binary to the Tauri binaries directory with target triple suffix
Copy-Item "dist\backend.exe" "src-tauri\binaries\backend-$TargetTriple.exe"

Write-Host "Sidecar built successfully: src-tauri\binaries\backend-$TargetTriple.exe"
