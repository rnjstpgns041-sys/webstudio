"""Send new or changed sitemap URLs to IndexNow (Naver, Bing). Run by .github/workflows/indexnow.yml.
tools/daily_index.py also uses submit() for the daily 08:00 batch."""
import glob, json, os, re, subprocess, time, urllib.request

HOST = "webstudio-4e9.pages.dev"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = next(os.path.basename(f)[:-4] for f in glob.glob(os.path.join(ROOT, "*.txt"))
           if re.fullmatch(r"[0-9a-f]{32}\.txt", os.path.basename(f)))
ENDPOINTS = ["https://searchadvisor.naver.com/indexnow", "https://api.indexnow.org/indexnow"]
UA = {"User-Agent": "Mozilla/5.0 (compatible; webstudio-indexnow/1.0)"}


def urls(xml):
    return re.findall(r"<loc>([^<]+)</loc>", xml)


def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return repr(e)


def wait_deployed(url):
    """Wait for Cloudflare Pages to serve the key file and the given page."""
    for _ in range(40):
        status = get(f"https://{HOST}/{KEY}.txt"), get(url)
        print("deploy check", status)
        if status == (200, 200):
            return
        time.sleep(15)
    raise SystemExit("site not deployed yet")


def submit(url_list):
    """Send URLs to every endpoint. Returns {endpoint: status}."""
    body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": url_list}).encode()
    result = {}
    for ep in ENDPOINTS:
        req = urllib.request.Request(ep, data=body, headers={**UA, "Content-Type": "application/json; charset=utf-8"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                result[ep] = r.status
        except urllib.error.HTTPError as e:
            result[ep] = f"{e.code} {e.read()[:300]!r}"
        except Exception as e:
            result[ep] = repr(e)
        print(ep, result[ep], len(url_list), "URLs")
    return result


def main():
    now = urls(open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read())
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
        return
    wait_deployed(new[-1])
    submit(new)


if __name__ == "__main__":
    main()
