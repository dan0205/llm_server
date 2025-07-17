from flask import Flask
import redis

app = Flask(__name__)

# Redis 연결 (Docker에서 실행 중인 redis-container와 연결)
r = redis.Redis(host='localhost', port=6379, db=0)

@app.route('/')
def index():
    r.set('greeting', 'Hello from Redis!')
    greeting = r.get('greeting').decode('utf-8')
    return f'<h1>{greeting}</h1>'

if __name__ == '__main__':
    app.run(debug=True)
