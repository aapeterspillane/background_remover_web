# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for building the backend sidecar."""

import os
import sys
from pathlib import Path

block_cipher = None

# Find the u2net model in the user's home directory
home_dir = Path.home()
u2net_home = home_dir / ".u2net"
u2net_model = u2net_home / "u2net.onnx"

# Collect model files if they exist
datas = []
if u2net_model.exists():
    datas.append((str(u2net_model), 'u2net_models'))

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
    ],
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
