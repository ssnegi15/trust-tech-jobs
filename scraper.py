import gspread
import re
from oauth2client.service_account import ServiceAccountCredentials
import requests
import time
from bs4 import BeautifulSoup
import datetime

def clean_html(html_content):
    """Keeps HTML tags so React can render them, but cleans up scripts."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
    # Return as string so dangerouslySetInnerHTML works
    return str(soup)

def extract_metadata(description):
    desc_lower = description.lower()
    
    # Experience Logic
    exp_match = re.search(r'(\d+\s*(?:-|to|\+)?\s*\d*\s*years?)', desc_lower)
    experience = exp_match.group(1).upper() if exp_match else "Mid Level"
    
    tags = []
    # Tech Stack Detection
    if any(x in desc_lower for x in [".net", "c#", "asp.net", "dotnet", "entity framework"]):
        tags.append(".NET")
    if any(x in desc_lower for x in ["react", "next.js", "typescript", "frontend"]):
        tags.append("React")
    if any(x in desc_lower for x in ["ai", "ml", "llm", "openai", "nlp", "machine learning"]):
        tags.append("AI")
    if any(x in desc_lower for x in ["azure", "aws", "gcp"]):
        tags.append("Cloud")
            
    return experience, ",".join(tags) if tags else "Software"

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("Job Board Data")
    return spreadsheet.get_worksheet(0)

# --- COMPANY LISTS ---

greenhouse_list = [
    # Big Tech / AI
    ("microsoft", "Microsoft"), ("adobe", "Adobe"), ("google", "Google"), ("nvidia", "Nvidia"),
    ("openai", "OpenAI"), ("appliedintuition", "Applied Intuition"), ("paloaltonetworks", "Palo Alto Networks"),
    # NCR / India Tech Hubs
    ("paytm", "Paytm"), ("ixigo", "Ixigo"), ("makemytrip", "MakeMyTrip"), ("airtel", "Airtel"),
    ("zomato", "Zomato"), ("blinkit", "Blinkit"), ("policybazaar", "PolicyBazaar"), 
    # Enterprise .NET/React
    ("chegg", "Chegg"), ("metlife", "MetLife"), ("optum", "Optum"), ("expedia", "Expedia"),
    ("salesforce", "Salesforce"), ("servicenow", "ServiceNow"), ("atlassian", "Atlassian"),
    ("twilio", "Twilio"), ("hubspot", "HubSpot"), ("stripe", "Stripe"), ("cloudera", "Cloudera")
]

lever_list = [
    # AI & Modern Stack
    ("palantir", "Palantir"), ("anduril", "Anduril"), ("anthropic", "Anthropic"), ("cohere", "Cohere"),
    ("fidelity", "Fidelity"), ("docker", "Docker"), ("figma", "Figma"), ("notion", "Notion"),
    # NCR / Growth
    ("urbancompany", "Urban Company"), ("juspay", "Juspay"), ("postman", "Postman"), 
    ("razorpay", "Razorpay"), ("cred", "CRED"), ("meesho", "Meesho"), ("groww", "Groww"),
    # Engineering Heavy
    ("codenation", "CodeNation"), ("thoughtworks", "Thoughtworks"), ("nagaro", "Nagarro"),
    ("bolt", "Bolt"), ("clutter", "Clutter"), ("6sense", "6sense"), ("asana", "Asana"),
    ("benchling", "Benchling"), ("datadog", "DataDog"), ("github", "GitHub")
]

# --- SCRAPER LOGIC ---

def fetch_and_save(sheet, existing_ids):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d")
    total_added = 0
    
    # Process Greenhouse
    for token, name in greenhouse_list:
        url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
        try:
            res = requests.get(url, timeout=10).json()
            for job in res.get('jobs', []):
                jid = str(job.get('id'))
                if jid not in existing_ids:
                    desc = clean_html(job.get('content', ""))
                    exp, tags = extract_metadata(desc)
                    row = [jid, job.get('title'), name, tags, job.get('location', {}).get('name'), job.get('absolute_url'), desc, current_time, exp]
                    sheet.append_row(row)
                    existing_ids.append(jid)
                    total_added += 1
                    print(f"Added {job.get('title')} @ {name}")
                    time.sleep(0.5)
        except: continue

    # Process Lever
    for token, name in lever_list:
        url = f"https://api.lever.co/v0/postings/{token}"
        try:
            res = requests.get(url, timeout=10).json()
            for job in res:
                jid = str(job.get('id'))
                if jid not in existing_ids:
                    desc = clean_html(job.get('description', ""))
                    exp, tags = extract_metadata(desc)
                    row = [jid, job.get('text'), name, tags, job.get('categories', {}).get('location'), job.get('hostedUrl'), desc, current_time, exp]
                    sheet.append_row(row)
                    existing_ids.append(jid)
                    total_added += 1
                    print(f"Added {job.get('text')} @ {name}")
                    time.sleep(0.5)
        except: continue

    print(f"Done! Added {total_added} jobs.")

if __name__ == "__main__":
    sheet = get_sheet()
    existing_ids = sheet.col_values(1)
    fetch_and_save(sheet, existing_ids)