# 사용법: python3 tools/gen_pages.py  (저장소 루트에서)
# tools/pages_data.py의 PAGES로 /<slug>/index.html, sitemap.xml, 메인의 안내 목록을 만든다.
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from pages_data import PAGES, CASES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://webstudio-4e9.pages.dev"
SITE = "웹 스튜디오"
PHONE = "010-3406-4060"
TEL = "01034064060"
EMAIL = "rnjstpgns0411@naver.com"
LASTMOD = "2026-10-20"
NAVER_TAG = '<meta name="naver-site-verification" content="143886b928e8811ee874b6e0498388b83ea62daa">'
ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%232350F0'/%3E"
        "%3Ctext x='16' y='22' font-size='16' font-weight='700' text-anchor='middle' fill='white' font-family='sans-serif'%3EW%3C/text%3E%3C/svg%3E")

e = html.escape


def body(blocks):
    out = []
    for b in blocks:
        if isinstance(b, list):
            out.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in b) + "</ul>")
        else:
            out.append(f"<p>{e(b)}</p>")
    return "\n".join(out)


def case_cards(keys):
    cards = []
    for k in keys:
        name, url, kind, feats = CASES[k]
        cards.append(
            f'<a class="case" href="{url}" target="_blank" rel="noopener">'
            f'<img src="/img/{k}.webp" alt="{e(name)} 홈페이지 첫 화면" width="960" height="600" loading="lazy">'
            f'<span class="kind">{e(kind)}</span><b>{e(name)} <i>사이트 보기 ↗</i></b><span class="f">{e(feats)}</span></a>')
    return "\n".join(cards)


def page(p):
    kw, slug = p["kw"], p["slug"]
    url = f"{BASE}/{slug}/"
    title = f"{kw} | {SITE}"
    desc = f"{p['lede']} 상담 {PHONE}."
    if len(desc) > 150:
        desc = p["lede"][:140].rstrip() + "…"
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}
    svc_ld = {"@context": "https://schema.org", "@type": "Service", "name": kw, "serviceType": "홈페이지 제작",
              "provider": {"@type": "Organization", "name": SITE, "url": BASE + "/", "telephone": PHONE, "email": EMAIL},
              "areaServed": "KR", "url": url}
    sections = "\n".join(f"<h2>{e(h)}</h2>\n{body(b)}" for h, b in p["sections"])
    faq = "\n".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in p["faq"])
    others = "\n".join(f'<li><a href="/{o["slug"]}/">{e(o["kw"])}</a></li>' for o in PAGES if o["slug"] != slug)
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{NAVER_TAG}
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="keywords" content="{e(kw)}, 홈페이지 제작, 소상공인 홈페이지, {SITE}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/img/{p['cases'][0]}.webp">
<meta property="og:site_name" content="{SITE}">
<meta property="og:locale" content="ko_KR">
<meta name="theme-color" content="#2350F0">
<link rel="icon" href="{ICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap">
<link rel="stylesheet" href="/css/sub.css">
<script type="application/ld+json">{json.dumps(svc_ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>
</head>
<body>
<header class="bar"><div class="wrap">
  <a class="brand" href="/"><span>W</span>{SITE}</a>
  <a class="btn sm" href="/#contact">제작 문의</a>
</div></header>
<main class="wrap">
  <nav class="crumb" aria-label="현재 위치"><a href="/">홈</a> › <a href="/#guides">제작 안내</a> › {e(kw)}</nav>
  <header class="head">
    <span class="tag">제작 안내</span>
    <h1>{e(kw)}</h1>
    <p class="lede">{e(p['lede'])}</p>
  </header>
  <article>
{sections}
  </article>
  <section class="cases" aria-labelledby="c-h">
    <h2 id="c-h">직접 만든 작업 사례</h2>
    <div class="grid">
{case_cards(p['cases'])}
    </div>
  </section>
  <section class="faq" aria-labelledby="f-h">
    <h2 id="f-h">자주 묻는 질문</h2>
{faq}
  </section>
  <section class="cta">
    <h2>{e(kw)}, 상담부터 받아 보세요</h2>
    <p>업종과 지금 쓰는 블로그·SNS 주소만 알려 주시면 맞는 구성을 제안해 드립니다. 상담은 무료입니다.</p>
    <div class="btns">
      <a class="btn" href="tel:{TEL}">전화 {PHONE}</a>
      <a class="btn line" href="sms:{TEL}">문자 보내기</a>
      <a class="btn line" href="mailto:{EMAIL}?subject={e('홈페이지 제작 문의')}">메일 보내기</a>
    </div>
  </section>
  <nav class="more" aria-labelledby="m-h">
    <h2 id="m-h">다른 제작 안내</h2>
    <ul>
{others}
    </ul>
  </nav>
</main>
<footer class="wrap foot"><a href="/">{SITE}</a> · 소상공인·1인 사업자 홈페이지 제작 · <a href="tel:{TEL}">{PHONE}</a></footer>
<script src="/js/track.js" defer></script>
</body>
</html>
"""


def main():
    for p in PAGES:
        d = os.path.join(ROOT, p["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write(page(p))
    urls = [BASE + "/"] + [f"{BASE}/{p['slug']}/" for p in PAGES]
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        f.writelines(f"  <url><loc>{u}</loc><lastmod>{LASTMOD}</lastmod></url>\n" for u in urls)
        f.write("</urlset>\n")
    # 통계 화면에서 주소 대신 페이지 이름을 보여 주는 표
    names = {"/": "메인 페이지"}
    names.update({f"/{p['slug']}/": p["kw"] for p in PAGES})
    os.makedirs(os.path.join(ROOT, "stats"), exist_ok=True)
    with open(os.path.join(ROOT, "stats", "pages.json"), "w") as f:
        json.dump(names, f, ensure_ascii=False, indent=0)
    # 메인 페이지 안내 목록 갱신 (<!--guides--> ... <!--/guides--> 사이)
    idx = os.path.join(ROOT, "index.html")
    s = open(idx).read()
    items = "\n".join(f'          <li><a href="/{p["slug"]}/">{e(p["kw"])}</a></li>' for p in PAGES)
    s, n = re.subn(r"<!--guides-->.*?<!--/guides-->", "<!--guides-->\n" + items + "\n          <!--/guides-->", s, flags=re.S)
    assert n == 1, "index.html에 <!--guides--> 표시가 없습니다"
    open(idx, "w").write(s)
    print(f"{len(PAGES)} pages, {len(urls)} urls")


if __name__ == "__main__":
    main()
