import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import time
import os
from bs4 import BeautifulSoup # To clean the HTML tags

# Helper to turn HTML into clean plain text for the Spreadsheet
def clean_html(html_content):
    if not html_content:
        return "No description available."
    soup = BeautifulSoup(html_content, "html.parser")
    # This removes script/style tags and gives us just the text
    return soup.get_text(separator='\n').strip()

def get_sheet():
    print("DEBUG: starting Google Sheets authentication...")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("Job Board Data")
    try:
        return spreadsheet.worksheet("Jobs")
    except gspread.exceptions.WorksheetNotFound:
        return spreadsheet.get_worksheet(0)

def fetch_greenhouse_jobs(board_token, company_name):
    print(f"\n--- DEBUG: Fetching {company_name} (Greenhouse) ---")
    # We add ?content=true to Greenhouse to get the full description
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        filtered = []
        keywords = ["AI", "Privacy", "Ethics", "Policy", "Trust", "Safety", "ESG", "Compliance"]
        
        for job in data.get('jobs', []):
            title = job.get('title')
            if any(word.lower() in title.lower() for word in keywords):
                # Greenhouse content is in 'content' field
                raw_desc = job.get('content', "")
                description = clean_html(raw_desc)
                
                filtered.append([
                    str(job.get('id')), 
                    title, 
                    company_name, 
                    "Trust Tech", 
                    job.get('location', {}).get('name'), 
                    job.get('absolute_url'),
                    description, # Real Description!
                    "" 
                ])
        return filtered
    except Exception as e:
        print(f"ERROR: Greenhouse failed for {company_name}: {e}")
        return []

def fetch_lever_jobs(board_token, company_name):
    print(f"\n--- DEBUG: Fetching {company_name} (Lever) ---")
    url = f"https://api.lever.co/v0/postings/{board_token}"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        filtered = []
        keywords = ["AI", "Privacy", "Ethics", "Policy", "Trust", "Safety"]
        
        for job in data:
            title = job.get('text')
            if any(word.lower() in title.lower() for word in keywords):
                # Lever content is usually in 'descriptionPlain' or 'description'
                description = job.get('descriptionPlain', "")
                if not description:
                    description = clean_html(job.get('description', ""))
                
                filtered.append([
                    str(job.get('id')), 
                    title, 
                    company_name, 
                    "Trust Tech", 
                    job.get('categories', {}).get('location'), 
                    job.get('hostedUrl'),
                    description, # Real Description!
                    ""
                ])
        return filtered
    except Exception as e:
        print(f"ERROR: Lever failed for {company_name}: {e}")
        return []

def run_scraper():
    sheet = get_sheet()
    existing_ids = sheet.col_values(1)
    
    gh_targets = [("anthropic", "Anthropic"), ("scaleai", "Scale AI")]
    lever_targets = [("openai", "OpenAI"), ("palantir", "Palantir")]

    for token, name in gh_targets:
        jobs = fetch_greenhouse_jobs(token, name)
        for job in jobs:
            if job[0] not in existing_ids:
                sheet.append_row(job)
                print(f"SUCCESS: Added {job[1]}")
                time.sleep(1)

    for token, name in lever_targets:
        jobs = fetch_lever_jobs(token, name)
        for job in jobs:
            if job[0] not in existing_ids:
                sheet.append_row(job)
                print(f"SUCCESS: Added {job[1]}")
                time.sleep(1)

if __name__ == "__main__":
    run_scraper()