# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

from PyInstaller.utils.hooks import collect_submodules

# Collect all submodules of encodings
hiddenimports = collect_submodules('encodings') + [
    'importlib_metadata', 
    'pickle', 
    'shutil', 
    'subprocess'
]

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[('templates/index.html', 'templates'), ('start.py', '.'), ('app.py', '.')],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=['runtime_hook.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='StockDataViewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set to False if you want windowed mode (no console)
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StockDataViewer',
)
