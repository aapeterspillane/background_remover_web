# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for building the backend sidecar."""

import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, copy_metadata

block_cipher = None

# Find the u2net model - check multiple possible locations
possible_model_paths = [
    Path.home() / ".u2net" / "u2net.onnx",
    Path(os.environ.get("U2NET_HOME", "")) / "u2net.onnx" if os.environ.get("U2NET_HOME") else None,
    Path("/Users/runner/.u2net/u2net.onnx"),  # GitHub Actions macOS
    Path("C:/Users/runneradmin/.u2net/u2net.onnx"),  # GitHub Actions Windows
]

# Collect model files if they exist
datas = []
for model_path in possible_model_paths:
    if model_path and model_path.exists():
        print(f"Found u2net model at: {model_path}")
        datas.append((str(model_path), 'u2net_models'))
        break
else:
    print("WARNING: u2net model not found! The app will need to download it on first run.")

# Add package metadata for packages that use importlib.metadata
datas += copy_metadata('pymatting')
datas += copy_metadata('rembg')
datas += copy_metadata('onnxruntime')

# Collect all submodules for packages that have dynamic imports
hiddenimports_extra = collect_submodules('pymatting')

a = Analysis(
    ['backend/sidecar_main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'rembg',
        'rembg.sessions',
        'rembg.sessions.u2net',
        'onnxruntime',
        'PIL',
        'PIL.Image',
        'fastapi',
        'starlette',
        'starlette.routing',
        'starlette.middleware',
        'starlette.middleware.cors',
        'pydantic',
        'anyio',
        'anyio._backends',
        'anyio._backends._asyncio',
        'multipart',
        'python_multipart',
        'backend',
        'backend.main',
        'backend.routes',
        'backend.routes.process',
        'backend.image_processor',
        'backend.utils',
        'backend.utils.file_handling',
    ] + hiddenimports_extra,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
