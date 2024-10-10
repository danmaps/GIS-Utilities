# Time to get those credentials, don't be shy!
$TaskCredential = Get-Credential

# Let's find those sneaky scheduled tasks that belong to our user
Get-ScheduledTask |
    Where-Object { $_.Principal.UserId -eq $TaskCredential.UserName } |

    # Now, let's give those tasks a fresh new password!
    Set-ScheduledTask -User $TaskCredential.UserName -Password $TaskCredential.GetNetworkCredential().Password

# Mission accomplished! Your tasks are now ready to roll with the new password.