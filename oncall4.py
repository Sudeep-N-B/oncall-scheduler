import os
import requests
import datetime

OUTLINE_URL = "https://docs.dpdzero.com"
OUTLINE_TOKEN = os.getenv("OUTLINE_TOKEN")
DOCUMENT_ID = "2dba7c0c-26c6-4005-a82c-fab2e0d8a75a"
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"


# Slack user IDs mapping 
slack_id_map = {
    "Sudeep": "U087FA2BPFW",
    "Jaswant Kondur": "U063WPVFQ2X",
    "Ibrahim Abdul Mujeeb": "U03M543QH8D",
    "Krupal M R": "U07P61J74P9",
    "Vadiraj Karanam": "U07CYG0RVPW",
    "Shambhavi Priya": "U07LFG61PBM",
    "Ramkumar S V": "U07G8MBFL4W",
    "Avi Apratim Sinha": "U05QPCUN7A4",
    "Yogeshwar Trehan": "U0888PW6685",
    "Abhilash Hegde": "U0783AV4W6P",
    "Akshat Yadav": "U03LTDL171D",
    "Momin Uzma": "U07NQCBUCFP",
    "Sharat Koliwad": "U07B51ZL5LJ"
}

headers = {
    "Authorization": f"Bearer {OUTLINE_TOKEN}",
    "Content-Type": "application/json"
}

response = requests.post(f"{OUTLINE_URL}/api/documents.info", headers=headers, json={"id": DOCUMENT_ID})

if response.status_code != 200:
    print("❌ Failed to fetch document:", response.status_code, response.text)
    exit()

content = response.json()["data"]["text"]
lines = content.splitlines()

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)

users_to_alert = []

for line in lines:
    if '|' not in line or 'Name' in line or '---' in line:
        continue

    parts = [p.strip() for p in line.strip('|').split('|')]

    if len(parts) < 6:
        continue

    date_str = parts[0]
    name = parts[2]
    remarks = parts[5]

    try:
        entry_date = datetime.date(2025, 5, int(date_str))
    except ValueError:
        continue

    if entry_date == tomorrow:
        slack_user_id = slack_id_map.get(name)
        formatted_date = entry_date.strftime("%d-%m-%Y")
        if slack_user_id:
            users_to_alert.append(f"<@{slack_user_id}> is on-call monitoring tomorrow ({formatted_date}).")
        else:
            users_to_alert.append(f"{name} is on-call monitoring tomorrow ({formatted_date}).")

if users_to_alert:
    message = "*On-Call Monitoring Reminder:*\n" + "\n".join(f"• {entry}" for entry in users_to_alert)
    slack_response = requests.post(SLACK_WEBHOOK_URL, json={"text": message})

    if slack_response.status_code == 200:
        print("✅ Slack alert sent.")
    else:
        print("❌ Failed to send Slack message:", slack_response.status_code, slack_response.text)
else:
    print("✅ No one is on-call monitoring tomorrow.")
