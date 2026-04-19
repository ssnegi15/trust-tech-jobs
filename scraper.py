import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import time
import os
from bs4 import BeautifulSoup

def clean_html(html_content):
    if not html_content:
        return "No description available."
    # Use BeautifulSoup to convert HTML tags into plain text with line breaks
    soup = BeautifulSoup(html_content, "html.parser")
    # This replaces </p>, <br>, and </li> with actual newlines
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for p in soup.find_all("p"):
        p.append("\n")
    for li in soup.find_all("li"):
        li.insert(0, "• ")
        li.append("\n")
        
    return soup.get_text().strip()

def get_sheet():
    print("DEBUG: Authenticating Google Sheets...")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("Job Board Data")
    try:
        return spreadsheet.worksheet("Jobs")
    except:
        return spreadsheet.get_worksheet(0)

def fetch_greenhouse_jobs(board_token, company_name):
    print(f"--- Fetching {company_name} (Greenhouse) ---")
    # Added ?content=true to get the full job description body
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        jobs = data.get('jobs', [])
        new_jobs = []
        keywords = ["AI", "Privacy", "Ethics", "Policy", "Trust", "Safety", "ESG", "Compliance", "Security", "Legal"]
        
        for job in jobs:
            title = job.get('title')
            if any(word.lower() in title.lower() for word in keywords):
                # Greenhouse puts the description in 'content'
                raw_description = job.get('content', "")
                clean_description = clean_html(raw_description)
                
                new_jobs.append([
                    str(job.get('id')), 
                    title, 
                    company_name, 
                    "AI/Policy", 
                    job.get('location', {}).get('name'), 
                    job.get('absolute_url'),
                    clean_description, # REAL DESCRIPTION
                    "" 
                ])
        return new_jobs
    except Exception as e:
        print(f"Error {company_name}: {e}")
        return []

def fetch_lever_jobs(board_token, company_name):
    print(f"--- Fetching {company_name} (Lever) ---")
    url = f"https://api.lever.co/v0/postings/{board_token}"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        new_jobs = []
        keywords = ["AI", "Privacy", "Ethics", "Policy", "Trust", "Safety", "Security"]
        
        for job in data:
            title = job.get('text')
            if any(word.lower() in title.lower() for word in keywords):
                # Lever usually provides 'description' (HTML) or 'descriptionPlain'
                raw_description = job.get('description', "")
                clean_description = clean_html(raw_description)
                
                new_jobs.append([
                    str(job.get('id')), 
                    title, 
                    company_name, 
                    "AI/Policy", 
                    job.get('categories', {}).get('location', 'Remote'), 
                    job.get('hostedUrl'),
                    clean_description, # REAL DESCRIPTION
                    ""
                ])
        return new_jobs
    except Exception as e:
        print(f"Error {company_name}: {e}")
        return []

def run_scraper():
    sheet = get_sheet()
    existing_ids = sheet.col_values(1)
    
    # Expanded list to ensure you see more companies
    greenhouse_list = [
        ("anthropic", "Anthropic"),
        ("scaleai", "Scale AI"),
        ("cohere", "Cohere"),
        ("paloaltonetworks", "Palo Alto Networks"),
        ("appliedintuition", "Applied Intuition")
    ]
    
    lever_list = [
        ("openai", "OpenAI"),
        ("palantir", "Palantir"),
        ("anduril", "Anduril")
    ]
    
    total_added = 0

    for token, name in greenhouse_list:
        jobs = fetch_greenhouse_jobs(token, name)
        for job in jobs:
            if job[0] not in existing_ids:
                sheet.append_row(job)
                existing_ids.append(job[0])
                total_added += 1
                print(f"Added: {job[1]} at {name}")
                time.sleep(1)

    for token, name in lever_list:
        jobs = fetch_lever_jobs(token, name)
        for job in jobs:
            if job[0] not in existing_ids:
                sheet.append_row(job)
                existing_ids.append(job[0])
                total_added += 1
                print(f"Added: {job[1]} at {name}")
                time.sleep(1)

    print(f"Finished. Added {total_added} new jobs.")

if __name__ == "__main__":
    run_scraper()