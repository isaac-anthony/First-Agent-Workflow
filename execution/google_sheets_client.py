#!/usr/bin/env python3
"""
Layer 3: Execution Script
Google Sheets Client
Handles appending lead data, updating contact status, and reading data for maintenance.
"""

import os
import os.path
from datetime import datetime
from typing import Optional, List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]

class GoogleSheetsClient:
    def __init__(self, spreadsheet_id: Optional[str] = None):
        self.spreadsheet_id = spreadsheet_id
        self.creds = self._authenticate()
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)

    def upload_to_drive(self, file_path: str, folder_id: str = None) -> Optional[str]:
        """Uploads a file to Google Drive and returns the webViewLink."""
        try:
            from googleapiclient.http import MediaFileUpload
            
            file_metadata = {'name': os.path.basename(file_path)}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            media = MediaFileUpload(file_path, resumable=True)
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            # Make the file readable by anyone with the link (optional but helpful for the Sheet)
            self.drive_service.permissions().create(
                fileId=file.get('id'),
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
            
            return file.get('webViewLink')
        except Exception as e:
            print(f"Error uploading to Drive: {e}")
            return None

    def _authenticate(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    os.remove('token.json')
                    return self._authenticate()
            else:
                json_file = 'credentials.actual.json' if os.path.exists('credentials.actual.json') else 'credentials.json'
                if not os.path.exists(json_file):
                    raise FileNotFoundError(f"{json_file} not found. Please follow the setup guide to create it.")
                flow = InstalledAppFlow.from_client_secrets_file(
                    json_file, SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def create_new_spreadsheet(self, title: str) -> Optional[str]:
        """Creates a new Google Spreadsheet and returns its ID."""
        try:
            spreadsheet = {'properties': {'title': title}}
            spreadsheet = self.service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
            new_id = spreadsheet.get('spreadsheetId')
            self.spreadsheet_id = new_id
            print(f"Created new spreadsheet with ID: {new_id}")
            return new_id
        except HttpError as err:
            print(f"An error occurred creating spreadsheet: {err}")
            return None

    def create_new_tab(self, tab_name: str) -> bool:
        """Creates a new tab (sheet) in the current spreadsheet."""
        try:
            body = {'requests': [{'addSheet': {'properties': {'title': tab_name}}}]}
            self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body=body).execute()
            print(f"Created new tab: {tab_name}")
            return True
        except HttpError as err:
            if "already exists" in str(err):
                return True
            print(f"An error occurred creating tab: {err}")
            return False

    def get_last_row(self, tab_name: str = "Sheet1") -> int:
        """Returns the index of the last row containing data in the specified tab."""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"'{tab_name}'!A:A"
            ).execute()
            values = result.get('values', [])
            return len(values)
        except Exception:
            return 0

    def get_all_values(self, tab_name: str = "Sheet1") -> List[List[Any]]:
        """Returns all rows from the specified tab."""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"'{tab_name}'!A:Z"
            ).execute()
            return result.get('values', [])
        except Exception as e:
            print(f"Error fetching values from {tab_name}: {e}")
            return []

    def append_leads(self, leads_data: List[List[Any]], tab_name: str = "Sheet1"):
        """Appends lead records to the sheet."""
        try:
            body = {'values': leads_data}
            self.create_new_tab(tab_name)
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"'{tab_name}'!A2",
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            return result
        except HttpError as err:
            print(f"An error occurred appending leads: {err}")
            return None

    def update_cell(self, cell_range: str, value: str, tab_name: str = "Sheet1"):
        """Updates a specific cell or range with a value."""
        try:
            range_name = f"'{tab_name}'!{cell_range}"
            body = {'values': [[value]]}
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            return True
        except Exception as e:
            print(f"Error updating cell {cell_range} in {tab_name}: {e}")
            return False

    def mark_as_contacted(self, row_index: int, tab_name: str = "Sheet1"):
        """Updates the 'Contacted?' and 'Time Contacted' columns (H and I)."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        range_name = f"'{tab_name}'!H{row_index}:I{row_index}"
        body = {'values': [["Yes", now]]}
        try:
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            return True
        except HttpError as err:
            print(f"An error occurred marking contacted: {err}")
            return False

    def get_sheet_names(self) -> List[str]:
        """Returns a list of all tab names in the spreadsheet."""
        try:
            spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            return [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
        except Exception as e:
            print(f"Error fetching sheet names: {e}")
            return []

    def initialize_report_sheet(self):
        """Initializes headers for the Weekly Reports tab."""
        tab_name = "Weekly_Reports"
        headers = [["Week Ending", "Total Leads Scanned", "Total Contacted", "Total Interested", "Pipeline Value ($)", "Avg AI Score", "Executive Summary"]]
        try:
            self.create_new_tab(tab_name)
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"'{tab_name}'!A1",
                valueInputOption="USER_ENTERED",
                body={'values': headers}
            ).execute()
        except HttpError as err:
            print(f"An error occurred initializing report sheet: {err}")

    def initialize_sheet(self, tab_name: str = "Sheet1"):
        """Creates headers if the sheet is empty."""
        headers = [["Business Name", "Lead Name", "Email", "Phone", "Website", "Address", "Date Added", "Contacted?", "Time Contacted", "Status", "Follow-up Count", "AI Lead Score", "AI Score Reason", "Personalized Hook"]]
        try:
            self.create_new_tab(tab_name)
            # Check if headers already exist
            existing = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"'{tab_name}'!A1:A1"
            ).execute()
            
            if not existing.get('values'):
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"'{tab_name}'!A1",
                    valueInputOption="USER_ENTERED",
                    body={'values': headers}
                ).execute()
        except HttpError as err:
            print(f"An error occurred initializing sheet: {err}")
