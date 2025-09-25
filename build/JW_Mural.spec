# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['..\\layout.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('documentosCriados', 'documentosCriados'), ('Templates', 'Templates'), ('util', 'util'), ('process', 'process'), ('database', 'database'), ('Template.docx', '.'), ('.env', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='JW_Mural',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JW_Mural',
)
