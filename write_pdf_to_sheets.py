import camelot
import io
import json
import pandas as pd
import pickle
import pprint
import os.path
import matplotlib
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SPREADSHEET_ID = '1atmXdOFCyVKSFSuQSSdnV72FPfzGAJk_PJjxwAEVjM4'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/spreadsheets']


def process():
    tables = camelot.read_pdf('20200917-155157-01261_09_16_2020_1503_Snell_Valley_Road_Reservior_7_Field_Daily_Report.pdf', pages='2', line_scale=40, shift_text=[''])
    print(len(tables))
    df = tables[0].df
    pd.set_option('display.width', 480)
    pd.set_option('display.max_columns', 14)
    df.rename(columns=df.iloc[0], inplace=True)
    df.drop(df.index[0], inplace=True)
    print(df)
    keys = ['test_number', 'suffix', 'depth_and_elevation', 'location', 'wet_density',
            'dry_density', 'max_dry_density', 'optimum_moisture_content', 'moisture_content',
            'relative_compaction', 'corrected_dry_density', 'corrected_moisture',
            'corrected_relative_compaction', 'pass_fail_retest']
    for row in df.itertuples():
        idx = 0
        for entry in row:
            # skip the first entry which is the index of the df
            if idx == 0:
                idx += 1
                continue
            # skip entry if no value found
            if entry == '':
                idx += 1
                continue
            entry = entry.replace('\n', '')
            print(f"{keys[idx-1]}: {entry}")
            idx += 1




def main():

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    """
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range='A1').execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Found data.')
    """

    drive = build('drive', 'v3', credentials=creds)
    sheets = build('sheets', 'v4', credentials=creds).spreadsheets()
    project_id = '1mMsAhR_fwZu1Vf9b17eKqXzkyNftJemJ'

    # for the demo we are starting in a specific project directory
    page_token = None
    while True:
        query = f"'{project_id}' in parents and mimeType='application/pdf'"
        project_files = drive.files().list(q=query,
                                           fields='nextPageToken, files(id, name)',
                                           pageToken=page_token).execute()
        for file in project_files.get('files', []):
            print(f"Looking at file '{file.get('name')}'")

            if "Field_Daily_Report" in file.get('name'):

                print("Downloading ...")
                # write to spreadsheet
                request = drive.files().get_media(fileId=file.get('id'))
                fh = io.FileIO(file.get('name'), 'wb')
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()

                print("Processing ...")
                tables = camelot.read_pdf(file.get('name'), pages='2', line_scale=40, shift_text=[''])

                if len(tables) == 0:
                    print("No table data found ...\n")
                    continue

                else:
                    print(f"(found {len(tables)} table(s))")
                    df = tables[0].df
                    df.rename(columns=df.iloc[0], inplace=True)
                    df.drop(df.index[0], inplace=True)
                    pd.set_option('display.width', 480)
                    pd.set_option('display.max_columns', 14)
                    #print(df)

                    keys = ['test_number', 'suffix', 'depth_and_elevation', 'location', 'wet_density',
                            'dry_density', 'max_dry_density', 'optimum_moisture_content', 'moisture_content',
                            'relative_compaction', 'corrected_dry_density', 'corrected_moisture',
                            'corrected_relative_compaction', 'pass_fail_retest']
                    # create a dict for our values, default to None
                    vals = {}
                    for key in keys:
                        vals[key] = None

                    print("Values ...")
                    for row in df.itertuples():
                        idx = 0
                        for entry in row:
                            # skip the first entry which is the index of the df
                            if idx == 0:
                                idx += 1
                                continue
                            # skip entry if no value found
                            if entry == '':
                                idx += 1
                                continue
                            entry = entry.replace('\n', '')
                            #print(f"{keys[idx-1]}: {entry}")
                            vals[keys[idx-1]] = entry
                            idx += 1

                        print(f"{vals}")

                        # we can write to the spreadsheet here
                        # but we probably want to do a batch write at the end
                        # which would mean we need to store all the dicts rather
                        # than overwrite
                        """
                        values = [list(vals.values())]
                        body = {
                            'values': values
                        }
                        result = sheets.values().update(
                            spreadsheetId='1atmXdOFCyVKSFSuQSSdnV72FPfzGAJk_PJjxwAEVjM4', range='A2:N2',
                            valueInputOption='RAW', body=body).execute()
                        """

                        rows = [list(vals.values())]
                        sheets.values().append(
                            #spreadsheetId='1atmXdOFCyVKSFSuQSSdnV72FPfzGAJk_PJjxwAEVjM4',
                            # TODO: reformat order of values
                            spreadsheetId='1Is64aJWC8VaIZgQjCIPNoO9alKiJqlNbIa7YLUZCPUw',
                            range="Sheet1!A:N",
                            body={
                                "majorDimension": "ROWS",
                                "values": rows
                            },
                            valueInputOption="USER_ENTERED"
                        ).execute()

                        # clear the vals dict for the next iteration
                        for key in keys:
                            vals[key] = None

                    print()

            else:
                print("Skipping ...\n")

        page_token = project_files.get('nextPageToken', None)
        if page_token is None:
            break


def test():
    d = {'a': 1}
    print(list(d.values()))
    print(type(list(d.values())))

if __name__ == "__main__":
    #test()
    main()
    # process()
