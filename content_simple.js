// 매우 간단한 테스트 버전
console.log('확장 프로그램 로드됨');

// ===== 스타일 1회 주입 =====
(function injectJargonTipStyles(){
  if (document.getElementById("__jargon_tip_style")) return;
  const s = document.createElement("style");
  s.id="__jargon_tip_style";
  s.textContent = `
  :root {
    --tip-bg: rgba(16,16,20,0.82);
    --tip-fg: #fff;
    --tip-border: rgba(255,255,255,0.12);
    --tip-shadow: 0 18px 50px rgba(0,0,0,.35);
  }
  @media (prefers-color-scheme: light){
    :root {
      --tip-bg: rgba(255,255,255,0.9);
      --tip-fg: #111;
      --tip-border: rgba(0,0,0,0.08);
      --tip-shadow: 0 18px 50px rgba(0,0,0,.15);
    }
  }
  #__jargon_tip {
    position: absolute;
    z-index: 2147483647;
    display: inline-block !important;     /* shrink-to-fit */
    width: auto !important;               /* 고정폭 제거 */
    min-width: 120px !important;
    max-width: 280px !important;          /* 더 컴팩트 */
    box-sizing: border-box;               /* padding 포함 계산 */
    padding: 10px 12px 10px 40px;         /* 아이콘 여백 포함 */
    border-radius: 12px;
    backdrop-filter: saturate(120%) blur(10px);
    -webkit-backdrop-filter: saturate(120%) blur(10px);
    color: var(--tip-fg);
    background: var(--tip-bg);
    border: 1px solid var(--tip-border);
    box-shadow: var(--tip-shadow);
    font: 600 14px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, "Apple SD Gothic Neo", "Noto Sans KR", "Helvetica Neue", Arial, "PingFang SC", "Malgun Gothic", sans-serif;
    letter-spacing: .2px;
    transform-origin: 0 0;
    animation: jt-fade .15s ease-out forwards;
    white-space: normal;
    word-break: keep-all;
  }
  #__jargon_tip[data-state="hidden"]{ display:none; }

  /* 아이콘 */
  #__jargon_tip .jt-icon{
    position:absolute; left:8px; top:8px; width:22px; height:22px; opacity:.9;
    filter: drop-shadow(0 2px 6px rgba(0,0,0,.25));
  }

  /* 텍스트 */
  #__jargon_tip .jt-text{
    margin: 0;
    font-weight: 600;
    line-height: 1.55;
  }

  /* 화살표 */
  #__jargon_tip::after{
    content:"";
    position:absolute;
    left: 14px; top:-6px;
    width:12px; height:12px;
    background: var(--tip-bg);
    border-left: 1px solid var(--tip-border);
    border-top: 1px solid var(--tip-border);
    transform: rotate(45deg);
    box-shadow: -2px -2px 10px rgba(0,0,0,.06);
  }

  @keyframes jt-fade{
    from{ opacity:0; transform: translateY(4px) scale(.98); }
    to  { opacity:1; transform: translateY(0)   scale(1); }
  }
  `;
  document.head.appendChild(s);
})();

// ===== 위치 계산 유틸 =====
let __lastMouse = { x: 0, y: 0 };
document.addEventListener("mousemove", (e) => { __lastMouse = { x:e.clientX, y:e.clientY }; }, true);

function getAnchorPoint() {
  const sel = window.getSelection?.();
  if (sel && sel.rangeCount > 0) {
    try {
      const rect = sel.getRangeAt(0).getBoundingClientRect();
      if (rect && (rect.width || rect.height)) {
        return { x: rect.left + rect.width/2, y: rect.bottom + 10 };
      }
    } catch {}
  }
  return { x: __lastMouse.x, y: __lastMouse.y + 12 };
}

