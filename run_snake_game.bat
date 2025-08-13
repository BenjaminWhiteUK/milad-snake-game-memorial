@echo off
title Snake Game Launcher
color 0A

echo ===================================
echo     ADVANCED SNAKE GAME LAUNCHER
echo ===================================
echo.

:: Check for Python in standard installation locations
set PYTHON_FOUND=0
set PYTHON_PATH=

echo Searching for Python installation...
echo.

:: Check if python is available in PATH
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PYTHON_PATH=python
    set PYTHON_FOUND=1
    echo Python found in PATH
    goto :RUN_GAME
)

:: Check if py launcher is available (preferred method on modern Windows)
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PYTHON_PATH=py
    set PYTHON_FOUND=1
    echo Python launcher found
    goto :RUN_GAME
)

:: Check common installation paths
set PYTHON_LOCATIONS=^
C:\Python39\python.exe^
C:\Python38\python.exe^
C:\Python37\python.exe^
C:\Python310\python.exe^
C:\Python311\python.exe^
C:\Python312\python.exe^
C:\Program Files\Python39\python.exe^
C:\Program Files\Python38\python.exe^
C:\Program Files\Python37\python.exe^
C:\Program Files\Python310\python.exe^
C:\Program Files\Python311\python.exe^
C:\Program Files\Python312\python.exe^
C:\Program Files (x86)\Python39\python.exe^
C:\Program Files (x86)\Python38\python.exe^
C:\Program Files (x86)\Python37\python.exe^
C:\Program Files (x86)\Python310\python.exe^
C:\Program Files (x86)\Python311\python.exe^
C:\Program Files (x86)\Python312\python.exe^
C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe^
C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python38\python.exe^
C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python37\python.exe^
C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe^
C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe^
C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe

for %%p in (%PYTHON_LOCATIONS%) do (
    if exist %%p (
        set PYTHON_PATH="%%p"
        set PYTHON_FOUND=1
        echo Found Python at: %%p
        goto :RUN_GAME
    )
)

:RUN_GAME
if %PYTHON_FOUND% EQU 1 (
    :: Check if pygame is installed
    echo Checking for pygame installation...
    %PYTHON_PATH% -c "import pygame" >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo Pygame is not installed. Attempting to install it now...
        %PYTHON_PATH% -m pip install pygame
        
        :: Check if installation was successful
        %PYTHON_PATH% -c "import pygame" >nul 2>nul
        if %ERRORLEVEL% NEQ 0 (
            echo.
            echo Failed to install pygame. Please run:
            echo pip install pygame
            echo.
            pause
            exit /b 1
        ) else (
            echo Pygame installed successfully!
        )
    ) else (
        echo Pygame is already installed.
    )
    
    echo.
    echo ===================================
    echo     STARTING SNAKE GAME
    echo ===================================
    echo.
    
    :: Run the game
    cd /d "%~dp0"
    %PYTHON_PATH% main.py
    
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo Game exited with an error. Error code: %ERRORLEVEL%
        echo.
        pause
        exit /b %ERRORLEVEL%
    )
) else (
    echo.
    echo ===================================
    echo     PYTHON NOT FOUND
    echo ===================================
    echo.
    echo Python could not be found on your system.
    echo.
    echo Options:
    echo 1. Install Python from python.org
    echo 2. Install from Microsoft Store by typing 'python' in the command prompt
    echo 3. If Python is already installed, add it to your PATH environment variable
    echo.
    echo After installing Python, you'll need to also install pygame:
    echo pip install pygame
    echo.
    pause
    exit /b 1
)

echo.
echo Game closed. Thanks for playing!
echo.
pause
exit /b 0 