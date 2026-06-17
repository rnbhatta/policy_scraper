import httpx
from typing import Optional


PROXY_APIS = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=elite",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=anonymous",
]

TEST_URL = "https://www.sheinindia.in/"


def fetch_proxy_list() -> list[str]:
    proxies = []
    for url in PROXY_APIS:
        try:
            r = httpx.get(url, timeout=10)
            lines = [l.strip() for l in r.text.splitlines() if l.strip()]
            proxies.extend(lines)
        except Exception:
            pass
    # deduplicate
    return list(dict.fromkeys(proxies))


def test_proxy(proxy: str) -> bool:
    try:
        r = httpx.get(
            TEST_URL,
            proxies={"http://": f"http://{proxy}", "https://": f"http://{proxy}"},
            timeout=8,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )
        return r.status_code == 200
    except Exception:
        return False


def find_working_proxy(max_tries: int = 30) -> Optional[str]:
    print("  Fetching proxy list...")
    proxies = fetch_proxy_list()
    print(f"  Got {len(proxies)} proxies. Testing up to {max_tries}...")
    for i, proxy in enumerate(proxies[:max_tries]):
        print(f"  [{i+1}/{max_tries}] Testing {proxy} ...", end=" ", flush=True)
        if test_proxy(proxy):
            print("OK")
            return proxy
        print("fail")
    return None