// ===== 메인 표시 함수 =====
function showTooltipMeaningLine(meaningLine) {
  let tip = document.getElementById("__jargon_tip");
  if (!tip) {
    tip = document.createElement("div");
    tip.id = "__jargon_tip";
    tip.innerHTML = `
      <svg class="jt-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path fill="currentColor" d="M12 2a10 10 0 1 0 .001 20.001A10 10 0 0 0 12 2Zm1 15h-2v-6h2v6Zm0-8h-2V7h2v2Z"/>
      </svg>
      <p class="jt-text"></p>
    `;
    document.body.appendChild(tip);
  }

  tip.querySelector(".jt-text").textContent = String(meaningLine || "해석 없음");

  // 위치 및 뷰포트 보정
  const pt = getAnchorPoint();
  const margin = 12;
  const vw = document.documentElement.clientWidth;
  const vh = document.documentElement.clientHeight;

  tip.style.display = "inline-block";
  tip.style.removeProperty("width");          // 혹시 남아있던 width 제거
  tip.style.minWidth = "120px";
  tip.style.maxWidth = "280px";
  tip.dataset.state = "shown";
  tip.style.left = "0px"; tip.style.top = "0px"; // 일단 배치 후 사이즈 측정
  const { width: tw, height: th } = tip.getBoundingClientRect();

  let x = pt.x + window.scrollX;
  let y = pt.y + window.scrollY;

  // 좌우/상하 오버플로우 보정
  if (x + tw + margin > window.scrollX + vw) x = window.scrollX + vw - tw - margin;
  if (x < window.scrollX + margin) x = window.scrollX + margin;

  // 위쪽이 더 공간이 많으면 위로 배치하고 화살표도 이동
  const spaceBelow = (window.scrollY + vh) - y;
  const spaceAbove = (pt.y + window.scrollY) - window.scrollY;
  const arrow =  tip; // after 사용
  if (spaceBelow < th + 24 && spaceAbove > th + 24) {
    y = (pt.y + window.scrollY) - th - 18;
    tip.style.transformOrigin = "bottom left";
    tip.style.animation = "jt-fade .15s ease-out forwards";
    tip.style.setProperty("--arrow-top", "auto");
    tip.style.setProperty("--arrow-bottom", "-6px");
    tip.style.setProperty("--arrow-rotate", "225deg");
    tip.style.setProperty("--arrow-shadow", "2px 2px 10px rgba(0,0,0,.06)");
    tip.style.setProperty("--arrow-y", (th-6)+"px");
    tip.style.setProperty("--arrow-x", "14px");
    tip.style.setProperty("--arrow-display", "block");
    tip.style.removeProperty("--arrow-top");
    // 위 배치일 때 화살표를 아래로 옮기려면 ::after 제어가 필요하지만,
    // 간단히 위아래 모두 보이도록 두되 위치로 자연스레 가리키게 함.
  } else {
    // 기본: 아래 배치
  }

  tip.style.left = `${Math.round(x)}px`;
  tip.style.top  = `${Math.round(y)}px`;
}

// 숨기기(선택)
function hideTooltipMeaningLine() {
  const tip = document.getElementById("__jargon_tip");
  if (tip){ 
    tip.dataset.state="hidden"; 
    tip.style.display="none"; 
  }
}

// 필요하다면 selection clear 시 자동 숨김
document.addEventListener("selectionchange", () => {
  const sel = window.getSelection?.();
  if (!sel || !sel.toString().trim()) hideTooltipMeaningLine();
});

// API 설정
const API_BASE = "http://localhost:8000/api/v1";

// 신조어 데이터
const JARGON_DATA = {
  "갑분싸": "갑자기 분위기가 싸해진다는 뜻",
  "인싸": "인사이더의 줄임말로, 특정 그룹에 속한 사람",
  "아싸": "아웃사이더의 줄임말로, 특정 그룹에 속하지 않은 사람",
  "대박": "엄청나게 좋은 일이 일어났을 때 사용하는 표현",
  "헐": "놀라거나 충격받았을 때 사용하는 감탄사",
  "ㅋㅋ": "웃음을 표현하는 인터넷 용어",
  "ㅎㅎ": "웃음을 표현하는 인터넷 용어",
  "ㅇㅇ": "응응의 줄임말로 동의를 표현",
  "ㄴㄴ": "노노의 줄임말로 부정을 표현"
};

// 중복 방지 변수
let lastSelectedText = '';
let tooltipShown = false;
let lastProcessTime = 0;

function cslog(...a){ console.log("[CS]", ...a); }

// 확장 로드 시 워커가 살아있는지 체크
chrome.runtime.sendMessage({ type: "PING" }, (resp) => {
  if (chrome.runtime.lastError) {
    console.warn("[CS] BG ping error:", chrome.runtime.lastError.message);
  } else {
    console.log("[CS] BG ping resp:", resp);
  }
});

