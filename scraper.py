import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import time
import os

# 1. Setup Google Sheets Connection
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    
    spreadsheet = client.open("Job Board Data")
    
    try:
        # Try to find the specific tab
        return spreadsheet.worksheet("Jobs")
    except gspread.exceptions.WorksheetNotFound:
        # If "Jobs" isn't found, just grab the very first tab available
        print("Worksheet 'Jobs' not found, using the first tab instead.")
        return spreadsheet.get_worksheet(0)

def fetch_greenhouse_jobs(board_token, company_name):
    print(f"--- Fetching: {company_name} ---")
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        new_jobs = []
        # Expanded keywords for "Trust Tech"
        keywords = ["AI", "Privacy", "Ethics", "Policy", "Trust", "Safety", "ESG", "Compliance"]
        
        for job in data.get('jobs', []):
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
                    "" # LogoURL placeholder
                ])
        return new_jobs
    except Exception as e:
        print(f"Error fetching {company_name}: {e}")
        return []

def run_scraper():
    sheet = get_sheet()
    
    # List of high-value targets (Greenhouse tokens)
    companies = [
        ("anthropic", "Anthropic"),
        ("openai", "OpenAI"),
        ("mistralai", "Mistral AI"),
        ("scaleai", "Scale AI"),
        ("perplexity", "Perplexity"),
        ("cohere", "Cohere"),
        ("paloaltonetworks", "Palo Alto Networks")
    ]
    
    existing_ids = sheet.col_values(1)
    
    for token, name in companies:
        jobs = fetch_greenhouse_jobs(token, name)
        for job in jobs:
            if job[0] not in existing_ids:
                sheet.append_row(job)
                print(f"Added: {job[1]} at {name}")
                time.sleep(1) # Be nice to the API
            else:
                print(f"Skipped (Duplicate): {job[1]}")

if __name__ == "__main__":
    run_scraper()