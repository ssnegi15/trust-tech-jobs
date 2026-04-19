import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
import time

# 1. Setup Google Sheets Connection
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
# Replace with your actual Google Sheet name
sheet = client.open("Job Board Data").worksheet("Jobs")

def fetch_greenhouse_jobs(board_token, company_name):
    print(f"Fetching jobs for {company_name}...")
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    response = requests.get(url).json()
    
    new_jobs = []
    keywords = ["AI", "Privacy", "Trust", "Ethics", "Policy", "ESG"]
    
    for job in response.get('jobs', []):
        title = job.get('title')
        # Filter for "Trusted Tech" roles
        if any(word.lower() in title.lower() for word in keywords):
            new_jobs.append([
                job.get('id'),        # ID
                title,                 # Title
                company_name,          # Company
                "AI/Privacy",          # Category (Manual/Logic)
                job.get('location', {}).get('name'), # Location
                job.get('absolute_url'), # Link
                "Scraped Role",        # Description
                ""                     # LogoURL
            ])
    return new_jobs

def run_scraper():
    # Example: Anthropic uses Greenhouse
    anthropic_jobs = fetch_greenhouse_jobs("anthropic", "Anthropic")
    
    # Get existing IDs from Sheet to avoid duplicates
    existing_ids = sheet.col_values(1)
    
    for job in anthropic_jobs:
        if str(job[0]) not in existing_ids:
            sheet.append_row(job)
            print(f"Added: {job[1]}")
            time.sleep(1) # Avoid rate limits

if __name__ == "__main__":
    run_scraper()