# -*- mode: python ; coding: utf-8 -*-
import os
import subprocess
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

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

# Install browsers before building
try:
    subprocess.run(["playwright", "install", "chromium"], check=True)
    print("Playwright browsers installed")
except:
    print("Could not install browsers - may need manual installation")

# Add playwright browsers to data files
playwright_browsers = []
try:
    import playwright
    playwright_path = os.path.dirname(playwright.__file__)
    browsers_path = os.path.join(playwright_path, "driver", "package", ".local-browsers")
    if os.path.exists(browsers_path):
        for root, dirs, files in os.walk(browsers_path):
            for file in files:
                src = os.path.join(root, file)
                dst = os.path.relpath(src, playwright_path)
                playwright_browsers.append((src, os.path.join("playwright", dst)))
except:
    pass

# Add to datas
added_files.extend(playwright_browsers)

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
        'datetime',
        'openpyxl',
        'openpyxl.workbook',
        'openpyxl.worksheet',
        'openpyxl.styles'
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
    console=True,  # Set to True if you need console for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)