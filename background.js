// background.js (확장 루트에 존재해야 함)
function log(...a){ console.log("[BG]", ...a); }

self.addEventListener("install", () => log("SW install"));
self.addEventListener("activate", (e) => { log("SW activate"); e.waitUntil(self.clients.claim()); });

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  log("onMessage", msg?.type, "from", sender?.origin || sender?.url);

  if (msg?.type === "PING") {
    sendResponse({ ok: true, pong: true });
    return; // sync 응답
  }

  if (msg?.type !== "FETCH_JARGON") return;

  (async () => {
    try {
      const API_BASE = "http://127.0.0.1:8000/api/v1"; // 127로 고정
      const url = `${API_BASE}/jargons/interpret/${encodeURIComponent(msg.term)}?context=${encodeURIComponent(msg.context || "")}`;

      log("fetch start", url);
      const controller = new AbortController();
      const t = setTimeout(() => controller.abort(), 10000);

      const res = await fetch(url, { method: "GET", signal: controller.signal });
      clearTimeout(t);

      log("fetch done", res.status);
      if (!res.ok) throw new Error(`API ${res.status}`);

      const data = await res.json();
      sendResponse({ ok: true, data });
    } catch (e) {
      log("fetch error", String(e));
      try { sendResponse({ ok: false, error: String(e) }); } catch {}
    }
  })();

  return true; // ★ async sendResponse 유지
});
