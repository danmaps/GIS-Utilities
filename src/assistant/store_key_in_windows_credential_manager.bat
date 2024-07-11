@echo off
setlocal EnableDelayedExpansion

echo This script will store your OpenAI API key in the Windows Credential Manager.
echo Please make sure you have your OpenAI API key ready.
echo.

:PROMPT
set /p "API_KEY=Enter your OpenAI API key: "

if "!API_KEY!"=="" (
    echo API key cannot be empty. Please try again.
    goto PROMPT
)

echo.
echo Storing the OpenAI API key in Windows Credential Manager...

powershell -Command "$secure = ConvertTo-SecureString '%API_KEY%' -AsPlainText -Force; New-StoredCredential -Target 'OpenAI_API_Key' -UserName 'OpenAI' -Password $secure -Persist LocalMachine" > nul 2>&1

if %errorlevel% neq 0 (
    echo An error occurred while storing the credential.
    echo Please ensure you have the necessary permissions and that the CredentialManager PowerShell module is installed.
    echo You can install it by running 'Install-Module -Name CredentialManager' in an elevated PowerShell prompt.
) else (
    echo The OpenAI API key has been successfully stored in the Windows Credential Manager.
)

echo.
pause