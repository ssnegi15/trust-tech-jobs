import gspread
import re
from oauth2client.service_account import ServiceAccountCredentials
import requests
import time
import os
from bs4 import BeautifulSoup
import datetime


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

def extract_metadata(description):
    # Improved regex for Indian experience formats (e.g., "3-5 years", "4+ years")
    exp_match = re.search(r'(\d+\s*(?:-|to|\+)?\s*\d*\s*years?)', description, re.IGNORECASE)
    experience = exp_match.group(1) if exp_match else "Entry/Mid"
    
    # Tagging specifically for your filters
    tags = []
    if ".net" in description.lower() or "c#" in description.lower(): tags.append(".NET")
    if "react" in description.lower(): tags.append("React")
    if "ai" in description.lower() or "ml" in description.lower(): tags.append("AI")
            
    return experience, ",".join(tags) if tags else "Software"

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
        keywords = ["AI", "Privacy", "Ethics", "Policy", "Trust", "Safety", ".NET", "React", "C#", "Frontend", "Backend"]
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for job in jobs:
            title = job.get('title')
            if any(word.lower() in title.lower() for word in keywords):
                # Greenhouse puts the description in 'content'
                raw_description = job.get('content', "")
                clean_description = clean_html(raw_description)
                exp, tech_tags = extract_metadata(clean_description)
                new_jobs.append([
                    str(job.get('id')), 
                    title, 
                    company_name, 
                    tech_tags, 
                    job.get('location', {}).get('name'), 
                    job.get('absolute_url'),
                    clean_description, # REAL DESCRIPTION
                    current_time, # Added Date for sorting
                    exp
                ])
        return new_jobs
    except Exception as e:
        print(f"Error {company_name}: {e}")
        return []

def fetch_lever_jobs(board_token, company_name):
    print(f"--- Fetching {company_name} (Lever) ---")
    url = f"https://api.lever.co/v0/postings/{board_token}"
    
    # Adding headers to prevent 403/Unexpected format errors
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        # If response is not 200, Lever might be blocking or token is wrong
        if response.status_code != 200:
            print(f"Skipping {company_name}: Received status {response.status_code}")
            return []

        data = response.json() 
        new_jobs = []
        
        # Expanded keywords for NCR Tech
        keywords = ["AI", ".NET", "React", "C#", "Frontend", "Software", "Full Stack", "Node"]
        
        # Ensure data is a list (Lever's standard format)
        job_list = data if isinstance(data, list) else []

        for job in job_list:
            title = job.get('text', 'Untitled Role')
            location = job.get('categories', {}).get('location', 'Remote')
            
            # Check if it matches technology OR region
            is_tech = any(word.lower() in title.lower() for word in keywords)
            is_ncr = any(loc.lower() in location.lower() for loc in ["noida", "gurgaon", "gurugram", "delhi", "ncr"])

            if is_tech or is_ncr:
                raw_description = job.get('description', "")
                clean_description = clean_html(raw_description)
                
                # Use the metadata extractor we built
                exp, tech_tags = extract_metadata(clean_description)
                
                new_jobs.append([
                    str(job.get('id')), 
                    title, 
                    company_name, 
                    tech_tags, 
                    location, 
                    job.get('hostedUrl'),
                    clean_description,
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    exp
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
    ("paytm", "Paytm"),               # React (Noida HQ)
    ("ixigo", "Ixigo"),               # React/Frontend (Gurgaon)
    ("makemytrip", "MakeMyTrip"),     # React (Gurgaon)
    ("expedia", "Expedia Group"),     # React/.NET (Gurgaon office)
    ("adobe", "Adobe"),               # React/C++ (Noida/Gurgaon)
    ("airtel", "Airtel Digital"),     # React (Gurgaon)
    ("paloaltonetworks", "Palo Alto Networks"), # Security (Gurgaon)
    ("appliedintuition", "Applied Intuition"), # AI (Noida hub)
    ("cisco", "Cisco Systems"),       # React/Network (Gurgaon)
    ("vmware", "VMware"),             # React/Cloud (Gurgaon)
    ("microsoft", "Microsoft India"), # .NET/AI (Multiple NCR locations)
    ("google", "Google India"),       # AI/Policy (Multiple NCR locations)
    ("amazon", "Amazon India"),       # AI/Cloud (Multiple NCR locations)
    ("facebook", "Meta India"),        # AI/Policy (Multiple NCR locations)
    ("oracle", "Oracle India"),        # React/Cloud (Gurgaon)
    ("salesforce", "Salesforce India"), # React/Cloud (Gurgaon)
    ("twosigma", "Two Sigma")   # AI/Quant (Gurgaon)

    ]   

# Lever: Enterprise .NET & High-Growth Startups in NCR
    lever_list = [
    ("indiamart", "IndiaMART"),       # React/.NET (Noida)
    ("stack-overflow", "Stack Overflow"), # .NET (Remote-friendly India)
    ("fidelity", "Fidelity"),         # .NET (Massive Gurgaon presence)
    ("cars24", "CARS24"),             # React (Gurgaon HQ)
    ("urbancompany", "Urban Company"),# React (Gurgaon HQ)
    ("shuttl", "Shuttl"),             # React (Gurgaon)
    ("openai", "OpenAI"),             # AI
    ("anduril", "Anduril"),            # AI/Defense
    ("rubrik", "Rubrik"),              # Cloud/Security (Gurgaon)
    ("databricks", "Databricks"),        # AI/Cloud (Gurgaon)
    ("hashicorp", "HashiCorp"),         # Cloud/Infrastructure (Gurgaon)
    ("okta", "Okta"),                   # Security (Gurgaon)
    ("splunk", "Splunk"),               # Security/Cloud (Gurgaon)
    ("snowflake", "Snowflake"),         # Cloud/Data (Gurgaon)
    ("cloudera", "Cloudera"),            # Cloud/Data (Gurgaon)
    ("elastic", "Elastic"),               # Search/Cloud (Gurgaon)
    ("confluent", "Confluent"),           # Cloud/Data (Gurgaon)
    ("datadog", "Datadog"),               # Cloud/Monitoring (Gurgaon)
    ("newrelic", "New Relic"),           # Cloud/Monitoring (Gurgaon)
    ("splunk", "Splunk"),               # Security/Cloud (Gurgaon)
    ("rubrik", "Rubrik"),              # Cloud/Security (Gurgaon)
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