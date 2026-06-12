from playwright.sync_api import sync_playwright
from datetime import datetime, timezone
from typing import Dict

POLICIES = {
    "return_policy":        "https://www.sheinindia.in/Return-Policy-a-281.html",
    "privacy_policy":       "https://www.sheinindia.in/Privacy-Policy-a-282.html",
    "terms_and_conditions": "https://www.sheinindia.in/Terms-Conditions-a-283.html",
    "shipping_policy":      "https://www.sheinindia.in/Shipping-Info-a-280.html",
    "payment_security":     "https://www.sheinindia.in/Payment-Security-a-284.html",
}


def fetch_policy(url: str, page) -> str:
    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(2000)
    for sel in ["script", "style", "nav", "header", "footer"]:
        page.eval_on_selector_all(sel, "els => els.forEach(e => e.remove())")
    text = page.inner_text("main, article, .page-content, .policy-content, body")
    return text.strip()


def scrape() -> Dict:
    retailer = "sheinindia"
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()
        for policy_type, url in POLICIES.items():
            print(f"  Fetching {policy_type} ...")
            try:
                text = fetch_policy(url, page)
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
        browser.close()
    return results
