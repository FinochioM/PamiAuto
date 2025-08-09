# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Collect playwright data
try:
    playwright_data = collect_data_files('playwright')
except:
    playwright_data = []

# Define data files to include
added_files = [
    ('ui/main.ui', 'ui'),  # UI file
]

# Add playwright data
added_files.extend(playwright_data)

# Add any existing image files from ui folder
image_files = [
    ('ui/Bioimagenes2.png', '.'),
    ('ui/cropped-cropped-iso-bioimagenes2-32x32-1-32x32.png', '.')
]

for img_file, dest in image_files:
    if os.path.exists(img_file):
        added_files.append((img_file, dest))

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets', 
        'PyQt6.QtGui',
        'PyQt6.uic',
        'playwright',
        'playwright.sync_api',
        'gspread',
        'google.oauth2.service_account',
        'google.auth',
        'pandas',
        'requests',
        'dateutil',
        'dateutil.relativedelta',
        'json',
        'os',
        'sys',
        'threading',
        'time',
        'datetime'
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
    name='PamiAutomation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you need console for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)