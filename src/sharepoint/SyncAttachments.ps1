<#
.SYNOPSIS
This script synchronizes attachments from a source SharePoint list to a destination SharePoint list based on modified items within a specified time window.

.PARAMETER SourceSiteUrl
The URL of the source SharePoint site.

.PARAMETER SourceListName
The name or ID of the source SharePoint list.

.PARAMETER DestinationSiteUrl
The URL of the destination SharePoint site.

.PARAMETER DestinationListName
The name or ID of the destination SharePoint list.

.PARAMETER ModifiedWithinLastHours
(Optional) The time window in hours to filter modified items. If not supplied, all items will be fetched.

.PARAMETER DownloadPath
(Optional) The path to the folder where attachments will be downloaded. Default is "$env:TEMP\sharepoint_attachments".

.PARAMETER CleanUp
(Optional) Switch to indicate if the download folder should be deleted after execution. Default is $False.

.PARAMETER UseWebLogin
(Optional) Switch to use web login for authentication. Default is $False.

.EXAMPLE
.\Sync-Attachments.ps1 -SourceSiteUrl "https://source.sharepoint.com" -SourceListName "SourceList" -DestinationSiteUrl "https://destination.sharepoint.com" -DestinationListName "DestinationList"

#>

param(
    [Parameter(Mandatory = $true)]
    [string]$SourceSiteUrl,

    [Parameter(Mandatory = $true)]
    [string]$SourceListName,

    [Parameter(Mandatory = $true)]
    [string]$DestinationSiteUrl,

    [Parameter(Mandatory = $true)]
    [string]$DestinationListName,

    [int]$ModifiedWithinLastHours,

    [string]$DownloadPath = "$env:TEMP\sharepoint_attachments",

    [switch]$SkipCleanUp = $False,

    [switch]$UseWebLogin = $False
)

# Ensure PnP.PowerShell module is installed and imported
if (-not (Get-Module -ListAvailable -Name PnP.PowerShell)) {
    Install-Module -Name PnP.PowerShell -Force
}
Import-Module PnP.PowerShell

# Prepare the download folder
if (Test-Path $DownloadPath) {
    Remove-Item -Path $DownloadPath -Recurse -Force
}
New-Item -Path $DownloadPath -ItemType Directory | Out-Null

function Connect-ToSharePoint {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SiteUrl,
        [switch]$UseWebLogin = $false
    )
    if ($UseWebLogin) {
        Connect-PnPOnline -Url $SiteUrl -UseWebLogin
    } else {
        Connect-PnPOnline -Url $SiteUrl
    }
}

function Get-ModifiedListItems {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ListName,
        [int]$ModifiedWithinLastHours
    )
    $listItems = Get-PnPListItem -List $ListName -Fields "Modified", "ID"
    if ($ModifiedWithinLastHours) {
        $filteredItems = $listItems | Where-Object { $_["Modified"] -gt (Get-Date).AddHours(-$ModifiedWithinLastHours) }
        return $filteredItems
    } else {
        return $listItems
    }
}

function Get-AndRenameAttachments {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ListName,
        [Parameter(Mandatory = $true)]
        [array]$ListItems,
        [Parameter(Mandatory = $true)]
        [string]$DownloadPath
    )
    foreach ($item in $ListItems) {
        $itemID = $item["ID"]
        # Get attachments
        $attachments = Get-PnPProperty -ClientObject $item -Property AttachmentFiles
        foreach ($attachment in $attachments.AttachmentFiles) {
            $attachmentUrl = $attachment.ServerRelativeUrl
            $fileName = $attachment.FileName
            $newFileName = "ID_$itemID-$fileName"
            # Download and rename
            Get-PnPFile -Url $attachmentUrl -Path $DownloadPath -FileName $newFileName -AsFile
        }
    }
}

function Add-Attachments {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ListName,
        [Parameter(Mandatory = $true)]
        [string]$DownloadPath,
        [Parameter(Mandatory = $true)]
        [hashtable]$DestinationItemsHash
    )
    $count = 0
    $downloadedFiles = Get-ChildItem -Path $DownloadPath
    foreach ($image in $downloadedFiles) {
        if ($image.Name -match "^ID_(.+?)-") {
            $trackingID = $Matches[1]
            if ($DestinationItemsHash.ContainsKey($trackingID)) {
                $itemID = $DestinationItemsHash[$trackingID]
                $shortName = $image.Name -replace "^ID_$([regex]::Escape($trackingID))-", ""
                try {
                    Add-PnPListItemAttachment -Path $image.FullName -List $ListName -Identity $itemID -NewFileName $shortName
                    Write-Host "Successfully added attachment $shortName to item $itemID (TrackingID: $trackingID)"
                    $count++
                }
                catch {
                    Write-Host "Failed to add attachment to item $itemID (TrackingID: $trackingID). Error: $_"
                }
            } else {
                Write-Host "No matching destination item found for TrackingID $trackingID"
            }
        } else {
            Write-Host "Filename does not match expected pattern: $($image.Name)"
        }
    }
    Write-Host "Total attachments uploaded: $count"
}

# Main Script Execution

# Connect to the source SharePoint site
Connect-ToSharePoint -SiteUrl $SourceSiteUrl -UseWebLogin:$UseWebLogin

# Get modified items from the source list
$modifiedItems = Get-ModifiedListItems -ListName $SourceListName -ModifiedWithinLastHours $ModifiedWithinLastHours

if ($ModifiedWithinLastHours) {
    Write-Host "Found $($modifiedItems.Count) items modified in the last $ModifiedWithinLastHours hour(s)."
} else {
    Write-Host "Found $($modifiedItems.Count) items in the source list."
}

# Download and rename attachments
Get-AndRenameAttachments -ListName $SourceListName -ListItems $modifiedItems -DownloadPath $DownloadPath

# Connect to the destination SharePoint site
Connect-ToSharePoint -SiteUrl $DestinationSiteUrl -UseWebLogin:$UseWebLogin

# Get destination list items with TrackingID
$destinationItems = Get-PnPListItem -List $DestinationListName -Fields "ID", "TrackingID"

# Build a hashtable mapping TrackingID to ItemID
$destinationItemsHash = @{}
foreach ($item in $destinationItems) {
    $itemID = $item["ID"]
    $trackingID = $item["TrackingID"]
    if ($trackingID) {
        $destinationItemsHash[$trackingID] = $itemID
    }
}

# Upload attachments to the destination list
Add-Attachments -ListName $DestinationListName -DownloadPath $DownloadPath -DestinationItemsHash $destinationItemsHash

# Clean up the download folder if skip cleanup is not specified
if (!$SkipCleanUp) {
    Remove-Item -Path $DownloadPath -Recurse -Force
}
