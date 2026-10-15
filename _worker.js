// 운영자 전용 통계: 방문·문의 버튼 기록(/api/t)과 요약(/api/stats). 나머지 요청은 정적 파일로 넘깁니다.
// D1 바인딩 이름 DB, 비밀번호 비밀값 STATS_KEY 가 필요합니다.
async function ensure(db) {
  await db.prepare(`CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL, day TEXT NOT NULL, type TEXT NOT NULL,
    path TEXT, landing TEXT, src TEXT, q TEXT, dev TEXT)`).run();
  await db.prepare("CREATE INDEX IF NOT EXISTS events_day ON events(day)").run();
}

// view 방문, call 전화, sms 문자, mail 메일, form 문의 양식 보내기, plan 가격표 상품 선택, copy 연락처 복사, case 작업 사례 열기
const TYPES = new Set(["view", "call", "sms", "mail", "form", "plan", "copy", "case"]);
const cut = (v, n) => (typeof v === "string" ? v.slice(0, n) : "");

async function track(request, env) {
  if (!env.DB) return new Response(null, { status: 204 });
  let b;
  try { b = JSON.parse(await request.text()); } catch { return new Response(null, { status: 400 }); }
  if (!b || !TYPES.has(b.t)) return new Response(null, { status: 400 });
  const ua = request.headers.get("user-agent") || "";
  if (/bot|crawl|spider|yeti|daum|preview/i.test(ua)) return new Response(null, { status: 204 });
  const dev = /mobi|android|iphone/i.test(ua) ? "모바일" : "PC";
  const now = Date.now();
  const day = new Date(now + 9 * 3600e3).toISOString().slice(0, 10); // 한국 날짜
  await ensure(env.DB);
  await env.DB.prepare("INSERT INTO events (ts,day,type,path,landing,src,q,dev) VALUES (?,?,?,?,?,?,?,?)")
    .bind(now, day, b.t, cut(b.p, 200), cut(b.l, 200), cut(b.s, 40), cut(b.q, 100), dev).run();
  return new Response(null, { status: 204 });
}

const json = (o, status = 200) => new Response(JSON.stringify(o), {
  status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

async function stats(request, env) {
  if (!env.DB || !env.STATS_KEY) return json({ error: "setup" }, 503);
  if (request.headers.get("x-stats-key") !== env.STATS_KEY) return json({ error: "key" }, 401);
  const days = Math.min(Math.max(parseInt(new URL(request.url).searchParams.get("days") || "30", 10) || 30, 1), 3650);
  const from = new Date(Date.now() + 9 * 3600e3 - (days - 1) * 864e5).toISOString().slice(0, 10);
  await ensure(env.DB);
  const q = (sql) => env.DB.prepare(sql).bind(from).all().then((r) => r.results);
  const sum = `SUM(type='view') v, SUM(type='call') c, SUM(type IN ('sms','mail','form')) s, SUM(type='plan') pl, SUM(type='copy') cp`;
  const [total, daily, pages, sources, queries, devices, plans, cases] = await Promise.all([
    q(`SELECT ${sum} FROM events WHERE day>=?`),
    q(`SELECT day, ${sum} FROM events WHERE day>=? GROUP BY day ORDER BY day`),
    q(`SELECT landing, ${sum} FROM events WHERE day>=? AND landing<>'' GROUP BY landing ORDER BY v DESC, c DESC LIMIT 200`),
    q(`SELECT src, ${sum} FROM events WHERE day>=? GROUP BY src ORDER BY v DESC`),
    q(`SELECT q, src, COUNT(*) v FROM events WHERE day>=? AND type='view' AND q<>'' GROUP BY q, src ORDER BY v DESC LIMIT 100`),
    q(`SELECT dev, ${sum} FROM events WHERE day>=? GROUP BY dev`),
    q(`SELECT q, COUNT(*) n FROM events WHERE day>=? AND type='plan' GROUP BY q ORDER BY n DESC`),
    q(`SELECT q, COUNT(*) n FROM events WHERE day>=? AND type='case' GROUP BY q ORDER BY n DESC`),
  ]);
  return json({ from, days, total: total[0], daily, pages, sources, queries, devices, plans, cases });
}

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);
    if (pathname === "/api/t" && request.method === "POST") return track(request, env);
    if (pathname === "/api/stats" && request.method === "GET") return stats(request, env);
    return env.ASSETS.fetch(request);
  },
};
