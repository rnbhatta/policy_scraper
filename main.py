import json
import os
from datetime import datetime, timezone
from scrapers import mamaearth, sheinindia

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def save_json(retailer: str, data: dict):
    path = os.path.join(OUTPUT_DIR, retailer, "policies.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Saved JSON -> {path}")


def save_markdown(retailer: str, data: dict):
    lines = [f"# {retailer.title()} — Policies\n"]
    lines.append(f"_Scraped at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_\n")
    lines.append("---\n")
    for policy_type, doc in data.items():
        title = policy_type.replace("_", " ").title()
        lines.append(f"## {title}\n")
        lines.append(f"**Source:** {doc['url']}\n")
        if doc.get("error"):
            lines.append(f"_Error: {doc['error']}_\n")
        else:
            lines.append(doc["content"])
        lines.append("\n---\n")
    path = os.path.join(OUTPUT_DIR, retailer, "policies.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Saved MD  -> {path}")


def run(retailer: str, scraper_module):
    print(f"\n{'='*50}")
    print(f"Scraping: {retailer}")
    print(f"{'='*50}")
    os.makedirs(os.path.join(OUTPUT_DIR, retailer), exist_ok=True)
    data = scraper_module.scrape()
    save_json(retailer, data)
    save_markdown(retailer, data)
    print(f"Done: {len(data)} policies saved.")


if __name__ == "__main__":
    run("mamaearth", mamaearth)
    run("sheinindia", sheinindia)
