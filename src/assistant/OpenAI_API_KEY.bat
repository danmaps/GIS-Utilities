@echo off
setlocal enabledelayedexpansion

echo This script will set up your OpenAI API key as a persistent environment variable.
echo Please make sure you have your OpenAI API key ready.
echo.

:PROMPT
set /p API_KEY="Enter your OpenAI API key: "

if "!API_KEY!"=="" (
    echo API key cannot be empty. Please try again.
    goto PROMPT
)

echo.
echo Setting the OPENAI_API_KEY environment variable...

setx OPENAI_API_KEY "!API_KEY!"

if %errorlevel% neq 0 (
    echo An error occurred while setting the environment variable.
    echo Please try running this script as an administrator.
) else (
    echo Environment variable OPENAI_API_KEY has been set successfully.
    echo You may need to restart your command prompt or applications for the change to take effect.
)

echo.
pause