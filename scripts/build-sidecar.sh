#!/bin/bash
# Build script for the Python backend sidecar

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "Building backend sidecar..."

# Detect target triple
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    ARCH=$(uname -m)
    if [[ "$ARCH" == "arm64" ]]; then
        TARGET_TRIPLE="aarch64-apple-darwin"
    else
        TARGET_TRIPLE="x86_64-apple-darwin"
    fi
elif [[ "$OSTYPE" == "linux"* ]]; then
    # Linux
    ARCH=$(uname -m)
    if [[ "$ARCH" == "aarch64" ]]; then
        TARGET_TRIPLE="aarch64-unknown-linux-gnu"
    else
        TARGET_TRIPLE="x86_64-unknown-linux-gnu"
    fi
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

echo "Target triple: $TARGET_TRIPLE"

# Ensure PyInstaller is installed
pip install pyinstaller --quiet

# Build with PyInstaller
pyinstaller backend.spec --noconfirm --clean

# Create binaries directory if it doesn't exist
mkdir -p src-tauri/binaries

# Copy the built binary to the Tauri binaries directory with target triple suffix
cp "dist/backend" "src-tauri/binaries/backend-$TARGET_TRIPLE"

echo "Sidecar built successfully: src-tauri/binaries/backend-$TARGET_TRIPLE"
