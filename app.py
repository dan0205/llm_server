from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# 환경변수 로드
load_dotenv()

# Flask 설정
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DB 연결
db = SQLAlchemy(app)

# 테이블 모델
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
with app.app_context():
    db.create_all()

# 라우트
@app.route("/")
def index():
    try:
        user = User.query.first()
        return f"Hello, {user.name if user else 'World'}!"
    except Exception as e:
        return f"<h1>DB 연결 오류</h1><pre>{str(e)}</pre>", 500

# 앱 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

