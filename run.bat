@echo off
setlocal

cd /d "%~dp0"

set "ROOT_DIR=%CD%"
set "BACKEND_DIR=%ROOT_DIR%\backend"
set "FRONTEND_DIR=%ROOT_DIR%\frontend"
set "VENV_PYTHON=%BACKEND_DIR%\.venv\Scripts\python.exe"
set "APP_URL=http://127.0.0.1:5173"

if /I "%~1"=="--help" goto :help

echo.
echo VisaSponsor Jobs Launcher
echo =========================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed or not on PATH.
    goto :fail
)

where npm >nul 2>nul
if errorlevel 1 (
    echo npm is not installed or not on PATH.
    goto :fail
)

if not exist "%VENV_PYTHON%" (
    echo Creating backend virtual environment...
    python -m venv "%BACKEND_DIR%\.venv"
    if errorlevel 1 goto :fail
)

echo Installing backend dependencies...
"%VENV_PYTHON%" -m pip install -r "%BACKEND_DIR%\requirements.txt"
if errorlevel 1 goto :fail

if not exist "%FRONTEND_DIR%\node_modules" (
    echo Installing frontend dependencies...
    pushd "%FRONTEND_DIR%"
    call npm install
    if errorlevel 1 (
        popd
        goto :fail
    )
    popd
)

echo Starting backend server...
start "AI Job Search Backend" cmd /k ""%ROOT_DIR%\start-backend.bat""

echo Starting frontend server...
start "AI Job Search Frontend" cmd /k ""%ROOT_DIR%\start-frontend.bat""

if /I "%~1"=="--no-browser" goto :success

echo Waiting for the backend and frontend to become available...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ErrorActionPreference = 'SilentlyContinue';" ^
    "$frontendReady = $false;" ^
    "$backendReady = $false;" ^
    "for ($i = 0; $i -lt 90; $i++) {" ^
    "  if (-not $backendReady) {" ^
    "    try {" ^
    "      $backend = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/api/health';" ^
    "      if ($backend.StatusCode -eq 200) { $backendReady = $true }" ^
    "    } catch {}" ^
    "  }" ^
    "  if (-not $frontendReady) {" ^
    "  try {" ^
    "    $response = Invoke-WebRequest -UseBasicParsing '%APP_URL%';" ^
    "    if ($response.StatusCode -ge 200) { $frontendReady = $true }" ^
    "  } catch {}" ^
    "  }" ^
    "  if ($backendReady -and $frontendReady) { Start-Process '%APP_URL%'; exit 0 }" ^
    "  Start-Sleep -Seconds 1" ^
    "}" ^
    "Start-Process '%APP_URL%'"

:success
echo.
echo The app is starting.
echo Frontend: %APP_URL%
echo Backend:  http://127.0.0.1:8000
echo.
echo Leave the two server windows open while using the app.
echo Run ".\run.bat --no-browser" if you do not want it to open a browser tab.
goto :end

:help
echo.
echo Usage:
echo   .\run.bat
echo   .\run.bat --no-browser
echo.
echo This script creates the backend virtual environment if needed,
echo installs dependencies, starts both servers, and opens the app.
goto :end

:fail
echo.
echo Startup failed. Fix the error above and run .\run.bat again.
exit /b 1

:end
endlocal
