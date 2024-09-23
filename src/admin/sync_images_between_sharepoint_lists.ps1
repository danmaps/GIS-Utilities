# Install the PnP.PowerShell module if not already installed
Install-Module -Name PnP.PowerShell

# Import the PnP.PowerShell module
Import-Module PnP.PowerShell

# define a temporary download folder
if (!(Test-Path $downloadPath)) {
    New-Item -Path $downloadPath -ItemType Directory
}

# open the download folder in windows file explorer
Start-Process $downloadPath

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

    # for testing purposes, focus only on ID_8776648 
    # https://edisonintl.sharepoint.com/sites/GeospatialAnalysis-TD/Lists/DamageAssessmentSurvey/DispForm.aspx?ID=50&e=v57upI


    # see if there's a corresponding image in the Images folder that matches the ID
    $OANImage = Get-ChildItem -Path $downloadPath -Filter "ID_$($itemID)*"
    Write-Host "Found $($OANImage.Name)"

    # if there is, add it to the listitem
    if ($OANImage) {
        Write-Host "Adding $($itemID) to the list"
        #remove OAN-$($itemID) from the name
        $shortName = $OANImage.Name -replace "ID_$($itemID)-", "hello_"
        $shortName = "hi"
        Add-PnPListItemAttachment -Content $OANImage -List $listName -Identity $itemID -FileName $shortName
    }

}

# delete the temporary download folder
Remove-Item -Path $downloadPath -Recurse