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
$listItems = Get-PnPListItem -List $listName -Fields "Title"

# Loop through each item to get the attachments
foreach ($item in $listItems) {
    $itemID = $item["ID"]

    # Get and download the attachments for the list item
    Get-PnPListItemAttachment -List $listName -Identity $itemID -Path $downloadPath

    # Rename the attachments by prepending the ID_Number
    # get the attachments that don't start with ID_
    $attachments = Get-ChildItem -Path $downloadPath | Where-Object { $_.Name -notmatch "^ID_" }
    foreach ($attachment in $attachments) {
        $newFileName = "ID_$itemID-$($attachment.Name)"
        Rename-Item -Path $attachment.FullName -NewName $newFileName

        Write-Host "Renamed $($attachment.Name) to $newFileName"
    }
}
# for each image in the Images directory, copy it to the sharepoint list defined in toList

# Define the destination SharePoint site URL and list name
# $siteUrl = "https://edisonintl.sharepoint.com/sites/TD/org"
# $listName = "Damage Assessment Survey Questions"

# for proof of concept, just copy the images to the rows of the origin list

# Get the list items
$listItems = Get-PnPListItem -List $listName
# Loop through each item to add the correct attachment by ID_Number
foreach ($item in $listItems) {
    $itemID = $item["ID"]

    # https://edisonintl.sharepoint.com/sites/GeospatialAnalysis-TD/Lists/DamageAssessmentSurvey/DispForm.aspx?ID=50&e=v57upI

    # see if there's a corresponding image in the Images folder that matches the ID
    $OANImages = Get-ChildItem -Path $downloadPath | Where-Object { $_.Name -like "ID_$itemID*" }
    Write-Host "Found $($OANImage.Name)"

    # Try to add any matching images to the corresponding list item


    foreach ($OANImage in $OANImages) {
        
        Write-Host "Attempting to add $($itemID) to the list"
        
        # Remove the ID_ prefix from the image name
        $shortName = $OANImage.Name -replace "ID_$($itemID)-", ""

        # Further shorten the name to only the last 10 characters (excluding the extension)
        $extension = $OANImage.Extension  # Extract the extension
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($shortName)  # Get the base name without extension

        # If the base name is longer than 10 characters, slice it to the last 10
        if ($baseName.Length -gt 10) {
            $baseName = $baseName.Substring($baseName.Length - 10)
        }

        # Recombine the shortened base name with the extension
        $shortName = "$baseName$extension"

        try {
            
            # Attempt to add the attachment
            Add-PnPListItemAttachment -Path $OANImage.FullName -List $listName -Identity $itemID -FileName $shortName
            Write-Host "Successfully added attachment $shortName for item $itemID"
        }
        catch {
            # Handle the error
            Write-Host "Failed to add attachment for item $itemID. Error: $_"
        }
    }
}

# delete the temporary download folder
Remove-Item -Path $downloadPath -Recurse

# only sync attachments for changed list items
#   if this process is meant to be run hourly, just look at what has been updated in the last hour

