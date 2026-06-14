import os
import json
from datetime import datetime, timezone
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv

load_dotenv()

MONGO_URI        = os.environ["MONGODB_URI"]
MONGO_DB         = os.getenv("MONGODB_DB", "policy_scraper")
MONGO_COLLECTION = os.getenv("MONGODB_COLLECTION", "policies")


def get_collection():
    client = MongoClient(MONGO_URI)
    return client[MONGO_DB][MONGO_COLLECTION]


def load_to_mongo(retailer: str):
    json_path = os.path.join(
        os.path.dirname(__file__), "output", retailer, "policies.json"
    )
    if not os.path.exists(json_path):
        print(f"  No output found for {retailer} — run main.py first.")
        return

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    collection = get_collection()
    ops = [
        UpdateOne(
            {"retailer": doc["retailer"], "policy_type": doc["policy_type"]},
            {"$set": {**doc, "updated_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True,
        )
        for doc in data.values()
        if doc.get("content")  # skip failed/empty scrapes
    ]

    if not ops:
        print(f"  No valid documents to load for {retailer}.")
        return

    result = collection.bulk_write(ops)
    print(f"  {retailer}: {result.upserted_count} inserted, {result.modified_count} updated.")


if __name__ == "__main__":
    for retailer in ["mamaearth", "sheinindia"]:
        print(f"\nLoading {retailer} -> MongoDB ({MONGO_DB}.{MONGO_COLLECTION})")
        load_to_mongo(retailer)
    print("\nDone.")
