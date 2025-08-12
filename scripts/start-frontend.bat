@echo off
echo Starting Angular Frontend...

echo Checking if we're in the correct directory...
if not exist "angular-frontend" (
    echo Error: angular-frontend directory not found!
    echo Please make sure you're in the project root directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Navigating to Angular frontend directory...
cd angular-frontend

echo Checking Node.js installation...
node --version
if %errorlevel% neq 0 (
    echo Node.js is not installed or not in PATH
    echo Please install Node.js 18+ and try again
    pause
    exit /b 1
)

echo Checking npm installation...
npm --version
if %errorlevel% neq 0 (
    echo npm is not available
    echo Please install Node.js with npm and try again
    pause
    exit /b 1
)

echo Installing Angular CLI globally if not present...
npm list -g @angular/cli >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Angular CLI...
    npm install -g @angular/cli
)

echo Installing project dependencies...
if not exist "node_modules" (
    echo Running npm install...
    npm install
) else (
    echo Dependencies already installed, checking for updates...
    npm install
)

echo.
echo ========================================
echo Angular Frontend Starting
echo ========================================
echo Frontend: http://localhost:4200
echo Backend API: http://localhost:8000
echo ========================================
echo.
echo Starting Angular development server...
echo Press Ctrl+C to stop the server
echo.

ng serve --host 0.0.0.0 --port 4200 --open
