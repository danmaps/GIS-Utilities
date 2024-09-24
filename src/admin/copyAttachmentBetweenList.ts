async function copyAttachmentBetweenLists(siteUrl, sourceListName, targetListName, commonAttribute) {
    try {
        const digest = await getRequestDigestToken(siteUrl);

        // Step 1: Get the source item based on the common attribute
        const sourceItem = await $.ajax({
            url: `${siteUrl}/_api/web/lists/getbytitle('${sourceListName}')/items?$filter=CommonAttribute eq '${commonAttribute}'`,
            method: "GET",
            headers: { "Accept": "application/json;odata=verbose" }
        });

        const sourceItemId = sourceItem.d.results[0].ID;

        // Step 2: Get the target item based on the common attribute
        const targetItem = await $.ajax({
            url: `${siteUrl}/_api/web/lists/getbytitle('${targetListName}')/items?$filter=CommonAttribute eq '${commonAttribute}'`,
            method: "GET",
            headers: { "Accept": "application/json;odata=verbose" }
        });

        const targetItemId = targetItem.d.results[0].ID;

        // Step 3: Fetch attachment(s) from the source item
        const attachments = await getAttachmentFromSourceItem(siteUrl, sourceListName, sourceItemId);

        // Step 4: Upload attachment(s) to the target item
        for (let attachment of attachments) {
            const fileName = attachment.FileName;
            const fileContent = await $.ajax({
                url: attachment.ServerRelativeUrl,
                method: "GET",
                responseType: "arraybuffer"
            });

            await $.ajax({
                url: `${siteUrl}/_api/web/lists/getbytitle('${targetListName}')/items(${targetItemId})/AttachmentFiles/add(FileName='${fileName}')`,
                method: "POST",
                data: fileContent,
                processData: false,
                binaryStringRequestBody: true,
                headers: {
                    "Accept": "application/json;odata=verbose",
                    "X-RequestDigest": digest // Use the digest token here
                }
            });
        }
    } catch (error) {
        console.log("Error copying attachment between lists:", error);
    }
}
