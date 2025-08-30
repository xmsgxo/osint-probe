import httpx
import asyncio

SITES_TO_CHECK = {
    "Instagram": "https://www.instagram.com/{}",
    "Twitter": "https://www.twitter.com/{}",
    "GitHub": "https://www.github.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "TikTok": "https://www.tiktok.com/@{}",
}

async def check_site(client, site, url):
    """Helper function to check a single site."""
    try:
        response = await client.head(url, follow_redirects=True, timeout=5)
        if response.status_code == 200:
            return site, url, True
    except httpx.RequestError:
        pass
    return site, url, False

async def find_username(username):
    """Searches for a username across multiple platforms."""
    print(f"\n--- 👤 Username Analysis for {username} ---")
    print(f"Searching across {len(SITES_TO_CHECK)} sites... Please wait.")

    found_sites = []
    async with httpx.AsyncClient() as client:
        tasks = [check_site(client, site, url.format(username)) for site, url in SITES_TO_CHECK.items()]
        results = await asyncio.gather(*tasks)

        for site, url, found in results:
            if found:
                found_sites.append((site, url))

    if found_sites:
        print("✅ Found on the following sites:")
        for site, url in found_sites:
            print(f"  - {site}: {url}")
    else:
        print("❌ Username not found on any of the checked sites.")
