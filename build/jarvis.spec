# build/jarvis.spec — Dynamic PyInstaller Spec File for J.A.R.V.I.S. Standalone Executable
# Run with: pyinstaller build/jarvis.spec --noconfirm --clean

import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

project_root = Path(os.getenv("JARVIS_ROOT", os.getcwd())).resolve()

# 1. Collect Data Files & ONNX Model Binaries Dynamically
datas = [
    (str(project_root / "data"), "data"),
    (str(project_root / "mcp_config.json"), "."),
]

# Add PySide6 assets and ONNX runtimes if installed
try:
    datas += collect_data_files("PySide6")
    datas += collect_data_files("onnxruntime")
except Exception:
    pass

# 2. Hidden Imports (Dynamic Modules)
hiddenimports = [
    "uvicorn.logging", "uvicorn.loops.asyncio", "uvicorn.protocols.http.h11_impl",
    "fastapi", "pydantic", "chromadb", "faster_whisper", "sounddevice",
    "psutil", "wmi", "requests", "httpx", "websockets"
]
try:
    hiddenimports += collect_submodules("jarvis")
except Exception:
    pass

a = Analysis(
    [str(project_root / "jarvis" / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="jarvis",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
