 import os
import requests

# Environment Variables se Tokens nikalna
APIFY_TOKEN = os.environ.get("APIFY_TOKEN")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_discord_msg(message):
    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code != 204:
        print(f"Error sending Discord message: {response.status_code}, {response.text}")

def run_apify_maps_scraper():
    # Correct Endpoint & Actor ID
    actor_id = "compass~crawler-google-places"
    run_url = f"https://api.apify.com/v2/actors/{actor_id}/run-sync-get-dataset-items?token={APIFY_TOKEN}"

    payload = {
        "searchStringsArray": ["Dental Clinic in Los Angeles"],
        "maxCrawledPlacesPerSearch": 10,
        "language": "en"
    }

    print("Scraping started via Apify...")
    response = requests.post(run_url, json=payload)

    if response.status_code != 201 and response.status_code != 200:
        print("Apify Run Error:", response.text)
        return

    items = response.json()
    found_leads = []

    for item in items:
        name = item.get("title", "Unknown Name")
        website = item.get("website", None)
        phone = item.get("phone", "No Phone")

        # 1. High Priority: Website bilkul nahi hai
        if not website:
            found_leads.append(f"🔴 **NO WEBSITE**\n**Name:** {name}\n**Phone:** {phone}\n")
            continue

        # 2. Medium Priority: Website hai
        found_leads.append(f"🟡 **HAS WEBSITE (Check Chatbot)**\n**Name:** {name}\n**Phone:** {phone}\n**Site:** {website}\n")

    # Discord par notification bhejna
   
    else:
        send_discord_msg("ℹ️️ Is run me koi lead nahi mili.")
if __name__ == "__main__":
    run_apify_maps_scraper()
