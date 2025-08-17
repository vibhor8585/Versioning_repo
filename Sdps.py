import requests
import re
import os
import smtplib
from email.mime.text import MIMEText


# ---------------------------
# Assembla API Credentials
# ---------------------------
API_KEY = os.getenv("ASSEMBLA_API_KEY", "b3e2b2e478634a951707")
API_SECRET = os.getenv("ASSEMBLA_API_SECRET", "fa4a28e7c094e4542ea4041961a779813ccd218a")
BASE_URL = "https://api.assembla.com"

# ---------------------------
# Email Settings
# ---------------------------
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "vibhorn@plasmacomp.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "wrnvnkbbblxmgqns") 
TO_EMAIL = os.getenv("TO_EMAIL", "vibhornanda09@gmail.com")
CC_EMAIL = os.getenv(" ")

SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587

# ---------------------------
# Get Space ID
# ---------------------------
def get_space_id(space_name):
    url = f"{BASE_URL}/v1/spaces.json"
    try:
        response = requests.get(url, headers={"X-Api-key": API_KEY, "X-Api-Secret": API_SECRET}, timeout=10)
        response.raise_for_status()
        spaces = response.json()
        for space in spaces:
            if space["name"] == space_name:
                return space["id"]
    except requests.RequestException as e:
        print(f"Failed to retrieve spaces: {e}")
    return None

# ---------------------------
# Get Open Milestones
# ---------------------------
def get_open_milestones(space_id):
    page = 1
    all_milestones = []

    while True:
        url = f"{BASE_URL}/v1/spaces/{space_id}/milestones.json?page={page}&per_page=100"
        try:
            response = requests.get(url, headers={"X-Api-key": API_KEY, "X-Api-Secret": API_SECRET}, timeout=10)
            if response.status_code in [200, 204]:
                milestones = response.json()
                if not milestones:
                    break
                all_milestones.extend(milestones)
                page += 1
            else:
                print(f" Failed to retrieve milestones, status code: {response.status_code}")
                break
        except requests.RequestException as e:
            print(f" An error occurred while fetching milestones: {e}")
            break

    open_milestones = [m for m in all_milestones if not m.get("is_completed", False)]

    if not open_milestones:
        print("No open milestones found.")
        return []

    print("Open Milestones:")
    for m in open_milestones:
        print(f"- {m.get('title')} (Due: {m.get('due_date')}, Id: {m.get('id')})")

    return open_milestones

# ---------------------------
# Naming Convention Check
# ---------------------------
def is_valid_name(name):
    pattern = r"^(Console|Workflow|Bigdata|GenAI) \d+\.\d+\.\d+$"
    return bool(re.match(pattern, name))

# ---------------------------
# Send Email via SMTP
# ---------------------------
def send_email_smtp(bad_milestones):
    subject = "Milestones with Wrong Naming Convention"
    body = "Hi,\n\n"
    body += "The following open milestones do not follow the naming convention:\n\n"

    if not bad_milestones:
        body += " All milestones follow the correct naming convention."
    else:
        for m in bad_milestones:
            body += f"- {m.get('title')} (Id: {m.get('id')}, Due: {m.get('due_date')})\n"



    body += "\n\nBest regards,\nVibhor Nanda\nDevOps Support"
    
    
    
    msg = MIMEText(body, 'plain')
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL
    msg['cc'] = CC_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.set_debuglevel(1)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(" Email sent successfully via SMTP!")
    except smtplib.SMTPAuthenticationError:
        print(" Authentication failed. Check your email/password or use an app password if MFA is enabled.")
    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# ---------------------------
# Main
# ---------------------------
def main():
    space_name = "C2M CI"
    space_id = get_space_id(space_name)
    if space_id:
        open_milestones = get_open_milestones(space_id)
        bad_milestones = [m for m in open_milestones if not is_valid_name(m.get("title", ""))]
        send_email_smtp(bad_milestones)
    else:
        print(" Space not found.")

if __name__ == "__main__":
    main()
