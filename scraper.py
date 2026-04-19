import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import time
import os

# 1. Setup Google Sheets Connection
def get_sheet():
    print("DEBUG: starting Google Sheets authentication...")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    if not os.path.exists("credentials.json"):
        print("ERROR: credentials.json not found in current directory!")
    
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    
    print("DEBUG: looking for spreadsheet 'Job Board Data'...")
    spreadsheet = client.open("Job Board Data")
    
    try:
        ws = spreadsheet.worksheet("Jobs")
        print("DEBUG: successfully connected to 'Jobs' worksheet.")
        return ws
    except gspread.exceptions.WorksheetNotFound:
        print("WARNING: 'Jobs' worksheet not found. Falling back to first tab.")
        return spreadsheet.get_worksheet(0)

def fetch_greenhouse_jobs(board_token, company_name):
    print(f"\n--- DEBUG: Fetching {company_name} (Token: {board_token}) ---")
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    try:
        response = requests.get(url, timeout=15)
        print(f"DEBUG: API Status Code: {response.status_code}")
        data = response.json()
        
        all_jobs = data.get('jobs', [])
        print(f"DEBUG: Found {len(all_jobs)} total open roles at {company_name}")
        
        new_jobs = []
        keywords = ["AI", "Privacy", "Ethics", "Policy", "Trust", "Safety", "ESG", "Compliance"]
        
        for job in all_jobs:
            title = job.get('title')
            if any(word.lower() in title.lower() for word in keywords):
                new_jobs.append([
                    str(job.get('id')), 
                    title, 
                    company_name, 
                    "AI/Policy", 
                    job.get('location', {}).get('name'), 
                    job.get('absolute_url'),
                    f"Trust Tech role at {company_name}", 
                    "" 
                ])
        
        print(f"DEBUG: Filtered down to {len(new_jobs)} relevant 'Trust Tech' roles.")
        return new_jobs
    except Exception as e:
        print(f"ERROR: Exception while fetching {company_name}: {e}")
        return []

def run_scraper():
    print("DEBUG: Scraper execution started.")
    sheet = get_sheet()
    
    # Check current state of the sheet
    existing_ids = sheet.col_values(1)
    print(f"DEBUG: Found {len(existing_ids)} existing job IDs in Column A.")
    
    companies = [
        ("anthropic", "Anthropic"),
        ("openai", "OpenAI"),
        ("mistralai", "Mistral AI"),
        ("scaleai", "Scale AI"),
        ("perplexity", "Perplexity"),
        ("cohere", "Cohere"),
        ("paloaltonetworks", "Palo Alto Networks")
    ]
    
    total_added = 0
    
    for token, name in companies:
        jobs = fetch_greenhouse_jobs(token, name)
        for job in jobs:
            if job[0] not in existing_ids:
                try:
                    sheet.append_row(job)
                    print(f"SUCCESS: Added '{job[1]}' to sheet.")
                    total_added += 1
                    time.sleep(1.5) # Slight delay to prevent Google API rate limits
                except Exception as e:
                    print(f"ERROR: Failed to write row to Google Sheets: {e}")
            else:
                print(f"SKIP: '{job[1]}' already exists.")

    print(f"\nDEBUG: Scraper finished. Total new jobs added: {total_added}")

if __name__ == "__main__":
    run_scraper()