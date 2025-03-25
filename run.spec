# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include your project's source directory to ensure modules can be found
        ('./src', 'src'),
        ('./icons', 'icons'),
    ],
    hiddenimports=[
        'main', 
        'ui.main_window', 
        'utils.image_utils', 
        'utils.icon_utils',
        'cv2',
        'numpy',
        'PIL',
        'PIL._imaging',
        'PIL.Image',
        # Add any other modules that might be imported dynamically
    ],
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
    name='TransForm',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TransForm',
)

# For macOS, create a proper .app bundle
app = BUNDLE(
    coll,
    name='TransForm.app',
    icon="icons/app-light.icns",
    bundle_identifier=None,
    codesign_identity=None,  # Set to your Apple Developer ID if you have one
    entitlements_file=None,
)