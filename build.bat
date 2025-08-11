@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    PAMI AUTOMATION EXE BUILDER
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found
echo.

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install requirements
    pause
    exit /b 1
)

:: Install Playwright browsers
echo Installing Playwright browsers (this may take a while)...
playwright install chromium
if %errorlevel% neq 0 (
    echo  Warning: Failed to install Playwright browsers
    echo    The application will attempt to download browsers on first run
)

:: Clean previous builds
echo Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

:: Check if required files exist
echo Checking required files...
set "missing_files="

if not exist "app.py" (
    set "missing_files=!missing_files! app.py"
)
if not exist "ui\main.ui" (
    set "missing_files=!missing_files! ui\main.ui"
)
if not exist "browser_automation.py" (
    set "missing_files=!missing_files! browser_automation.py"
)
if not exist "logger.py" (
    set "missing_files=!missing_files! logger.py"
)
if not exist "settings_manager.py" (
    set "missing_files=!missing_files! settings_manager.py"
)
if not exist "config.py" (
    set "missing_files=!missing_files! config.py"
)

if not "!missing_files!"=="" (
    echo Missing required files: !missing_files!
    pause
    exit /b 1
)

echo All required files found

:: Build executable
echo Building executable with PyInstaller...
pyinstaller pami_automation.spec
if %errorlevel% neq 0 (
    echo BUILD FAILED!
    echo Check the console output above for errors.
    echo.
    echo Common solutions:
    echo - Make sure all Python files are in the correct location
    echo - Check that the ui\main.ui file exists
    echo - Verify all imports in your Python files are correct
    pause
    exit /b 1
)

:: Check if executable was created
if exist "dist\PamiAutomation.exe" (
    echo.
    echo BUILD SUCCESSFUL!
    echo Executable created: dist\PamiAutomation.exe
    
    :: Get file size
    for %%A in (dist\PamiAutomation.exe) do (
        set "filesize=%%~zA"
        set /a "filesizeMB=!filesize!/1024/1024"
        echo File size: !filesizeMB! MB
    )
    
) else (
    echo BUILD FAILED!
    echo Executable was not created. Check the console output above for errors.
    pause
    exit /b 1
)

echo.
echo Build process completed!
pause