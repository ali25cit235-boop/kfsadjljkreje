import os
import requests
from bs4 import BeautifulSoup

# Discord Webhook URL
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_discord_msg(message):
    if not DISCORD_WEBHOOK_URL:
        print("Discord Webhook URL missing!")
        return
    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code != 204:
        print(f"Error sending Discord message: {response.status_code}, {response.text}")

def fetch_leads_osm(city="Los Angeles", amenity="dentist"):
    # HTTPS URL aur Proper Headers (User-Agent fix)
    overpass_url = "https://overpass-api.de/api/interpreter"
    headers = {
        "User-Agent": "LeadFinderAgent/1.0 (Contact: mybot@gmail.com)"
    }
    
    query = f"""
    [out:json];
    area["name"="{city}"]->.searchArea;
    node["amenity"="{amenity}"](area.searchArea);
    out body 15;
    """
    
    print("Fetching leads from OpenStreetMap...")
    response = requests.post(overpass_url, data={'data': query}, headers=headers)
    
    if response.status_code != 200:
        print("API Error:", response.text)
        return

    data = response.json()
    elements = data.get("elements", [])
    found_leads = []

    for item in elements:
        tags = item.get("tags", {})
        name = tags.get("name")
        if not name:
            continue
            
        website = tags.get("website") or tags.get("contact:website")
        phone = tags.get("phone") or tags.get("contact:phone", "No Phone")

        # 1. High Priority: Website nahi hai
        if not website:
            found_leads.append(f"🔴 **NO WEBSITE**\n**Name:** {name}\n**Phone:** {phone}\n")
            continue

        # 2. Check Chatbot on Website
        has_chatbot = False
        try:
            res = requests.get(website, timeout=5, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            page_text = str(soup).lower()
            if any(bot in page_text for bot in ['taidio', 'intercom', 'drift', 'chatbot', 'crisp', 'collect.chat']):
                has_chatbot = True
        except:
            pass

        if not has_chatbot:
            found_leads.append(f"🟡 **NO CHATBOT**\n**Name:** {name}\n**Phone:** {phone}\n**Site:** {website}\n")

    # Result Discord par bhejna
    if found_leads:
        report = f"🎯 **NEW LEADS FOUND ({len(found_leads)})**\n\n" + "\n---\n".join(found_leads[:5])
        send_discord_msg(report)
    else:
        send_discord_msg("ℹ️ Is run me koi lead nahi mili.")

if __name__ == "__main__":
    fetch_leads_osm()
