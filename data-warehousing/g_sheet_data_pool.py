import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

samples: int = 10000
# Replace the global variables with environment variables
SCOPES = [os.getenv('GOOGLE_SHEETS_SCOPES')]  # Note: Wrapped in list since SCOPES expects a list
SAMPLE_SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_ID')
SAMPLE_RANGE_NAME = "A1:O"+ str(samples) # originally "A1:06"

class GoogleSheetDataPooledToJson:
  def __init__(self):
    self.processed_samples = 0 # rows in g-sheets that have passed through filter
    self.creds = None
    self.row_dict = None
    
  def executeProcess(self) -> None:
    self.verifyCredentials()
    self.execute()

  def verifyCredentials(self) -> None:
    if os.path.exists("token.json"):
      self.creds = Credentials.from_authorized_user_file("auth/token.json", SCOPES)

    if not self.creds or not self.creds.valid:
      if self.creds and self.creds.expired and self.refresh_token:
        self.creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
          "auth/credentials.json", SCOPES
        )
        self.creds = flow.run_local_server(port=3000)
      
      with open("auth/token.json", "w") as token:
        token.write(self.creds.to_json())
  
  def format_data(self, row_data) -> json:
    return {
        "properties": {
            "contact_origin": "Biolite Aesthetic Clinic", # originally Branch changed to origin for simplifying
            "file_no": row_data.get("File No", ""),
            "firstname": row_data.get("Patient Name", ""),
            "email": row_data.get("Email", ""),
            "phone": row_data.get("Mobile", ""), # originally phone_number changed to phone because of weird tags
            "nationality": row_data.get("nationality", ""),
            "gender": row_data.get("Gender", ""),
            "date_of_birth": row_data.get("DOB", ""),
            "message": row_data.get("treatment Name", ""), # originallty treatment_name
            "patient_age_years": self.calculateDynamicAge(row_data.get("DOB", "")), # originally row_data.get("pat_age_years", "") but changed to get dynamic dob
            "date_registered": row_data.get("Date registered", ""),
            "hs_lead_status": "NEW",
            "origin": "Biolite Website",
            "contact_origin": "Biolite Website"
        },
        "id": row_data.get("Email", ""),
        "idProperty": "email"
    }
  
  def calculateDynamicAge(self, patient_dob: str) -> str:
    try:
        date_format = "%d/%m/%Y"
        dob = datetime.strptime(patient_dob, date_format)
        today = datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        # Add logging only when age differs significantly
        if abs(int(age) - int(self.row_dict.get("pat_age_years", "0"))) > 1:
            print(f"Large age difference detected - Dynamic: {age}, Sheet: {self.row_dict.get('pat_age_years', '')}")
        return str(age)
    except Exception as e:
        return self.row_dict.get("pat_age_years", "")

  def execute(self) -> None:
    try:
        service = build("sheets", "v4", credentials=self.creds)
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        # low level array size assignment for optimization
        data_rows = []
        data_rows.extend([None] * samples)

        values = result.get("values", [])
        if not values:
            print("No data found.")
            return
        
        headers = values[0]
        # Create index mapping for faster lookups
        header_index = {header: idx for idx, header in enumerate(headers)}
        email_idx = header_index["Email"]
        # Use set for faster duplicate checking
        unique_email_ids = set()
        data_rows = []
        # Batch process with optimized loops
        for row in values[1:]:
            email = row[email_idx]
            if email and email not in unique_email_ids:
                self.processed_samples+=1
                unique_email_ids.add(email)
                # Create row dict using dictionary comprehension
                row_dict = {headers[i]: value for i, value in enumerate(row)}
                self.row_dict = row_dict
                formatted_data = self.format_data(row_dict)
                data_rows.append(formatted_data)
        # aggregate data and store in file
        json_data = json.dumps(data_rows, indent=2)
        with open('data/json_data.json', 'w') as f:
            f.write(json_data)
        print("Processed samples, (with filter): ", str(self.processed_samples))

    except HttpError as err:
        print(err)

      
if __name__ == "__main__":
  gSheetData = GoogleSheetDataPooledToJson()
  gSheetData.executeProcess()