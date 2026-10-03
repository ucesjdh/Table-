"""
ercol Outlet monitor: emails you when new dining tables or dining chairs appear.
https://www.ercol.com/en-gb/our-company/ercol-outlet
"""
import json, os, re, smtplib, sys
from email.mime.text import MIMEText
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://www.ercol.com/en-gb/our-company/ercol-outlet"
BASE = "https://www.ercol.com"
STATE = Path("seen.json")

# ---- Matching rules (edit to taste) -----------------------------------
# Matching is done on the product's URL slug, e.g. "romana-dining-chair-in-cm-l806"
TABLE_EXCLUDE = ["coffee", "lamp", "nest", "bedside", "console", "dressing"]
# Upholstered lounge chairs, armchairs, etc. that the site calls "Chair" but aren't dining chairs
CHAIR_EXCLUDE = ["armchair", "recliner", "aldbury", "sandford", "forli", "enna",
                 "bronte", "marino", "aosta", "noto", "mondello", "reprise",
                 "prototype", "studio-couch"]
# -------------------------------------------------------------------------

def is_dining(slug: str) -> bool:
    words = slug.lower().split("-")
    if "dining" in words:                       # "Dining Chair", "Dining Table", "Dining Armchair"
        return True
    if "table" in words or "tables" in words:
        return not any(x in slug for x in TABLE_EXCLUDE)
    if "chair" in words or "chairs" in words:
        return not any(x in slug for x in CHAIR_EXCLUDE)
    return False

def fetch_products() -> dict:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}
    r = requests.get(URL, headers=headers, timeout=60)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    products = {}
    for a in soup.find_all("a", href=True):
        m = re.search(r"/ercol-outlet/([a-z0-9-]+)/?$", a["href"])
        if not m:
            continue
        slug = m.group(1)
        text = " ".join(a.get_text(" ", strip=True).split())
        price = re.search(r"£[\d,]+(?:\.\d{2})?", text)
        products[slug] = {
            "url": BASE + "/en-gb/our-company/ercol-outlet/" + slug,
            "text": text,
            "price": price.group(0) if price else "",
        }
    return products

def send_email(items: list):
    user, pwd = os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"].replace(" ", "")
    to = os.environ.get("EMAIL_TO", user)
    lines = [f"{p['text']}\n{p['url']}\n" for p in items]
    msg = MIMEText("New dining items in the ercol Outlet:\n\n" + "\n".join(lines))
    msg["Subject"] = f"ercol Outlet: {len(items)} new dining item(s)"
    msg["From"], msg["To"] = user, to
    with smtplib.SMTP_SSL(os.environ.get("SMTP_HOST", "smtp.gmail.com"), 465) as s:
        s.login(user, pwd)
        s.send_message(msg)

def main():
    products = fetch_products()
    if len(products) < 20:   # page layout changed or request blocked -> fail loudly
        sys.exit(f"Only found {len(products)} products; the page may have changed.")
    dining = {k: v for k, v in products.items() if is_dining(k)}
    print(f"{len(products)} products, {len(dining)} dining tables/chairs")

    first_run = not STATE.exists()
    seen = set(json.loads(STATE.read_text())) if not first_run else set()
    new = [dining[k] for k in dining if k not in seen]

    if first_run:
        print("First run: recording current stock, no email sent.")
    elif new:
        print(f"{len(new)} new: " + ", ".join(p["text"][:60] for p in new))
        send_email(new)
    else:
        print("Nothing new.")

    STATE.write_text(json.dumps(sorted(seen | set(dining)), indent=1))

if __name__ == "__main__":
    main()
