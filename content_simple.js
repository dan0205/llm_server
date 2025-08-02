// 매우 간단한 테스트 버전
console.log('확장 프로그램 로드됨');

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

// 툴팁 닫기 함수
function closeAllTooltips() {
  var existingTooltip = document.getElementById('jargon-tooltip');
  if (existingTooltip) {
    existingTooltip.remove();
  }
  tooltipShown = false;
}

// 텍스트 선택 감지
document.addEventListener('mouseup', function() {
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
      }
    }
    
    if (foundJargons.length > 0) {
      // 신조어가 발견되면 툴팁 표시
      showJargonTooltip(foundJargons[0]);
    } else {
      // 신조어가 없으면 간단한 알림
      showSimpleNotification('선택된 텍스트: ' + text);
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
function showJargonTooltip(jargon) {
  // 기존 툴팁 제거
  var existingTooltip = document.getElementById('jargon-tooltip');
  if (existingTooltip) {
    existingTooltip.remove();
  }
  
  var tooltip = document.createElement('div');
  tooltip.id = 'jargon-tooltip';
  tooltip.innerHTML = `
    <div class="tooltip-header">
      <h4>${jargon.term}</h4>
      <button class="close-btn">×</button>
    </div>
    <div class="tooltip-content">
      <p><strong>의미:</strong> ${jargon.meaning}</p>
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
    max-width: 300px;
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
  
  document.body.appendChild(tooltip);
  
  // 8초 후 자동 제거 (더 오래 보이도록)
  setTimeout(function() {
    if (tooltip.parentNode) {
      tooltip.remove();
      tooltipShown = false; // 자동 제거 시에도 상태 초기화
    }
  }, 8000);
}

// 간단한 알림 표시
function showSimpleNotification(message) {
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