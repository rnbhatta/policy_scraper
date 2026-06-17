from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from datetime import datetime, timezone
from typing import Dict, Optional
from scrapers.proxy_helper import find_working_proxy

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

    content = page.content()
    if "Access Denied" in content or "403" in content:
        raise Exception("Access denied — proxy blocked by WAF")

    for sel in ["script", "style", "nav", "header", "footer"]:
        page.eval_on_selector_all(sel, "els => els.forEach(e => e.remove())")

    text = page.inner_text("main, article, .page-content, .policy-content, body")
    return text.strip()


def scrape(proxy: Optional[str] = None) -> Dict:
    retailer = "sheinindia"
    results = {}

    if proxy is None:
        proxy = find_working_proxy()

    if proxy is None:
        print("  No working proxy found. Skipping SHEIN scrape.")
        return {}

    print(f"  Using proxy: {proxy}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            proxy={"server": f"http://{proxy}"},
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="en-IN",
            timezone_id="Asia/Kolkata",
        )
        page = context.new_page()
        Stealth().apply_stealth_sync(page)

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
