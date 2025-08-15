// background.js (확장 루트에 존재해야 함)
function log(...a){ console.log("[BG]", ...a); }

self.addEventListener("install", () => log("SW install"));
self.addEventListener("activate", (e) => { log("SW activate"); e.waitUntil(self.clients.claim()); });

// ===== 로컬 캐시 시스템 =====
function keyOf(term, context) {
  const h = context ? new TextEncoder().encode(context) : new Uint8Array();
  // 간단 해시 (md5 대신 빠른 해시)
  let hash = 0; 
  for (let b of h) {
    hash = ((hash << 5) - hash) + b; 
    hash |= 0;
  }
  const ctx8 = (hash >>> 0).toString(16).slice(0, 8);
  return `${term}::${context ? ctx8 : "noctx"}`;
}

// ===== 로컬 사전 시스템 =====
async function loadLocalDictOnce() {
  const { "__jargon_local_dict": exists } = await chrome.storage.local.get("__jargon_local_dict");
  if (exists) return;
  
  try {
    const res = await fetch(chrome.runtime.getURL("assets/slang_30.json"));
    const arr = await res.json();
    // term → meaning_line 빠른 조회용 맵
    const dict = {};
    for (const it of arr) dict[it.term] = it.meaning_line;
    await chrome.storage.local.set({ 
      "__jargon_local_dict": dict, 
      "__jargon_local_dict_version": "v1" 
    });
    log("local dict loaded", Object.keys(dict).length, "terms");
  } catch (e) { 
    console.warn("local dict load failed", e); 
  }
}

// 서비스워커 시작 시 1회 로드
loadLocalDictOnce();

async function cacheGet(term, context) {
  const k = keyOf(term, context);
  const res = await chrome.storage.local.get(k);
  let e = res[k];
  if (!e) return null;
  
  // TTL 체크
  if (e.ttl && Date.now() - e.ts > e.ttl * 1000) {
    await chrome.storage.local.remove(k);
    return null;
  }
  return e; // { line, ts, host?, ttl? }
}

async function cacheSet(term, context, entry) {
  const k = keyOf(term, context);
  await chrome.storage.local.set({ [k]: entry });
  
  // 모든 탭에 신규 데이터 전파
  const tabs = await chrome.tabs.query({});
  for (const t of tabs) {
    try { 
      chrome.tabs.sendMessage(t.id, { type: "JARGON_CACHE_UPDATED", key: k, entry }); 
    } catch {}
  }
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  log("onMessage", msg?.type, "from", sender?.origin || sender?.url);

  if (msg?.type === "PING") {
    sendResponse({ ok: true, pong: true });
    return; // sync 응답
  }

  if (msg?.type !== "FETCH_JARGON") return;

  (async () => {
    try {
      // 1. 로컬 캐시 먼저 확인
      const cached = await cacheGet(msg.term, msg.context);
      if (cached) {
        log("cache hit", cached);
        sendResponse({ ok: true, data: { meaning_line: cached.line }, fromCache: true });
        return;
      }

      // 2. API 호출
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
      
      // 3. 성공한 결과를 로컬 캐시에 저장 (TTL: 7일)
      if (data.meaning_line && !data.meaning_line.includes("정확한 해석을 찾지 못했습니다")) {
        const entry = {
          line: data.meaning_line,
          ts: Date.now(),
          ttl: 7 * 24 * 60 * 60, // 7일
          host: new URL(url).hostname
        };
        await cacheSet(msg.term, msg.context, entry);
        log("cache set", entry);
      }

      sendResponse({ ok: true, data, fromCache: false });
    } catch (e) {
      log("fetch error", String(e));
      try { sendResponse({ ok: false, error: String(e) }); } catch {}
    }
  })();

  return true; // ★ async sendResponse 유지
});

// ===== 사이트 무관 강제 안전망 =====
chrome.webNavigation.onHistoryStateUpdated.addListener(({tabId}) => {
  try { 
    chrome.tabs.sendMessage(tabId, { type: "CLEAR_TIP" }); 
    log("CLEAR_TIP sent to tab", tabId, "onHistoryStateUpdated");
  } catch (e) {
    log("CLEAR_TIP failed for tab", tabId, e);
  }
}, { url: [{ schemes: ["http","https"] }] });

chrome.webNavigation.onCommitted.addListener(({tabId}) => {
  try { 
    chrome.tabs.sendMessage(tabId, { type: "CLEAR_TIP" }); 
    log("CLEAR_TIP sent to tab", tabId, "onCommitted");
  } catch (e) {
    log("CLEAR_TIP failed for tab", tabId, e);
  }
}, { url: [{ schemes: ["http","https"] }] });
