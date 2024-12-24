import requests
import json
import os
from dotenv import load_dotenv
from requests_oauthlib import OAuth2


load_dotenv()

hubspot_endpoint = "https://api.hubapi.com/crm/v3/objects/contacts/batch/upsert"
HUBSPOT_API_KEY = os.getenv('HUBSPOT_API_KEY')

class requestJsonDataToHubspot():
  def __init__(self):
    self.jsonData: json = {}

  def process(self):
    self.getJsonData()
    self.executeBatch()

  def getJsonData(self):
    dataFile = open("data/json_data.json")
    patient_data = dataFile.read()
    self.jsonData = json.loads(patient_data)
  
  def filterData(self):
    if not self.jsonData:
      self.getJsonData()

    filtered_data = []
    unique_emails = set()
    
    for item in self.jsonData:
        properties = item["properties"]
        email = properties.get("email", "").strip()
        # Check if email exists and is not a duplicate
        if email and email not in unique_emails:
            # Validate required fields
            if self.validateDataFields(properties):
                unique_emails.add(email)
                filtered_data.append(item)
    
    self.jsonData = filtered_data
    print(f"Valid unique records: {len(filtered_data)}")
    print("Data validation complete!")

  def validateDataFields(self, properties):
      # Define minimum required fields
      required_fields = {
          "email": properties.get("email", "").strip(),
          "firstname": properties.get("firstname", "").strip(),
          "phone": properties.get("phone", "").strip()
      }
      # Check if at least email is present
      if not required_fields["email"]:
          return False
      # Ensure all properties have at least empty string values
      for key in properties:
          if properties[key] is None:
              properties[key] = ""
      return True
  
  def executeBatch(self):
    header = {
        "content-type": "application/json",
        "Authorization": f"Bearer {HUBSPOT_API_KEY}"
    }
    
    # Take only the first 10 items from jsonData
    limited_data = self.jsonData[:4]
    
    request_body = {
        "inputs": limited_data
    }
    
    response = requests.post(
        url=hubspot_endpoint,
        headers=header,
        json=request_body
    )
    
    print(response.status_code)
    print(response.json())

if __name__ == "__main__":
  request = requestJsonDataToHubspot()
  request.filterData()
  #request.process()