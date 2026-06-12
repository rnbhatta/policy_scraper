import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from typing import Dict

POLICIES = {
    "return_policy":            "https://mamaearth.in/return-policy",
    "privacy_policy":           "https://mamaearth.in/privacy-policy",
    "terms_and_conditions":     "https://mamaearth.in/terms-and-conditions",
    "cashback_terms":           "https://mamaearth.in/terms-and-conditions-cashback",
    "loyalty_program_terms":    "https://mamaearth.in/goodness-insider/terms-and-conditions",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_policy(url: str) -> str:
    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=30) as client:
        response = client.get(url)
        response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find(class_=lambda c: c and "policy" in c.lower())
        or soup.find(class_=lambda c: c and "content" in c.lower())
        or soup.body
    )
    return main.get_text(separator="\n", strip=True) if main else ""


def scrape() -> Dict:
    retailer = "mamaearth"
    results = {}
    for policy_type, url in POLICIES.items():
        print(f"  Fetching {policy_type} ...")
        try:
            text = fetch_policy(url)
            results[policy_type] = {
                "retailer":    retailer,
                "policy_type": policy_type,
                "url":         url,
                "content":     text,
                "scraped_at":  datetime.now(timezone.utc).isoformat(),
            }
            print(f"  OK ({len(text)} chars)")
        except Exception as e:
            print(f"  FAILED: {e}")
            results[policy_type] = {
                "retailer":    retailer,
                "policy_type": policy_type,
                "url":         url,
                "content":     "",
                "error":       str(e),
                "scraped_at":  datetime.now(timezone.utc).isoformat(),
            }
    return results
