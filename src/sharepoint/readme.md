# SyncAttachments.ps1

`SyncAttachments.ps1` is a PowerShell script that synchronizes image attachments between two SharePoint lists. The script connects to both a source and a destination SharePoint site, retrieves items modified within a specified time window (or all items if no time window is provided), downloads their attachments, and uploads them to the destination list based on a matching `TrackingID`.

## Prerequisites

### PowerShell Version

This script requires **PowerShell 7** (also known as PowerShell Core) or later. You can download and install PowerShell 7 from the [official documentation](https://aka.ms/powershell).

To verify that you have the correct version installed, run:

```powershell
$PSVersionTable.PSVersion
```

Ensure that your PowerShell version is 7.0 or greater.

### Required Modules

- **PnP.PowerShell**: This script uses the `PnP.PowerShell` module to interact with SharePoint Online. If you don't have this module installed, `SyncAttachments.ps1` will attempt to install it for you. You can install it with the following command:

```powershell
Install-Module -Name PnP.PowerShell -Force
```

If you already have the module installed, ensure it is updated to the latest version:

```powershell
Update-Module -Name PnP.PowerShell
```

### SharePoint Permissions

You must have the **correct permissions** on both the source and destination SharePoint lists:
- **Read/Download** permissions on the **source** list to fetch the list items and attachments.
- **Contribute/Upload** permissions on the **destination** list to upload the attachments.

Ensure your SharePoint credentials or service accounts have the appropriate access before running the script.

## How to Use

### Syntax

```powershell
.\SyncAttachments.ps1 -SourceSiteUrl <Source SharePoint URL> -SourceListName <Source List Name> `
    -DestinationSiteUrl <Destination SharePoint URL> -DestinationListName <Destination List Name> `
    [-ModifiedWithinLastHours <Number of Hours>] [-DownloadPath <Path>] [-SkipCleanUp] [-UseWebLogin]
```

### Parameters

- **SourceSiteUrl** (Mandatory): The URL of the **source** SharePoint site.
- **SourceListName** (Mandatory): The name or ID of the **source** SharePoint list.
- **DestinationSiteUrl** (Mandatory): The URL of the **destination** SharePoint site.
- **DestinationListName** (Mandatory): The name or ID of the **destination** SharePoint list.
- **ModifiedWithinLastHours** (Optional): Specifies the time window in hours for filtering modified items. If not supplied, the script will fetch **all** list items.
- **DownloadPath** (Optional): The local path to the folder where attachments will be downloaded. Default is `$env:TEMP\sharepoint_attachments`.
- **SkipCleanUp** (Optional, Switch): If supplied, the script will not clean up (delete) the downloaded files after execution. Disabled by default.
- **UseWebLogin** (Optional, Switch): If supplied, the script will use a web-based login for authentication. Disabled by default.

### Example

1. **Sync attachments modified within the last 2 hours** from the source list to the destination list:

    ```powershell
    .\SyncAttachments.ps1 -SourceSiteUrl "https://company.sharepoint.com/sites/sourceSite" `
    -SourceListName "SourceList" -DestinationSiteUrl "https://company.sharepoint.com/sites/destinationSite" `
    -DestinationListName "DestinationList" -ModifiedWithinLastHours 2
    ```

2. **Sync all attachments** (no time filter) from the source list to the destination list:

    ```powershell
    .\SyncAttachments.ps1 -SourceSiteUrl "https://company.sharepoint.com/sites/sourceSite" `
    -SourceListName "SourceList" -DestinationSiteUrl "https://company.sharepoint.com/sites/destinationSite" `
    -DestinationListName "DestinationList"
    ```

3. **Specify a custom download path** and disable automatic clean-up:

    ```powershell
    .\SyncAttachments.ps1 -SourceSiteUrl "https://company.sharepoint.com/sites/sourceSite" `
    -SourceListName "SourceList" -DestinationSiteUrl "https://company.sharepoint.com/sites/destinationSite" `
    -DestinationListName "DestinationList" -DownloadPath "C:\CustomFolder\Downloads" -SkipCleanUp:$True
    ```

### Authentication

The script uses **web login** by default, which prompts you to authenticate using your SharePoint credentials. If you want to use other authentication methods, you can modify the `Connect-ToSharePoint` function within the script as needed.

## Logging and Output

- The script provides verbose output in the console for each attachment it uploads or fails to upload.
- It also shows the number of items processed and the total number of attachments uploaded to the destination list.
- Run the script through `log_ps_output.ps1` to capture the output of the script in a log file.

## Troubleshooting

- **Permissions Issues**: Ensure your SharePoint account has the necessary permissions on both the source and destination lists.
- **Module Installation Errors**: If the `PnP.PowerShell` module fails to install, ensure you are running PowerShell as an Administrator and that you are connected to the internet.
- **Authentication**: If you are using **Multi-Factor Authentication (MFA)** or a **Single Sign-On (SSO)** solution, ensure you are using the `-UseWebLogin` parameter to trigger the correct authentication flow.

## License

This script is provided "as is" without warranty of any kind. You are free to modify and distribute it for your use.
