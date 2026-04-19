import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import time
import os

# --- CONFIGURATION & AUTH ---

def get_sheet():
    print("DEBUG: starting Google Sheets authentication...")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Check for credentials file
    if not os.path.exists("credentials.json"):
        print("ERROR: credentials.json not found! Ensure it is in the root directory.")
        raise FileNotFoundError("Missing credentials.json")
    
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

# --- FETCHERS ---

def fetch_greenhouse_jobs(board_token, company_name):
    print(f"\n--- DEBUG: Fetching {company_name} (Greenhouse: {board_token}) ---")
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            print(f"DEBUG: Skipping {company_name}, API returned {response.status_code}")
            return []
            
        data = response.json()
        all_jobs = data.get('jobs', [])
        print(f"DEBUG: Found {len(all_jobs)} total open roles.")
        
        filtered = []
        keywords = ["AI", "Privacy", "Ethics", "Policy", "Trust", "Safety", "ESG", "Compliance", "Security"]
        
        for job in all_jobs:
            title = job.get('title')
            if any(word.lower() in title.lower() for word in keywords):
                filtered.append([
                    str(job.get('id')), 
                    title, 
                    company_name, 
                    "Trust Tech", 
                    job.get('location', {}).get('name'), 
                    job.get('absolute_url'),
                    f"Role at {company_name}", 
                    "" 
                ])
        print(f"DEBUG: Filtered to {len(filtered)} relevant roles.")
        return filtered
    except Exception as e:
        print(f"ERROR: Greenhouse fetch failed for {company_name}: {e}")
        return []

def fetch_lever_jobs(board_token, company_name):
    print(f"\n--- DEBUG: Fetching {company_name} (Lever: {board_token}) ---")
    url = f"https://api.lever.co/v0/postings/{board_token}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            print(f"DEBUG: Skipping {company_name}, API returned {response.status_code}")
            return []
            
        data = response.json()
        print(f"DEBUG: Found {len(data)} total open roles.")
        
        filtered = []
        keywords = ["AI", "Privacy", "Ethics", "Policy", "Trust", "Safety", "ESG", "Compliance", "Security"]
        
        for job in data:
            title = job.get('text')
            if any(word.lower() in title.lower() for word in keywords):
                filtered.append([
                    str(job.get('id')), 
                    title, 
                    company_name, 
                    "Trust Tech", 
                    job.get('categories', {}).get('location', 'Remote/Various'), 
                    job.get('hostedUrl'),
                    f"Role at {company_name}", 
                    "" 
                ])
        print(f"DEBUG: Filtered to {len(filtered)} relevant roles.")
        return filtered
    except Exception as e:
        print(f"ERROR: Lever fetch failed for {company_name}: {e}")
        return []

# --- MAIN EXECUTION ---

def run_scraper():
    print("DEBUG: Scraper execution started.")
    sheet = get_sheet()
    
    # Get existing IDs to prevent duplicates (assumes ID is in Column A)
    existing_ids = sheet.col_values(1)
    print(f"DEBUG: Found {len(existing_ids)} existing job IDs in sheet.")
    
    # Define targets
    # Note: OpenAI and Palantir use Lever. Anthropic and Scale use Greenhouse.
    greenhouse_targets = [
        ("anthropic", "Anthropic"),
        ("scaleai", "Scale AI"),
        ("cohere", "Cohere"),
    ]
    
    lever_targets = [
        ("openai", "OpenAI"),
        ("palantir", "Palantir"),
    ]
    
    total_added = 0

    # Process Greenhouse
    for token, name in greenhouse_targets:
        jobs = fetch_greenhouse_jobs(token, name)
        for job in jobs:
            if job[0] not in existing_ids:
                try:
                    sheet.append_row(job)
                    print(f"SUCCESS: Added '{job[1]}' ({name})")
                    existing_ids.append(job[0]) # Update local list
                    total_added += 1
                    time.sleep(1) 
                except Exception as e:
                    print(f"ERROR: Write failed: {e}")
            else:
                print(f"SKIP: '{job[1]}' already in sheet.")

    # Process Lever
    for token, name in lever_targets:
        jobs = fetch_lever_jobs(token, name)
        for job in jobs:
            if job[0] not in existing_ids:
                try:
                    sheet.append_row(job)
                    print(f"SUCCESS: Added '{job[1]}' ({name})")
                    existing_ids.append(job[0])
                    total_added += 1
                    time.sleep(1)
                except Exception as e:
                    print(f"ERROR: Write failed: {e}")
            else:
                print(f"SKIP: '{job[1]}' already in sheet.")

    print(f"\nDEBUG: Scraper finished. Total new jobs added: {total_added}")

if __name__ == "__main__":
    run_scraper()