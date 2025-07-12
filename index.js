const express = require('express');
const app = express();
const path = require('path');

// 정적 파일 제공 (예: index.html, CSS, JS 등)
app.use(express.static(__dirname));

// 기본 라우트 처리
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Railway는 자체적으로 포트를 지정하므로 반드시 환경 변수 사용
const PORT = process.env.PORT;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
