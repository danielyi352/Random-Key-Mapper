@echo off
echo ========================================
echo Key Remapper - Setup and Run
echo ========================================
echo.

REM Check if executable already exists
if exist "dist\KeyRemapper.exe" (
    echo Executable found! Running...
    echo.
    start "" "dist\KeyRemapper.exe"
    exit /b
)

REM Executable doesn't exist, need to build it
echo Executable not found. Building it now...
echo This will take 1-2 minutes on first run...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Install PyInstaller if needed
echo Installing/updating PyInstaller...
pip install --quiet --upgrade pyinstaller

REM Install other dependencies if needed
echo Installing dependencies...
pip install --quiet -r requirements.txt

REM Build the executable
echo.
echo Building executable (this may take a minute)...
pyinstaller --onefile --windowed --name "KeyRemapper" --icon=NONE key_remapper.py

REM Check if build was successful
if exist "dist\KeyRemapper.exe" (
    echo.
    echo ========================================
    echo Build successful!
    echo ========================================
    echo.
    echo Running the application...
    echo.
    start "" "dist\KeyRemapper.exe"
) else (
    echo.
    echo ========================================
    echo ERROR: Build failed!
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo Make sure Python and all dependencies are installed.
    echo.
    pause
    exit /b 1
)

