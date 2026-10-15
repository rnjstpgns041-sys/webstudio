// 방문과 전화·문자·메일·상품 선택 버튼 누름을 기록합니다. 쿠키를 쓰지 않습니다.
(function () {
  var ls; try { ls = window.localStorage; if (ls.getItem("ws-owner") === "1") return; } catch (e) {}
  var ss = {}; try { ss = window.sessionStorage; } catch (e) {}
  function get(k) { try { return ss.getItem(k) || ""; } catch (e) { return ""; } }
  function set(k, v) { try { ss.setItem(k, v); } catch (e) {} }
  var path = location.pathname;
  if (!get("ws-landing")) {
    var src = "직접 방문", q = "", r = document.referrer;
    try {
      if (r) {
        var u = new URL(r), h = u.hostname;
        if (h === location.hostname) src = "사이트 안";
        else if (/naver\./.test(h)) src = "네이버";
        else if (/google\./.test(h)) src = "구글";
        else if (/daum\.|kakao/.test(h)) src = "다음·카카오";
        else if (/instagram\./.test(h)) src = "인스타그램";
        else if (/bing\./.test(h)) src = "빙";
        else src = h.replace(/^www\./, "");
        q = u.searchParams.get("query") || u.searchParams.get("q") || "";
      }
    } catch (e) {}
    set("ws-landing", path); set("ws-src", src); set("ws-q", q);
  }
  function send(t, extra) {
    var body = JSON.stringify({ t: t, p: path, l: get("ws-landing"), s: get("ws-src"), q: t === "view" ? get("ws-q") : (extra || "") });
    try {
      if (navigator.sendBeacon && navigator.sendBeacon("/api/t", body)) return;
      fetch("/api/t", { method: "POST", body: body, keepalive: true });
    } catch (e) {}
  }
  window.wsTrack = send;
  send("view");
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a,button");
    if (!a) return;
    var href = a.getAttribute("href") || "";
    if (href.indexOf("tel:") === 0) send("call");
    else if (href.indexOf("sms:") === 0) send("sms");
    else if (href.indexOf("mailto:") === 0) send("mail");
    else if (a.dataset && a.dataset.plan) send("plan", a.dataset.plan);
    else if (a.dataset && a.dataset.copy) send("copy", a.dataset.copy);
    else if (/^https?:/.test(href) && a.hostname !== location.hostname) send("case", a.hostname.replace(/^www\./, ""));
  }, true);
})();
