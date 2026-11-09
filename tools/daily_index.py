"""매일 오전 8시(한국 시간) 문의로 이어질 만한 페이지 30개를 네이버·빙(IndexNow)에 보낸다.
.github/workflows/daily-index.yml이 실행한다. 직접 확인: python3 tools/daily_index.py --dry-run

하루 30개 = 상담 직결 페이지 10 + 지역 페이지 10 + 업종 페이지 10.
세 묶음이 각자 날마다 다음 10개로 넘어가므로 같은 주소를 매일 반복해 보내지 않는다.
"""
import datetime, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pages_data import PAGES
from indexnow import HOST, submit, wait_deployed

PER_GROUP = 10

# 홈페이지를 '맡기려는' 사람이 찾는 말. 위에 있을수록 먼저 보낸다.
CORE = [
    "homepage-cost", "website-making-company", "homepage-agency-recommend", "store-homepage-making",
    "sosanggongin-homepage", "homepage-quote", "homepage-300k", "homepage-outsourcing", "homepage-freelancer",
    "choose-homepage-agency", "cheap-homepage-caution", "no-monthly-fee-homepage", "one-page-homepage",
    "solo-business-homepage", "sole-proprietor-homepage", "company-homepage", "how-to-make-homepage",
    "homepage-renewal", "old-homepage-problems", "homepage-migration", "homepage-maintenance",
    "homepage-maintenance-cost", "homepage-management-agency", "edit-homepage-myself", "homepage-timeline",
    "homepage-production-period", "homepage-portfolio-cases", "homepage-design-examples", "landing-page",
    "more-phone-calls", "no-inquiries-reasons", "homepage-search-exposure", "naver-top-exposure",
    "naver-search-homepage", "local-search-homepage", "naver-place-homepage", "naver-modoo-alternative",
    "imweb-wix-vs-custom", "template-vs-custom", "website-builder-vs-custom", "diy-vs-outsource-homepage",
    "freelancer-vs-agency-homepage", "homepage-contract-check", "free-homepage", "responsive-homepage",
    "mobile-homepage", "homepage-in-ai-era", "geo-optimization", "naver-ai-briefing",
    "chatgpt-store-recommendation", "ai-search-exposure", "google-ai-overview", "new-store-homepage",
    "startup-homepage", "professional-homepage", "brand-homepage", "blog-to-homepage", "personal-homepage",
    "questions-before-homepage", "trustworthy-homepage", "who-needs-homepage",
]

REGIONS = [
    "seoul", "busan", "incheon", "daegu", "daejeon", "gwangju", "ulsan", "sejong", "suwon", "seongnam-bundang",
    "goyang-ilsan", "yongin", "hwaseong-dongtan", "bucheon", "ansan", "anyang", "pyeongtaek", "uijeongbu",
    "paju", "gimpo", "namyangju", "hanam", "siheung-gwangmyeong", "cheongju", "cheonan-asan", "jeonju",
    "changwon", "gimhae", "pohang", "gumi", "gyeongju", "jinju", "mokpo", "suncheon-yeosu", "jeju", "gangwon",
]
REGIONS = [r + "-homepage" for r in REGIONS]

# 이름은 'OO-homepage'지만 업종이 아닌 비교·도구 글
NOT_TRADE = {
    "blog-vs-homepage", "flyer-vs-homepage", "smartstore-vs-homepage", "app-vs-homepage", "delivery-app-vs-homepage",
    "google-search-homepage", "instagram-homepage", "kakao-channel-homepage", "wordpress-homepage", "notion-homepage",
    "ai-homepage", "contact-form-homepage", "holiday-season-homepage", "english-homepage", "multi-branch-homepage",
}


def groups():
    slugs = [p["slug"] for p in PAGES]
    have = set(slugs)
    core = [s for s in CORE if s in have]
    regions = [s for s in REGIONS if s in have]
    taken = set(core) | set(regions)
    # 업종 페이지: 'OO 홈페이지'로 끝나는 나머지 (홍보 요령·용어 설명 글은 문의 의도가 약해 뺀다)
    trades = [s for s in slugs if s.endswith("-homepage") and s not in taken | NOT_TRADE]
    return core, regions, trades


def pick(pool, day):
    start = (day * PER_GROUP) % len(pool)
    return [pool[(start + i) % len(pool)] for i in range(min(PER_GROUP, len(pool)))]


def main():
    today = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).date()  # 한국 날짜
    day = (today - datetime.date(2026, 11, 10)).days
    core, regions, trades = groups()
    chosen = pick(core, day) + pick(regions, day) + pick(trades, day)
    url_list = [f"https://{HOST}/{s}/" for s in chosen]
    print(f"{today} (day {day}): core {len(core)}, regions {len(regions)}, trades {len(trades)} -> {len(url_list)} URLs")
    for u in url_list:
        print(" ", u)
    if "--dry-run" in sys.argv:
        return
    wait_deployed(url_list[0])
    result = submit(url_list)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"### {today} 색인 요청 {len(url_list)}개\n\n")
            f.writelines(f"- {ep}: {st}\n" for ep, st in result.items())
            f.write("\n" + "".join(f"- {u}\n" for u in url_list))
    if not any(str(st).startswith("20") for st in result.values()):
        raise SystemExit("no endpoint accepted the URLs")


if __name__ == "__main__":
    main()
