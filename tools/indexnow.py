"""Send new or changed sitemap URLs to IndexNow (Naver, Bing). Run by .github/workflows/indexnow.yml."""
import glob, json, os, re, subprocess, time, urllib.request

HOST = "webstudio-4e9.pages.dev"
KEY = next(os.path.basename(f)[:-4] for f in glob.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}\.txt", os.path.basename(f)))
ENDPOINTS = ["https://searchadvisor.naver.com/indexnow", "https://api.indexnow.org/indexnow"]


def urls(xml):
    return re.findall(r"<loc>([^<]+)</loc>", xml)


def get(url):
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return r.status
    except Exception:
        return 0


now = urls(open("sitemap.xml", encoding="utf-8").read())
before = os.environ.get("BEFORE", "")
if os.environ.get("ALL") == "true" or not before or set(before) == {"0"}:
    new = now
else:
    try:
        old = subprocess.run(["git", "show", f"{before}:sitemap.xml"], capture_output=True, text=True, check=True).stdout
        new = [u for u in now if u not in set(urls(old))]
    except subprocess.CalledProcessError:
        new = now
if not new:
    print("no new URLs")
    raise SystemExit

# Wait for Cloudflare Pages to finish deploying the key file and the newest page.
for _ in range(40):
    if get(f"https://{HOST}/{KEY}.txt") == 200 and get(new[-1]) == 200:
        break
    time.sleep(15)
else:
    raise SystemExit("site not deployed yet")

body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": new}).encode()
for ep in ENDPOINTS:
    req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(ep, r.status, len(new), "URLs")
    except urllib.error.HTTPError as e:
        print(ep, e.code, e.read()[:300])
