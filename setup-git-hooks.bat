@echo off
REM Setup script to configure Git to use hooks from .githooks directory (Windows)
REM
REM This script configures Git to use the hooks stored in .githooks/
REM Run this once after cloning the repository or when setting up a new machine.

echo Setting up Git hooks...

REM Check if .githooks directory exists
if not exist ".githooks" (
    echo Error: .githooks directory not found!
    exit /b 1
)

REM Configure Git to use .githooks as hooks path
echo Configuring Git hooks path...
git config core.hooksPath .githooks

echo Git hooks configured successfully!
echo.
echo The pre-push hook will now run tests before allowing pushes.
echo To bypass the hook (not recommended): git push --no-verify

