import httpx

async def check_email_breaches(email, api_key):
    """Checks an email against the Have I Been Pwned API."""
    print(f"\n--- 📧 Email Breach Analysis for {email} ---")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("❌ HIBP API Key not found in config.py. Please create the file and add your key.")
        return

    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {
        "hibp-api-key": api_key,
        "user-agent": "OSINT-Probe"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                breaches = response.json()
                print(f"🚨 DANGER: Email found in {len(breaches)} data breaches!")
                for breach in breaches:
                    print(f"  - Breach: {breach['Name']} ({breach['BreachDate']})")
            elif response.status_code == 404:
                print("✅ GOOD: Email not found in any known data breaches.")
            else:
                print(f"❌ Error: Received status code {response.status_code}")
                print(f"   Message: {response.text}")

    except Exception as e:
        print(f"An error occurred during the request: {e}")
