from google.cloud import storage
import tempfile as tempfile
import numpy as np
import pandas as pd
import requests
import os


async def data_process(event, context):
    """Background Cloud Function to be triggered by Cloud Storage.
       This generic function logs relevant data when a file is changed.

    Args:
        event (dict):  The dictionary with data specific to this type of event.
                       The `data` field contains a description of the event in
                       the Cloud Storage `object` format described here:
                       https://cloud.google.com/storage/docs/json_api/v1/objects#resource
        context (google.cloud.functions.Context): Metadata of triggering event.
    Returns:
        None; the output is written to Stackdriver Logging
    """
    if event['name'] == "newDataFile":
        tempFilePath = tempfile.mkdtemp()
        storage_client = storage.Client()

        bucket = storage_client.bucket("digital-equity.appspot.com")
        blobNew = bucket.blob("newDataFile")
        blobNew.download_to_filename(tempFilePath+"/newDataFile.json")
        blobOld = bucket.blob("totalDataFile")
        blobOld.download_to_filename(tempFilePath+"/totalDataFile.json")

        # cleaning up the data
        data_array = [pd.read_json(
            tempFilePath+"/newDataFile.json"), pd.read_json(tempFilePath+"/totalDataFile.json")]
        if 'School Name' in data_array[0].columns:
            print('data not found')
            data_array[0] = data_array[0].applymap(
                lambda x: np.nan if not x else x)
            school_names = [d["School Name"] for d in data_array]
            allschoolnames = pd.concat(
                school_names).drop_duplicates().reset_index(drop=True)
            currentYear = pd.merge(
                data_array[0], allschoolnames, on='School Name', how="outer")
            data_array[0] = currentYear
            currentTempYear = int(currentYear['SY'][0])
            all_merged = pd.concat(data_array)
            all_merged.to_json(
                tempFilePath+"/totalDataFile2.json", orient='records')
            tempYear = int(all_merged.at[len(data_array[1])-1, 'SY'])
            renameYear = max(currentTempYear, tempYear)
            # renaming the old
            bucket.rename_blob(
                blobOld, "totalDataFile"+str(renameYear))

            # uploading new file
            updatedTotal = bucket.blob("totalDataFile")
            updatedTotal.upload_from_filename(
                tempFilePath+"/totalDataFile2.json")

            # redeployment
            url = "https://api.github.com/repos/mbae-org/spark-digital-equity/actions/workflows/build.yml/dispatches"

            payload = "{\n    \"inputs\": {\n        \"downloadURL\": \"https://storage.googleapis.com/digital-equity.appspot.com/totalDataFile \"\n    },\n    \"ref\": \"master\"\n}"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/vnd.github.v3+json',
                'Authorization': 'Bearer ' + os.environ.get('access_token')}

            response = requests.request(
                "POST", url, headers=headers, data=payload)
            print(response)

    else:
        print("did not update")
