# Install the PnP.PowerShell module if not already installed
Install-Module -Name PnP.PowerShell

# Import the PnP.PowerShell module
Import-Module PnP.PowerShell

# create a temporary download folder in the user's temp folder
$downloadPath = Join-Path -Path $env:TEMP -ChildPath "download"

# create the download folder if it doesn't exist
if (!(Test-Path $downloadPath)) {
    New-Item -Path $downloadPath -ItemType Directory
}

# open the download folder in windows file explorer
# Start-Process $downloadPath

# Define the origin SharePoint site URL and list name
$siteUrl = "https://edisonintl.sharepoint.com/sites/GeospatialAnalysis-TD/"
$listName = "8e4e8acd-07fc-4e95-9573-b07fa8312d56" # DamageAssessmentSurvey

# Connect to SharePoint Online using current Windows credentials
Connect-PnPOnline -Url $siteUrl -UseWebLogin

# Get the list items
$listItems = Get-PnPListItem -List $listName -Fields "Modified"

# narrow it down to only items that have been modified within the last hour
# use the value in the Modified field

$listItemsModifiedWithinLastHour = $listItems | Where-Object { $_["Modified"] -gt (Get-Date).AddHours(-1) }
# $listItemsModifiedWithinLastHour = $listItems | Where-Object { $_.LastModified -gt (Get-Date).AddHours(-1) }

# Loop through each item to get the attachments
foreach ($item in $listItemsModifiedWithinLastHour) {
    $itemID = $item["ID"]

    # Get and download the attachments for the list item
    Get-PnPListItemAttachment -List $listName -Identity $itemID -Path $downloadPath

    # Rename the attachments by prepending the ID_Number
    # get the attachments that don't start with ID_
    $attachments = Get-ChildItem -Path $downloadPath | Where-Object { $_.Name -notmatch "^ID_" }
    foreach ($attachment in $attachments) {
        $newFileName = "ID_$itemID-$($attachment.Name)"
        Rename-Item -Path $attachment.FullName -NewName $newFileName

        # Write-Host "Renamed $($attachment.Name) to $newFileName"
    }
}

# stop here for debugging
# exit


# for each image in the Images directory, copy it to the sharepoint list defined in toList

# Define the destination SharePoint site URL and list name
 $siteUrl = "https://edisonintl.sharepoint.com/sites/TD/org"
 $listName = "Damage Assessment Survey Questions"

 # Connect to SharePoint Online using current Windows credentials
Connect-PnPOnline -Url $siteUrl -UseWebLogin

# Get the list items
$listItems = Get-PnPListItem -List $listName -Fields "TrackingID ID"

# Get the list items
$listItems = Get-PnPListItem -List $listName
# Loop through each item to add the correct attachment by ID_Number

foreach ($item in $listItems) {
    $itemID = $item["ID"]
    $trackingID = $item["TrackingID"]

    # Find the matching images in the download folder using the TrackingID
    $matchingImages = Get-ChildItem -Path $downloadPath | Where-Object { $_.Name -like "ID_$trackingID*" }
    
    if ($matchingImages.Count -eq 0) {
        Write-Host "No matching images found for TrackingID $trackingID"
    } else {
        foreach ($image in $matchingImages) {
            # Write-Host "Found matching image: $($image.Name) for TrackingID $trackingID"

            # Prepare the short name for uploading (if you need to modify the name)
            $shortName = $image.Name -replace "ID_$($trackingID)-", ""


            # Further shorten the name to only the last 10 characters (excluding the extension)
            $extension = $image.Extension  # Extract the extension
            $baseName = [System.IO.Path]::GetFileNameWithoutExtension($shortName)  # Get the base name without extension

            # If the base name is longer than 10 characters, slice it to the last 10
            # if ($baseName.Length -gt 10) {
            #     $baseName = $baseName.Substring($baseName.Length - 10)
            # }

            # Recombine the shortened base name with the extension
            $shortName = "$baseName$extension"

            try {
                # Use the itemID for uploading the attachment
                Add-PnPListItemAttachment -Path $image.FullName -List $listName -Identity $itemID -NewFileName $shortName
                Write-Host "Successfully added attachment $shortName for item $itemID (TrackingID: $trackingID)"
            }
            catch {
                Write-Host "Failed to add attachment for item $itemID (TrackingID: $trackingID). Error: $_"
            }
        }
    }
}

# delete the temporary download folder
Remove-Item -Path $downloadPath -Recurse

# only sync attachments for changed list items
#   if this process is meant to be run hourly, just look at what has been updated in the last hour

Write-Host "Done"