import httpx
from bs4 import BeautifulSoup

# We will use a public website as our data source
URL = "https://www.avast.com/hackcheck/"

async def check_email_breaches(email):
    """
    Scrapes a public website to check for email breaches,
    since the HIBP API is no longer free.
    """
    print(f"\n--- 📧 Email Breach Analysis for {email} ---")
    print("Checking public breach databases... (This may take a moment)")

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            # First, get the necessary cookies and CSRF token from the site
            initial_response = await client.get(URL)
            initial_response.raise_for_status() # Raise an exception for bad status codes
            
            soup = BeautifulSoup(initial_response.text, 'html.parser')
            # Find the security token needed to submit the form
            csrf_token = soup.find('input', {'name': '_csrf_token'})
            
            if not csrf_token:
                print("❌ Could not find the necessary security token to submit the form.")
                return

            # Now, submit the email to the website's form
            form_data = {
                'email': email,
                '_csrf_token': csrf_token['value']
            }
            
            check_response = await client.post(URL, data=form_data)
            check_response.raise_for_status()
            
            # Parse the results page
            results_soup = BeautifulSoup(check_response.text, 'html.parser')
            
            # Look for the section that lists the breaches
            leaks_list = results_soup.find('ul', {'class': 'leaks-list'})
            
            if leaks_list:
                breaches = leaks_list.find_all('li')
                print(f"🚨 DANGER: Email found in {len(breaches)} data breaches!")
                for breach in breaches:
                    site_name = breach.find('span', {'class': 'site-name'})
                    if site_name:
                        print(f"  - Breach Source: {site_name.text.strip()}")
            else:
                 # Check for a "no results" message
                no_results = results_soup.find(text=lambda t: "no leaks were found" in t.lower())
                if no_results:
                    print("✅ GOOD: Email not found in any known data breaches.")
                else:
                    print("🤔 Could not determine the result. The website may have changed.")


    except httpx.RequestError as e:
        print(f"❌ An error occurred: Could not connect to the data source. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
