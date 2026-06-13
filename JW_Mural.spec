# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

mpl_datas, mpl_binaries, mpl_hiddenimports = collect_all('matplotlib')
ttk_datas, ttk_binaries, ttk_hiddenimports = collect_all('ttkbootstrap')

a = Analysis(
    ['src/layout.py'],
    pathex=[],
    binaries=mpl_binaries + ttk_binaries,
    datas=[
        ('assets', 'assets'),
        ('src/database', 'database'),
        ('src/process', 'process'),
        ('src/util', 'util'),
        ('Templates', 'Templates'),
        ('documentosCriados', 'documentosCriados'),
        ('.env', '.'),
    ] + mpl_datas + ttk_datas,
    hiddenimports=[
        'ttkbootstrap',
        'ttkbootstrap.themes',
        'ttkbootstrap.style',
        'ttkbootstrap.widgets',
        'ttkbootstrap.dialogs',
        'ttkbootstrap.dialogs.colorchooser',
        'ttkbootstrap.dialogs.dialogs',
        'pymongo',
        'docx',
        'PIL',
        'requests',
        'bs4',
        'dotenv',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends.backend_agg',
    ] + mpl_hiddenimports + ttk_hiddenimports,
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
    upx=False,
    console=False,
    icon='assets/jw_mural_icon.ico',
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
    upx=False,
    upx_exclude=[],
    name='JW_Mural',
)
