# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import subprocess
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

# Collect playwright data
playwright_data = []
playwright_bins = []

try:
    import playwright
    playwright_path = os.path.dirname(playwright.__file__)
    
    # Collect playwright package data
    playwright_data = collect_data_files('playwright')
    playwright_bins = collect_dynamic_libs('playwright')
    
    # Add driver files
    driver_path = os.path.join(playwright_path, 'driver')
    if os.path.exists(driver_path):
        for root, dirs, files in os.walk(driver_path):
            for file in files:
                src = os.path.join(root, file)
                dst = os.path.relpath(root, os.path.dirname(playwright_path))
                playwright_data.append((src, dst))
    
    # Install browsers before building
    print("Installing Playwright browsers...")
    env = os.environ.copy()
    env['PLAYWRIGHT_BROWSERS_PATH'] = '0'  # Use default location
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                   check=True, env=env)
    
    # Find and include browser files
    home = os.path.expanduser("~")
    browser_paths = [
        os.path.join(home, "AppData", "Local", "ms-playwright"),
        os.path.join(playwright_path, "driver", "package", ".local-browsers"),
    ]
    
    for browser_path in browser_paths:
        if os.path.exists(browser_path):
            print(f"Found browsers at: {browser_path}")
            for root, dirs, files in os.walk(browser_path):
                for file in files:
                    src = os.path.join(root, file)
                    # Keep directory structure
                    rel_path = os.path.relpath(src, browser_path)
                    dst = os.path.join("playwright", "driver", "package", ".local-browsers", os.path.dirname(rel_path))
                    playwright_data.append((src, dst))
            break
    
except Exception as e:
    print(f"Warning: Could not collect playwright files: {e}")

# Define data files
added_files = [
    ('ui/main.ui', 'ui'),
    ('ui/Bioimagenes2.png', '.'),  # Put images in root directory
    ('ui/cropped-cropped-iso-bioimagenes2-32x32-1-32x32.png', '.')  # Put images in root directory
]

# Add playwright files
added_files.extend(playwright_data)

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=playwright_bins,
    datas=added_files,
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets', 
        'PyQt6.QtGui',
        'PyQt6.uic',
        'playwright',
        'playwright.sync_api',
        'playwright._impl._driver',
        'playwright._impl._api_types',
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
    upx=False,  # Disable UPX compression for better compatibility
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)