// 주변 문장 추출 함수
function getSurroundingSentence(selectedNode, selectedText) {
  try {
    if (!selectedNode || !selectedNode.parentNode) return "";
    
    let parent = selectedNode.parentNode;
    let text = parent.textContent || "";
    
    // 선택된 텍스트 주변의 문장을 찾기
    let startIndex = text.indexOf(selectedText);
    if (startIndex === -1) return "";
    
    // 문장 시작과 끝 찾기
    let sentenceStart = startIndex;
    let sentenceEnd = startIndex + selectedText.length;
    
    // 앞쪽으로 문장 시작점 찾기
    for (let i = startIndex; i >= 0; i--) {
      if (text[i] === '.' || text[i] === '!' || text[i] === '?' || text[i] === '\n') {
        sentenceStart = i + 1;
        break;
      }
    }
    
    // 뒤쪽으로 문장 끝점 찾기
    for (let i = startIndex + selectedText.length; i < text.length; i++) {
      if (text[i] === '.' || text[i] === '!' || text[i] === '?' || text[i] === '\n') {
        sentenceEnd = i;
        break;
      }
    }
    
    return text.substring(sentenceStart, sentenceEnd).trim();
  } catch (e) {
    console.log('문맥 추출 오류:', e);
    return "";
  }
}

// 백엔드 호출은 반드시 BG를 통해서만
async function fetchJargonFromAPI(term, context) {
  cslog("sendMessage -> BG", { term, context });
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ type: "FETCH_JARGON", term, context }, (resp) => {
      if (chrome.runtime.lastError) {
        return reject(new Error("BG lastError: " + chrome.runtime.lastError.message));
      }
      if (!resp) return reject(new Error("No response from background"));
      if (resp.ok) {
        // 서버는 {"meaning_line":"..."}을 반환
        resolve(resp.data?.meaning_line || resp.meaning_line || "");
      } else {
        reject(new Error(resp.error || "fetch failed"));
      }
    });
  });
}

// 수신 데이터 정규화
function normalizePayload(d) {
  d = d || {};
  return {
    term: d.term || "",
    meaning_line: d.meaning_line || "의미를 찾을 수 없습니다",
    isFromAPI: true // API 결과임을 표시
  };
}

// 툴팁 렌더 전에 한 번 더 가드
function safeShowTooltip(payload) {
  const p = normalizePayload(payload);
  try {
    showJargonTooltip([p]);
  } catch (e) {
    console.error("tooltip render error:", e, p);
    showSimpleNotification(`'${p.term}'에 대한 해석을 가져오지 못했습니다. (${e.message})`);
  }
}

// 툴팁 닫기 함수
function closeAllTooltips() {
  var existingTooltip = document.getElementById('jargon-tooltip');
  if (existingTooltip) {
    existingTooltip.remove();
  }
  
  // 새로운 툴팁도 닫기
  hideTooltipMeaningLine();
  
  tooltipShown = false;
}

// 텍스트 선택 감지
document.addEventListener('mouseup', async function() {
  var text = window.getSelection().toString().trim();
  if (text.length > 0) {
    console.log('선택된 텍스트:', text);
    
    // 시간 기반 중복 방지 (1초 이내 같은 텍스트면 무시)
    var currentTime = Date.now();
    if (text === lastSelectedText && tooltipShown && (currentTime - lastProcessTime) < 1000) {
      return;
    }
    
    lastSelectedText = text;
    lastProcessTime = currentTime;
    tooltipShown = true;
    
    // 신조어 검색
    var foundJargons = [];
    for (var jargon in JARGON_DATA) {
      if (text.includes(jargon)) {
        foundJargons.push({
          term: jargon,
          meaning: JARGON_DATA[jargon]
        });
        // 최대 3개까지만 인식
        if (foundJargons.length >= 3) {
          break;
        }
      }
    }
    
    if (foundJargons.length > 0) {
      // 신조어가 발견되면 툴팁 표시 (여러 개일 경우 모두 표시)
      showJargonTooltip(foundJargons);
    } else {
      // 로컬에 없는 경우 API 호출 시도
      try {
        const selectedNode = window.getSelection().anchorNode;
        const context = getSurroundingSentence(selectedNode, text);
        
        console.log('API 호출 시도:', text, '문맥:', context);
        
        // 로딩 표시
        showSimpleNotification('AI 해석 중... 잠시만 기다려주세요.');
        
        const apiResult = await fetchJargonFromAPI(text, context);
        
        // API 결과로 툴팁 표시
        showTooltipMeaningLine(apiResult);
        
      } catch (error) {
        console.error('API 호출 실패:', error);
        showSimpleNotification(`'${text}'에 대한 해석을 가져오지 못했습니다. (${error.message})`);
      }
    }
  } else {
    // 텍스트 선택이 해제되면 상태 초기화
    setTimeout(function() {
      var currentText = window.getSelection().toString().trim();
      if (!currentText) {
        lastSelectedText = '';
        tooltipShown = false;
      }
    }, 100);
  }
});

