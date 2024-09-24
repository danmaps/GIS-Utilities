param (
    [Parameter(Mandatory = $false)]
    [string]$LogDirectory = (Get-Location)  # Default to current working directory if not provided
)

# Check if the directory exists; if not, create it
if (-not (Test-Path -Path $LogDirectory)) {
    New-Item -Path $LogDirectory -ItemType Directory
}

# Define the path to your main script
$scriptPath = "sync_images_between_sharepoint_lists.ps1"

# Get the current timestamp for logging purposes
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

# Get the script file name without the extension
$scriptName = [System.IO.Path]::GetFileNameWithoutExtension($scriptPath)

# Define the full log file path (log file will be inside the directory passed as a parameter or default)
$logFile = Join-Path -Path $LogDirectory -ChildPath "$scriptName_$timestamp.txt"

# Execute the main script and redirect all output (stdout and stderr) to the log file
try {
    # Use the call operator (&) to run the script and redirect everything to the log file
    & $scriptPath *>> $logFile

    # Log successful completion
    Write-Host "$scriptName executed successfully. Output logged to $logFile"

} catch {
    # If an error occurs, log it
    $errorMessage = "An error occurred while running the script: $($_.Exception.Message)"
    $errorMessage | Out-File -Append $logFile

    # Show the error in the console as well
    Write-Host $errorMessage
}
