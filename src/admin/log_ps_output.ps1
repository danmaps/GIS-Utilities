# Define the path to your main script
$scriptPath = "sync_images_between_sharepoint_lists.ps1"

# Get the current timestamp for logging purposes
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

# Get the scriptPath file name without the extension
$scriptName = [System.IO.Path]::GetFileNameWithoutExtension($scriptPath)

# Append the timestamp to the log file to keep track of each run separately (optional)
$logFile = "$scriptName_$timestamp.txt"

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