// 다른 곳 클릭 시 툴팁 닫기
document.addEventListener('click', function(e) {
  // 툴팁이나 알림창을 클릭한 경우는 무시
  if (e.target.closest('#jargon-tooltip') || 
      e.target.closest('[style*="position: fixed"][style*="z-index: 10002"]')) {
    return;
  }
  
  // 텍스트가 선택되어 있으면 클릭 이벤트 무시 (드래그 후 클릭 방지)
  var selectedText = window.getSelection().toString().trim();
  if (selectedText.length > 0) {
    return;
  }
  
  // 다른 곳을 클릭하면 툴팁 닫기
  closeAllTooltips();
});

// 더블클릭 시 툴팁 닫기
document.addEventListener('dblclick', function(e) {
  // 툴팁이나 알림창을 더블클릭한 경우는 무시
  if (e.target.closest('#jargon-tooltip') || 
      e.target.closest('[style*="position: fixed"][style*="z-index: 10002"]')) {
    return;
  }
  
  // 다른 곳을 더블클릭하면 툴팁 닫기
  closeAllTooltips();
});

// 신조어 툴팁 표시
function showJargonTooltip(jargons) {
  // 기존 툴팁 제거
  var existingTooltip = document.getElementById('jargon-tooltip');
  if (existingTooltip) {
    existingTooltip.remove();
  }
  
  var tooltip = document.createElement('div');
  tooltip.id = 'jargon-tooltip';
  
  // AI 해석 결과를 포함한 더 자세한 툴팁 생성
  var tooltipContent = jargons.map(jargon => {
    let content = `
      <div class="jargon-item">
        <h5 class="term">${jargon.term}</h5>
        <p class="meaning">${jargon.meaning_line}</p>
    `;
    
    // AI 해석 결과인 경우 추가 정보 표시
    if (jargon.isFromAPI) {
      content += '<p class="source">🤖 AI 해석</p>';
      
      // 문맥 분석 정보 표시
      // if (jargon.context_analysis) { // context_analysis 정보가 없으므로 제거
      //   const analysis = jargon.context_analysis;
      //   content += `
      //     <div class="context-analysis">
      //       <p class="analysis-title"><em>문맥 분석:</em></p>
      //       <ul class="analysis-details">
      //         <li>감정: ${analysis.detected_emotion || 'neutral'}</li>
      //         <li>격식: ${analysis.formality_level || 'casual'}</li>
      //         <li>도메인: ${analysis.usage_domain || 'general'}</li>
      //       </ul>
      //     </div>
      //   `;
      // }
      
              // 추가 정보 표시
        // if (jargon.additional_info) { // additional_info 정보가 없으므로 제거
        //   const info = jargon.additional_info;
        //   if (info.synonyms && info.synonyms.length > 0) {
        //     content += `<p class="synonyms"><em>유사한 표현:</em> ${info.synonyms.join(', ')}</p>`;
        //   }
        //   if (info.usage_tips) {
        //     content += `<p class="usage-tips"><em>사용 팁:</em> ${info.usage_tips}</p>`;
        //   }
        //   if (info.origin) {
        //     content += `<p class="origin"><em>어원:</em> ${info.origin}</p>`;
        //   }
        // }
    }
    
    content += '</div>';
    return content;
  }).join('');
  
  tooltip.innerHTML = `
    <div class="tooltip-header">
      <h4>${jargons.length === 1 ? '신조어 해석' : '신조어 목록'}</h4>
      <button class="close-btn">×</button>
    </div>
    <div class="tooltip-content">
      ${tooltipContent}
    </div>
  `;
  
  // 마우스 위치 근처에 표시
  var mouseX = event.clientX;
  var mouseY = event.clientY;
  
  tooltip.style.cssText = `
    position: fixed;
    top: ${mouseY + 10}px;
    left: ${mouseX + 10}px;
    background: white;
    border: 1px solid #ccc;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    z-index: 10001;
    max-width: 400px;
    font-family: Arial, sans-serif;
    font-size: 13px;
    animation: tooltipFadeIn 0.2s ease;
  `;
  
  // 애니메이션 스타일 추가
  var style = document.createElement('style');
  style.textContent = `
    @keyframes tooltipFadeIn {
      from { opacity: 0; transform: scale(0.9); }
      to { opacity: 1; transform: scale(1); }
    }
  `;
  document.head.appendChild(style);
  
  // 헤더 스타일
  var header = tooltip.querySelector('.tooltip-header');
  header.style.cssText = `
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    border-bottom: 1px solid #eee;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 8px 8px 0 0;
  `;
  
  // 닫기 버튼
  var closeBtn = tooltip.querySelector('.close-btn');
  closeBtn.style.cssText = `
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    color: white;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background-color 0.2s ease;
  `;
  
  closeBtn.addEventListener('mouseenter', function() {
    closeBtn.style.backgroundColor = 'rgba(255,255,255,0.2)';
  });
  
  closeBtn.addEventListener('mouseleave', function() {
    closeBtn.style.backgroundColor = 'transparent';
  });
  
  closeBtn.addEventListener('click', function() {
    closeAllTooltips();
  });
  
  // 내용 스타일
  var content = tooltip.querySelector('.tooltip-content');
  content.style.cssText = `
    padding: 12px;
    line-height: 1.4;
  `;
  
  // jargon-item 스타일 추가
  var jargonItems = tooltip.querySelectorAll('.jargon-item');
  jargonItems.forEach(function(item) {
    item.style.cssText = `
      margin-bottom: 16px;
      padding: 12px;
      border: 1px solid #eee;
      border-radius: 6px;
      background: #f9f9f9;
    `;
    
    // term 스타일
    var term = item.querySelector('.term');
    if (term) {
      term.style.cssText = `
        margin: 0 0 8px 0;
        color: #333;
        font-size: 16px;
        font-weight: bold;
      `;
    }
    
    // meaning 스타일
    var meaning = item.querySelector('.meaning');
    if (meaning) {
      meaning.style.cssText = `
        margin: 0 0 8px 0;
        color: #555;
        font-size: 14px;
      `;
    }
    
    // example 스타일
    var example = item.querySelector('.example');
    if (example) {
      example.style.cssText = `
        margin: 0 0 8px 0;
        color: #666;
        font-size: 13px;
        font-style: italic;
      `;
    }
    
    // source 스타일
    var source = item.querySelector('.source');
    if (source) {
      source.style.cssText = `
        margin: 0 0 8px 0;
        color: #007acc;
        font-size: 12px;
        font-weight: bold;
      `;
    }
    
    // context-analysis 스타일
    var contextAnalysis = item.querySelector('.context-analysis');
    if (contextAnalysis) {
      contextAnalysis.style.cssText = `
        margin: 8px 0;
        padding: 8px;
        background: #f0f8ff;
        border-radius: 4px;
        border-left: 3px solid #007acc;
      `;
      
      var analysisTitle = contextAnalysis.querySelector('.analysis-title');
      if (analysisTitle) {
        analysisTitle.style.cssText = `
          margin: 0 0 6px 0;
          font-weight: bold;
          color: #007acc;
        `;
      }
      
      var analysisDetails = contextAnalysis.querySelector('.analysis-details');
      if (analysisDetails) {
        analysisDetails.style.cssText = `
          margin: 0;
          padding-left: 16px;
          color: #555;
        `;
      }
    }
    
    // synonyms, usage-tips, origin 스타일
    var additionalElements = item.querySelectorAll('.synonyms, .usage-tips, .origin');
    additionalElements.forEach(function(element) {
      element.style.cssText = `
        margin: 4px 0;
        color: #666;
        font-size: 12px;
      `;
    });
  });
  
  document.body.appendChild(tooltip);
  
  // 10초 후 자동 제거 (더 오래 보이도록)
  setTimeout(function() {
    if (tooltip.parentNode) {
      tooltip.remove();
      tooltipShown = false; // 자동 제거 시에도 상태 초기화
    }
  }, 10000);
}

// 간단한 알림 표시
function showSimpleNotification(message) {
  // 기존 알림 제거
  var existingNotifications = document.querySelectorAll('[style*="position: fixed"][style*="z-index: 10002"]');
  existingNotifications.forEach(function(notification) {
    notification.remove();
  });
  
  var notification = document.createElement('div');
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #333;
    color: white;
    padding: 12px 16px;
    border-radius: 8px;
    z-index: 10002;
    font-family: Arial, sans-serif;
    font-size: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    animation: notificationSlideIn 0.3s ease;
  `;
  
  // 애니메이션 스타일 추가
  var style = document.createElement('style');
  style.textContent = `
    @keyframes notificationSlideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  `;
  document.head.appendChild(style);
  
  document.body.appendChild(notification);
  
  setTimeout(function() {
    notification.remove();
  }, 3000);
} 