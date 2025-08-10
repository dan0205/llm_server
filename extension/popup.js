document.addEventListener('DOMContentLoaded', function() {
  const statusDiv = document.getElementById('status');
  const toggleBtn = document.getElementById('toggleBtn');
  
  // 현재 상태 확인
  chrome.storage.local.get(['isActive'], function(result) {
    const isActive = result.isActive || false;
    updateUI(isActive);
  });
  
  // 토글 버튼 클릭 이벤트
  toggleBtn.addEventListener('click', function() {
    chrome.storage.local.get(['isActive'], function(result) {
      const newState = !(result.isActive || false);
      
      // 상태 저장
      chrome.storage.local.set({isActive: newState}, function() {
        updateUI(newState);
        
        // content script에 상태 전달
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
          chrome.tabs.sendMessage(tabs[0].id, {
            action: 'toggle',
            isActive: newState
          });
        });
      });
    });
  });
  
  function updateUI(isActive) {
    if (isActive) {
      statusDiv.textContent = '활성화됨';
      statusDiv.className = 'status active';
      toggleBtn.textContent = '비활성화';
    } else {
      statusDiv.textContent = '비활성화됨';
      statusDiv.className = 'status inactive';
      toggleBtn.textContent = '활성화';
    }
  }
}); 