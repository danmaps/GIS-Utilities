# Time to get those credentials, don't be shy!
$TaskCredential = Get-Credential

# Let's find those sneaky scheduled tasks that belong to our user
$tasks = Get-ScheduledTask | Where-Object { $_.Principal.UserId -eq $TaskCredential.UserName }

# Now, let's give those tasks a fresh new password!
$tasks | ForEach-Object {
    Set-ScheduledTask -User $TaskCredential.UserName -Password $TaskCredential.GetNetworkCredential().Password
    Write-Output "Updated task: $($_.TaskName)"
}

# Mission accomplished! Your tasks are now ready to roll with the new password.
# Keeping the window open to admire our handiwork
Write-Output "Press any key to exit..."
$x = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")