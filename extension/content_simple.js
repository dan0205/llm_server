// API 서버 URL (로컬 개발용)
const API_BASE_URL = 'http://localhost:8001/api';

// 신조어 감지 및 처리
class JargonDetector {
  constructor() {
    this.isActive = false;
    this.jargonWords = [
      '갓생', '갓생', '갓생', '갓생', '갓생'
    ];
    this.init();
  }

  init() {
    // 저장된 상태 확인
    chrome.storage.local.get(['isActive'], (result) => {
      this.isActive = result.isActive || false;
      if (this.isActive) {
        this.startDetection();
      }
    });

    // 메시지 리스너 등록
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.action === 'toggle') {
        this.isActive = request.isActive;
        if (this.isActive) {
          this.startDetection();
        } else {
          this.stopDetection();
        }
      }
    });
  }

  startDetection() {
    console.log('신조어 감지 시작');
    console.log('현재 페이지 텍스트:', document.body.textContent.substring(0, 200));
    this.highlightJargons();
    this.addClickListeners();
  }

  stopDetection() {
    console.log('신조어 감지 중지');
    this.removeHighlights();
  }

  highlightJargons() {
    console.log('하이라이트 시작');
    console.log('찾을 신조어들:', this.jargonWords);
    
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      null,
      false
    );

    const textNodes = [];
    let node;
    while (node = walker.nextNode()) {
      textNodes.push(node);
    }

    console.log('찾은 텍스트 노드 수:', textNodes.length);

    textNodes.forEach((textNode, index) => {
      const text = textNode.textContent;
      this.jargonWords.forEach(jargon => {
        if (text.includes(jargon)) {
          console.log(`노드 ${index}에서 '${jargon}' 발견:`, text.substring(0, 100));
          this.highlightText(textNode, jargon);
        }
      });
    });
  }

  highlightText(textNode, jargon) {
    const text = textNode.textContent;
    const regex = new RegExp(`(${jargon})`, 'gi');
    
    if (regex.test(text)) {
      const span = document.createElement('span');
      span.innerHTML = text.replace(regex, '<span class="jargon-highlight" data-jargon="$1">$1</span>');
      textNode.parentNode.replaceChild(span, textNode);
    }
  }

  addClickListeners() {
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('jargon-highlight')) {
        const jargon = e.target.dataset.jargon;
        this.showJargonInfo(jargon, e);
      }
    });
  }

  async showJargonInfo(jargon, event) {
    try {
      console.log('신조어 클릭됨:', jargon);
      
      // 로딩 표시
      this.showLoading(event);
      
      // API 호출
      const url = `${API_BASE_URL}/v1/jargon/${encodeURIComponent(jargon)}`;
      console.log('API 호출 URL:', url);
      
      const response = await fetch(url);
      console.log('API 응답 상태:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('API 응답 데이터:', data);
        this.showTooltip(data, event);
      } else {
        throw new Error(`API 호출 실패: ${response.status}`);
      }
    } catch (error) {
      console.error('신조어 정보 조회 실패:', error);
      this.showError(event);
    }
  }

  showLoading(event) {
    const tooltip = document.createElement('div');
    tooltip.className = 'jargon-tooltip loading';
    tooltip.innerHTML = '분석 중...';
    tooltip.style.cssText = `
      position: absolute;
      background: #333;
      color: white;
      padding: 10px;
      border-radius: 5px;
      z-index: 10000;
      font-size: 14px;
      max-width: 300px;
      left: ${event.pageX + 10}px;
      top: ${event.pageY + 10}px;
    `;
    
    document.body.appendChild(tooltip);
    
    // 3초 후 자동 제거
    setTimeout(() => {
      if (tooltip.parentNode) {
        tooltip.parentNode.removeChild(tooltip);
      }
    }, 3000);
  }

  showTooltip(data, event) {
    // 기존 툴팁 제거
    const existingTooltip = document.querySelector('.jargon-tooltip');
    if (existingTooltip) {
      existingTooltip.parentNode.removeChild(existingTooltip);
    }

    const tooltip = document.createElement('div');
    tooltip.className = 'jargon-tooltip';
    tooltip.innerHTML = `
      <div style="font-weight: bold; margin-bottom: 8px;">${data.word}</div>
      <div style="margin-bottom: 8px;">${data.explanation}</div>
      <div style="font-size: 12px; color: #ccc;">출처: ${data.source || '알 수 없음'}</div>
      <div style="font-size: 12px; color: #ccc; margin-top: 5px;">검색 횟수: ${data.search_count}</div>
    `;
    
    tooltip.style.cssText = `
      position: absolute;
      background: #333;
      color: white;
      padding: 15px;
      border-radius: 8px;
      z-index: 10000;
      font-size: 14px;
      max-width: 300px;
      left: ${event.pageX + 10}px;
      top: ${event.pageY + 10}px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    
    document.body.appendChild(tooltip);
    
    // 클릭 시 툴팁 제거
    document.addEventListener('click', function removeTooltip(e) {
      if (!tooltip.contains(e.target)) {
        if (tooltip.parentNode) {
          tooltip.parentNode.removeChild(tooltip);
        }
        document.removeEventListener('click', removeTooltip);
      }
    });
  }

  showError(event) {
    const tooltip = document.createElement('div');
    tooltip.className = 'jargon-tooltip error';
    tooltip.innerHTML = '정보를 불러올 수 없습니다.';
    tooltip.style.cssText = `
      position: absolute;
      background: #dc3545;
      color: white;
      padding: 10px;
      border-radius: 5px;
      z-index: 10000;
      font-size: 14px;
      left: ${event.pageX + 10}px;
      top: ${event.pageY + 10}px;
    `;
    
    document.body.appendChild(tooltip);
    
    setTimeout(() => {
      if (tooltip.parentNode) {
        tooltip.parentNode.removeChild(tooltip);
      }
    }, 2000);
  }

  removeHighlights() {
    const highlights = document.querySelectorAll('.jargon-highlight');
    highlights.forEach(highlight => {
      const parent = highlight.parentNode;
      if (parent) {
        parent.replaceWith(highlight.textContent);
      }
    });
  }
}

// 스타일 추가
const style = document.createElement('style');
style.textContent = `
  .jargon-highlight {
    background-color: #ffeb3b;
    cursor: pointer;
    border-radius: 3px;
    padding: 1px 2px;
  }
  
  .jargon-highlight:hover {
    background-color: #ffc107;
  }
`;
document.head.appendChild(style);

// 디버깅용 로그
console.log('Content script 로드됨');

// 신조어 감지기 초기화
new JargonDetector(); 